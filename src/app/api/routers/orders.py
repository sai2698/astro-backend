import razorpay
import hmac
import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.core.config import settings
from app.models.course import Course
from app.models.enrollment import Order as OrderModel, Enrollment as EnrollmentModel
from app.models.user import User
from app.schemas.enrollment import OrderCreate, OrderVerify, Order, Enrollment
from app.api import deps

router = APIRouter()

# Initialize Razorpay client
rzp_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@router.post("/", response_model=Order)
async def create_order(
    order_in: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    if not current_user.phone:
        raise HTTPException(status_code=400, detail="Please add your mobile number in your profile before enrolling.")
        
    # Fetch course
    result = await db.execute(select(Course).filter(Course.id == order_in.course_id))
    course = result.scalars().first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    price = course.discount_price if course.discount_price is not None else course.price
    
    if price == 0:
        # Check if already enrolled
        enroll_check = await db.execute(select(EnrollmentModel).filter(
            EnrollmentModel.user_id == current_user.id,
            EnrollmentModel.course_id == course.id
        ))
        if enroll_check.scalars().first():
            raise HTTPException(status_code=400, detail="Already enrolled in this course")
            
        # Free course, direct enrollment
        db_enrollment = EnrollmentModel(user_id=current_user.id, course_id=course.id, is_active=False, status="pending")
        db.add(db_enrollment)
        
        db_order = OrderModel(user_id=current_user.id, course_id=course.id, amount=0, status="paid")
        db.add(db_order)
        
        await db.commit()
        await db.refresh(db_order)
        return db_order
        
    # Paid course, generate Razorpay order
    amount_in_paise = int(price * 100)
    
    if settings.RAZORPAY_KEY_ID == "test_key_id":
        # Mock Razorpay for test environment
        rzp_order_id = f"mock_order_{course.id}_{current_user.id}"
    else:
        rzp_order = rzp_client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": f"receipt_course_{course.id}_user_{current_user.id}"
        })
        rzp_order_id = rzp_order['id']
    
    db_order = OrderModel(
        user_id=current_user.id,
        course_id=course.id,
        amount=price,
        razorpay_order_id=rzp_order_id,
        status="created"
    )
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    
    return db_order

@router.post("/verify")
async def verify_payment(
    verify_in: OrderVerify,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    # Verify signature
    if settings.RAZORPAY_KEY_ID != "test_key_id":
        try:
            rzp_client.utility.verify_payment_signature({
                'razorpay_order_id': verify_in.razorpay_order_id,
                'razorpay_payment_id': verify_in.razorpay_payment_id,
                'razorpay_signature': verify_in.razorpay_signature
            })
        except razorpay.errors.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid payment signature")
        
    # Find order
    result = await db.execute(select(OrderModel).filter(OrderModel.razorpay_order_id == verify_in.razorpay_order_id))
    db_order = result.scalars().first()
    
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if db_order.status == "paid":
        return {"message": "Already paid and enrolled"}
        
    # Update order status
    db_order.status = "paid"
    
    # Guard: Check if already enrolled (handles retries / double-payment)
    enroll_check = await db.execute(select(EnrollmentModel).filter(
        EnrollmentModel.user_id == current_user.id,
        EnrollmentModel.course_id == verify_in.course_id
    ))
    if enroll_check.scalars().first():
        await db.commit()
        return {"message": "Payment verified and already enrolled"}
        
    # Create enrollment
    db_enrollment = EnrollmentModel(user_id=current_user.id, course_id=verify_in.course_id, is_active=False, status="pending")
    db.add(db_enrollment)
    
    await db.commit()
    
    # TODO in Phase 8: Send confirmation email via Celery
    
    return {"message": "Payment verified and enrolled successfully"}
