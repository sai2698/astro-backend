import uuid
import razorpay
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload
from typing import List

from app.core.database import get_db
from app.core.config import settings
from app.models.appointment import Appointment as AppointmentModel, AstrologerAvailability, ServiceType, AstrologerProfile, PurohitaSeva, AstrologerService
from app.models.user import User
from app.schemas.appointment import Appointment as AppointmentSchema, AppointmentCreate, AppointmentVerifyPayment
from app.api import deps

router = APIRouter()

rzp_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@router.post("/create-order", response_model=AppointmentSchema)
async def book_appointment(
    booking_in: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    if not current_user.phone:
        raise HTTPException(status_code=400, detail="Please add your mobile number in your profile before booking an appointment.")
        
    # Lock the availability slot to prevent double booking
    query = select(AstrologerAvailability).filter(
        AstrologerAvailability.id == booking_in.availability_id,
        AstrologerAvailability.astrologer_id == booking_in.astrologer_id,
        AstrologerAvailability.is_booked == False
    ).with_for_update() # Row-level lock
    
    result = await db.execute(query)
    availability = result.scalars().first()
    
    if not availability:
        raise HTTPException(status_code=400, detail="Slot is not available")
        
    availability.is_booked = True
    
    # Calculate price
    astro_query = select(AstrologerProfile).filter(AstrologerProfile.user_id == booking_in.astrologer_id)
    astro_result = await db.execute(astro_query)
    astrologer = astro_result.scalars().first()
    
    price = 0.0
    if booking_in.service_id:
        service_query = select(ServiceType).filter(ServiceType.id == booking_in.service_id)
        service_result = await db.execute(service_query)
        service = service_result.scalars().first()
        price = service.base_price if service else 0.0
    elif booking_in.selected_seva:
        seva_query = select(PurohitaSeva).filter(
            PurohitaSeva.purohita_id == booking_in.astrologer_id,
            PurohitaSeva.name == booking_in.selected_seva
        )
        seva_result = await db.execute(seva_query)
        seva = seva_result.scalars().first()
        price = seva.price if seva else (astrologer.price_per_session if astrologer else 0.0)
    elif booking_in.selected_service:
        astro_service_query = select(AstrologerService).filter(
            AstrologerService.astrologer_id == booking_in.astrologer_id,
            AstrologerService.name == booking_in.selected_service
        )
        astro_service_result = await db.execute(astro_service_query)
        astro_service = astro_service_result.scalars().first()
        price = astro_service.price if astro_service else (astrologer.price_per_session if astrologer else 0.0)
    else:
        price = astrologer.price_per_session if astrologer else 0.0

    # Create Razorpay order
    amount_in_paise = int(price * 100)
    if settings.RAZORPAY_KEY_ID == "test_key_id" or settings.RAZORPAY_KEY_ID.startswith("test_key"):
        rzp_order_id = f"mock_order_{booking_in.astrologer_id}_{current_user.id}"
    else:
        rzp_order = rzp_client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": f"receipt_appt_{booking_in.astrologer_id}_{current_user.id}"
        })
        rzp_order_id = rzp_order['id']
    
    # Generate mock Google Meet link
    meet_code = f"{uuid.uuid4().hex[:3]}-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:3]}"
    google_meet_link = f"https://meet.google.com/{meet_code}"
    
    appointment = AppointmentModel(
        user_id=current_user.id,
        astrologer_id=booking_in.astrologer_id,
        service_id=booking_in.service_id,
        availability_id=booking_in.availability_id,
        scheduled_date=availability.specific_date,
        scheduled_start_time=availability.start_time,
        status="payment_pending",
        google_meet_link=google_meet_link,
        selected_seva=booking_in.selected_seva,
        selected_service=booking_in.selected_service,
        razorpay_order_id=rzp_order_id,
        amount=price
    )
    
    db.add(appointment)
    await db.commit()
    
    # Reload with relationships to avoid MissingGreenlet error during serialization
    stmt = select(AppointmentModel).options(
        joinedload(AppointmentModel.service),
        selectinload(AppointmentModel.files)
    ).filter(AppointmentModel.id == appointment.id)
    
    result = await db.execute(stmt)
    appointment_loaded = result.scalars().first()
    
    if appointment_loaded and appointment_loaded.service:
        appointment_loaded.service_name = appointment_loaded.service.name
    
    return appointment_loaded

@router.post("/verify-payment")
async def verify_payment(
    verify_in: AppointmentVerifyPayment,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    if not (settings.RAZORPAY_KEY_ID == "test_key_id" or settings.RAZORPAY_KEY_ID.startswith("test_key")):
        try:
            rzp_client.utility.verify_payment_signature({
                'razorpay_order_id': verify_in.razorpay_order_id,
                'razorpay_payment_id': verify_in.razorpay_payment_id,
                'razorpay_signature': verify_in.razorpay_signature
            })
        except razorpay.errors.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid payment signature")
            
    query = select(AppointmentModel).filter(
        AppointmentModel.id == verify_in.appointment_id,
        AppointmentModel.user_id == current_user.id
    )
    result = await db.execute(query)
    appointment = result.scalars().first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
        
    if appointment.status == "pending":
        return {"message": "Already paid and scheduled"}
        
    appointment.status = "pending"
    await db.commit()
    
    return {"message": "Payment verified and appointment scheduled"}

@router.get("/me", response_model=List[AppointmentSchema])
async def my_appointments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    query = select(AppointmentModel).options(
        joinedload(AppointmentModel.service),
        selectinload(AppointmentModel.files)
    ).filter(AppointmentModel.user_id == current_user.id)
    
    result = await db.execute(query)
    appointments = result.scalars().all()
    
    # Needs to get astrologer name and service name
    # For now we'll just populate service_name from joined load
    for appt in appointments:
        if appt.service:
            appt.service_name = appt.service.name
            
    return appointments

@router.post("/cancel/{appointment_id}")
async def cancel_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    query = select(AppointmentModel).filter(
        AppointmentModel.id == appointment_id,
        AppointmentModel.user_id == current_user.id,
        AppointmentModel.status == "pending"
    )
    result = await db.execute(query)
    appointment = result.scalars().first()
    
    if not appointment:
        raise HTTPException(status_code=400, detail="Cannot cancel this appointment")
        
    appointment.status = "cancelled"
    
    # Free up the availability slot
    avail_query = select(AstrologerAvailability).filter(AstrologerAvailability.id == appointment.availability_id)
    avail_result = await db.execute(avail_query)
    availability = avail_result.scalars().first()
    if availability:
        availability.is_booked = False
        
    await db.commit()
    return {"message": "Appointment cancelled successfully"}
