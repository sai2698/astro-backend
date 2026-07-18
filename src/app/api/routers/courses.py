from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import or_
from typing import List, Optional

from app.core.database import get_db
from app.models.course import Course as CourseModel, CourseReview as ReviewModel, Wishlist as WishlistModel
from app.models.enrollment import Enrollment
from app.models.user import User
from app.schemas.course import Course, CourseCreate, CourseUpdate, CourseDetail, CourseReview, CourseReviewCreate
from app.api import deps

router = APIRouter()

# Placeholder for Cloud Storage Signed URL generator
def generate_signed_url(video_url: str) -> str:
    if not video_url:
        return ""
    if video_url.startswith("http://"):
        video_url = video_url.replace("http://", "https://")
    return f"{video_url}?sig=mock_signature&expires=mock_expiry"

@router.get("/", response_model=List[Course])
async def list_courses(
    db: AsyncSession = Depends(get_db),
    category_id: Optional[int] = None,
    level: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[User] = Depends(deps.get_current_user_optional)
):
    query = select(CourseModel).filter(CourseModel.is_published == True)
    
    if category_id:
        query = query.filter(CourseModel.category_id == category_id)
    if level:
        query = query.filter(CourseModel.level == level)
    if search:
        query = query.filter(CourseModel.title.ilike(f"%{search}%"))
        
    result = await db.execute(query.offset(skip).limit(limit))
    courses = result.scalars().all()
    
    if current_user:
        enroll_query = select(Enrollment.course_id, Enrollment.status).filter(
            Enrollment.user_id == current_user.id, 
            or_(Enrollment.is_active == True, Enrollment.status == "pending")
        )
        enroll_res = await db.execute(enroll_query)
        enrolled_courses = enroll_res.all()
        enrollment_map = {row.course_id: row.status for row in enrolled_courses}
        for c in courses:
            setattr(c, "is_enrolled", c.id in enrollment_map)
            setattr(c, "enrollment_status", enrollment_map.get(c.id))
    else:
        for c in courses:
            setattr(c, "is_enrolled", False)
            setattr(c, "enrollment_status", None)
            
    return courses

@router.get("/{course_id}", response_model=CourseDetail)
async def get_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(deps.get_current_user_optional)
):
    query = select(CourseModel).options(
        selectinload(CourseModel.sections).selectinload(CourseModel.sections.property.mapper.class_.lectures)
    ).filter(CourseModel.id == course_id)
    
    result = await db.execute(query)
    course = result.scalars().first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    is_enrolled = False 
    is_fully_active = False
    enrollment_status = None
    lecture_progresses = {}
    if current_user:
        enroll_query = select(Enrollment).filter(
            Enrollment.user_id == current_user.id,
            Enrollment.course_id == course_id
        )
        enroll_res = await db.execute(enroll_query)
        enrollment = enroll_res.scalars().first()
        if enrollment:
            if enrollment.is_active or enrollment.status == "pending":
                is_enrolled = True
            if enrollment.is_active:
                is_fully_active = True
            enrollment_status = enrollment.status
            
        from app.models.enrollment import LectureProgress
        lp_query = select(LectureProgress).filter(
            LectureProgress.user_id == current_user.id,
            LectureProgress.course_id == course_id
        )
        lp_res = await db.execute(lp_query)
        for lp in lp_res.scalars().all():
            lecture_progresses[lp.lecture_id] = lp.progress_percent

    # Process signed URLs and progress
    for section in course.sections:
        for lecture in section.lectures:
            lecture.progress_percent = lecture_progresses.get(lecture.id, 0)
            if lecture.is_preview or is_fully_active:
                lecture.video_url = generate_signed_url(lecture.video_url)
            else:
                lecture.video_url = None # Lock it

    setattr(course, "is_enrolled", is_enrolled)
    setattr(course, "enrollment_status", enrollment_status)
    return course

@router.post("/", response_model=Course)
async def create_course(
    course_in: CourseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.require_role("instructor")) # Or admin
):
    course_data = course_in.model_dump()
    db_course = CourseModel(**course_data, instructor_id=current_user.id)
    db.add(db_course)
    await db.commit()
    await db.refresh(db_course)
    return db_course

@router.patch("/{course_id}", response_model=Course)
async def update_course(
    course_id: int,
    course_in: CourseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.require_role("instructor"))
):
    result = await db.execute(select(CourseModel).filter(CourseModel.id == course_id))
    db_course = result.scalars().first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    if db_course.instructor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to edit this course")
        
    update_data = course_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_course, field, value)
        
    await db.commit()
    await db.refresh(db_course)
    return db_course

@router.delete("/{course_id}")
async def delete_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.require_role("admin"))
):
    result = await db.execute(select(CourseModel).filter(CourseModel.id == course_id))
    db_course = result.scalars().first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    await db.delete(db_course)
    await db.commit()
    return {"message": "Course deleted successfully"}

@router.post("/{course_id}/reviews", response_model=CourseReview)
async def create_review(
    course_id: int,
    review_in: CourseReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    db_review = ReviewModel(**review_in.model_dump(), course_id=course_id, user_id=current_user.id)
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    return db_review

@router.post("/{course_id}/wishlist")
async def add_to_wishlist(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    db_wishlist = WishlistModel(user_id=current_user.id, course_id=course_id)
    db.add(db_wishlist)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Already in wishlist")
    return {"message": "Added to wishlist"}

@router.delete("/{course_id}/wishlist")
async def remove_from_wishlist(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    result = await db.execute(select(WishlistModel).filter(
        WishlistModel.user_id == current_user.id,
        WishlistModel.course_id == course_id
    ))
    db_wishlist = result.scalars().first()
    if not db_wishlist:
        raise HTTPException(status_code=404, detail="Not in wishlist")
        
    await db.delete(db_wishlist)
    await db.commit()
    return {"message": "Removed from wishlist"}
