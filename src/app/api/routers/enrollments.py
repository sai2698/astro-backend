from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import func
from sqlalchemy import or_
from typing import List

from app.core.database import get_db
from app.models.enrollment import Enrollment as EnrollmentModel
from app.models.user import User
from app.schemas.enrollment import Enrollment, EnrollmentProgressUpdate
from app.api import deps

router = APIRouter()

@router.patch("/me/lectures/{lecture_id}/progress", response_model=Enrollment)
async def update_progress(
    lecture_id: int,
    progress_in: EnrollmentProgressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    from app.models.course import Lecture, CourseSection
    from app.models.enrollment import LectureProgress
    
    # 1. Verify the lecture exists and get its course_id
    lecture_query = select(Lecture).options(joinedload(Lecture.section)).filter(Lecture.id == lecture_id)
    lecture = (await db.execute(lecture_query)).scalars().first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
        
    course_id = lecture.section.course_id
    
    # 2. Verify the user is enrolled in this course and it is active
    enrollment_query = select(EnrollmentModel).filter(
        EnrollmentModel.user_id == current_user.id,
        EnrollmentModel.course_id == course_id,
        EnrollmentModel.is_active == True
    )
    enrollment = (await db.execute(enrollment_query)).scalars().first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    # 3. Update or create the LectureProgress
    lp_query = select(LectureProgress).filter(
        LectureProgress.user_id == current_user.id,
        LectureProgress.lecture_id == lecture_id
    )
    lecture_progress = (await db.execute(lp_query)).scalars().first()
    
    if not lecture_progress:
        lecture_progress = LectureProgress(
            user_id=current_user.id,
            lecture_id=lecture_id,
            course_id=course_id,
            progress_percent=progress_in.progress_percent
        )
        db.add(lecture_progress)
    else:
        if progress_in.progress_percent > lecture_progress.progress_percent:
            lecture_progress.progress_percent = progress_in.progress_percent
            
    await db.flush() # ensure lecture_progress is in DB to aggregate
    
    # 4. Calculate total course progress
    # Get all lectures for this course
    total_lectures_query = select(func.count(Lecture.id)).join(CourseSection).filter(CourseSection.course_id == course_id)
    total_lectures = (await db.execute(total_lectures_query)).scalar() or 1
    
    # Get sum of all progress_percent for this user and course
    sum_progress_query = select(func.sum(LectureProgress.progress_percent)).filter(
        LectureProgress.user_id == current_user.id,
        LectureProgress.course_id == course_id
    )
    sum_progress = (await db.execute(sum_progress_query)).scalar() or 0
    
    new_course_progress = int(sum_progress / total_lectures)
    enrollment.progress_percent = new_course_progress
        
    await db.commit()
    await db.refresh(enrollment)
        
    return enrollment

@router.get("/me", response_model=List[Enrollment])
async def get_my_enrollments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    query = select(EnrollmentModel).options(joinedload(EnrollmentModel.course)).filter(
        EnrollmentModel.user_id == current_user.id,
        or_(EnrollmentModel.is_active == True, EnrollmentModel.status == "pending")
    )
    result = await db.execute(query)
    enrollments = result.scalars().all()
    
    for enrollment in enrollments:
        if enrollment.course:
            enrollment.course_title = enrollment.course.title
            
    return enrollments

@router.post("/cancel/{course_id}")
async def cancel_enrollment(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    query = select(EnrollmentModel).filter(
        EnrollmentModel.user_id == current_user.id,
        EnrollmentModel.course_id == course_id,
        EnrollmentModel.status == "pending"
    )
    result = await db.execute(query)
    enrollment = result.scalars().first()
    
    if not enrollment:
        raise HTTPException(status_code=400, detail="Cannot cancel this enrollment")
        
    await db.delete(enrollment)
    await db.commit()
    return {"message": "Enrollment cancelled successfully"}
