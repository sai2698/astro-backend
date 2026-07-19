from fastapi import APIRouter, Request, Depends, Form, HTTPException, status, UploadFile, File
import shutil
import pathlib
from typing import Optional
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.orm import selectinload
import os

from app.core.database import get_db
from app.core.security import create_access_token
from app.models.user import User
from app.models.course import Course, CourseSection, Lecture
from app.models.enrollment import Enrollment, LectureProgress
from app.models.appointment import Appointment, ServiceType, AstrologerAvailability, AstrologerProfile, ConsultationFile, ExpertCalendarDay
from app.api.routers.utils import ensure_upcoming_3_days_generated
from app.api.deps import get_admin_user_cookie
from app.core.security import verify_password
from app.core.config import settings
from datetime import timedelta, date, time, datetime

router = APIRouter()

async def cleanup_expired_slots(db: AsyncSession):
    # Delete slots in the past that are not booked
    # We use a raw query or fetch and delete. For sqlite/postgres cross compatibility:
    result = await db.execute(select(AstrologerAvailability).filter(AstrologerAvailability.is_booked == False))
    slots = result.scalars().all()
    now = datetime.now()
    for slot in slots:
        try:
            slot_dt = datetime.combine(slot.specific_date, slot.start_time)
            if slot_dt < now:
                await db.delete(slot)
        except Exception:
            pass
    await db.commit()

# Setup templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates", "admin"))

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login_post(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()
    if not user or not verify_password(password, user.password_hash) or user.role != "admin":
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid admin credentials"})
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="admin_access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return response

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("admin_access_token")
    return response

@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    # Stats
    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
    total_courses = (await db.execute(select(func.count(Course.id)))).scalar() or 0
    total_enrollments = (await db.execute(select(func.count(Enrollment.id)))).scalar() or 0
    total_appointments = (await db.execute(select(func.count(Appointment.id)))).scalar() or 0
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "user": current_user,
        "total_users": total_users,
        "total_courses": total_courses,
        "total_enrollments": total_enrollments,
        "total_appointments": total_appointments
    })

@router.get("/users", response_class=HTMLResponse)
async def view_users(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(select(User).order_by(User.id.desc()))
    users = result.scalars().all()
    return templates.TemplateResponse("users.html", {"request": request, "user": current_user, "users": users})

@router.get("/enrollments", response_class=HTMLResponse)
async def view_enrollments(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(
        select(Enrollment)
        .options(selectinload(Enrollment.user), selectinload(Enrollment.course))
        .order_by(Enrollment.enrolled_at.desc())
    )
    enrollments = result.scalars().all()
    return templates.TemplateResponse("enrollments.html", {"request": request, "user": current_user, "enrollments": enrollments})

@router.post("/enrollments/{enrollment_id}/approve")
async def approve_enrollment(
    enrollment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(select(Enrollment).filter(Enrollment.id == enrollment_id))
    enrollment = result.scalars().first()
    if enrollment:
        enrollment.status = "approved"
        enrollment.is_active = True
        await db.commit()
    return RedirectResponse(url="/admin/enrollments", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/enrollments/{enrollment_id}/toggle_active")
async def toggle_enrollment_active(
    enrollment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(select(Enrollment).filter(Enrollment.id == enrollment_id))
    enrollment = result.scalars().first()
    if enrollment:
        enrollment.is_active = not enrollment.is_active
        if not enrollment.is_active:
            enrollment.status = "expired"
        else:
            enrollment.status = "approved"
        await db.commit()
    return RedirectResponse(url="/admin/enrollments", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/enrollments/{enrollment_id}/delete")
async def delete_enrollment(
    enrollment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(select(Enrollment).filter(Enrollment.id == enrollment_id))
    enrollment = result.scalars().first()
    if enrollment:
        await db.delete(enrollment)
        await db.commit()
    return RedirectResponse(url="/admin/enrollments", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/courses", response_class=HTMLResponse)
async def view_courses(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(select(Course).order_by(Course.id.asc()))
    courses = result.scalars().all()
    return templates.TemplateResponse("courses.html", {"request": request, "user": current_user, "courses": courses})

@router.post("/courses/create")
async def create_course(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    price: float = Form(0.0),
    discount_price: float = Form(None),
    thumbnail_url: str = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    new_course = Course(
        title=title,
        description=description,
        price=price,
        discount_price=discount_price,
        thumbnail_url=thumbnail_url,
        instructor_id=current_user.id
    )
    db.add(new_course)
    await db.commit()
    return RedirectResponse(url="/admin/courses", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/courses/edit/{course_id}", response_class=HTMLResponse)
async def edit_course_page(
    course_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(
        select(Course)
        .options(selectinload(Course.sections).selectinload(CourseSection.lectures))
        .filter(Course.id == course_id)
    )
    course = result.scalars().first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    # Sort sections and lectures by order_index
    course.sections.sort(key=lambda s: s.order_index)
    for section in course.sections:
        section.lectures.sort(key=lambda l: l.order_index)
        
    return templates.TemplateResponse("course_edit.html", {"request": request, "user": current_user, "course": course})

@router.post("/courses/edit/{course_id}")
async def edit_course_post(
    course_id: int,
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    price: float = Form(0.0),
    discount_price: float = Form(None),
    thumbnail_url: str = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(select(Course).filter(Course.id == course_id))
    course = result.scalars().first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    course.title = title
    course.description = description
    course.price = price
    course.discount_price = discount_price
    course.thumbnail_url = thumbnail_url
    
    await db.commit()
    return RedirectResponse(url="/admin/courses", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/courses/delete/{course_id}")
async def delete_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(select(Course).filter(Course.id == course_id))
    course = result.scalars().first()
    if course:
        await db.delete(course)
        await db.commit()
    return RedirectResponse(url="/admin/courses", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/courses/{course_id}/sections/add")
async def add_course_section(
    course_id: int,
    title: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    # Find max order index
    result = await db.execute(select(func.max(CourseSection.order_index)).filter(CourseSection.course_id == course_id))
    max_order = result.scalar() or 0
    
    new_section = CourseSection(
        course_id=course_id,
        title=title,
        order_index=max_order + 1
    )
    db.add(new_section)
    await db.commit()
    return RedirectResponse(url=f"/admin/courses/edit/{course_id}", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/sections/delete/{section_id}")
async def delete_course_section(
    section_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(select(CourseSection).filter(CourseSection.id == section_id))
    section = result.scalars().first()
    if section:
        course_id = section.course_id
        await db.delete(section)
        await db.commit()
        return RedirectResponse(url=f"/admin/courses/edit/{course_id}", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/admin/courses", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/sections/{section_id}/lectures/add")
async def add_lecture(
    section_id: int,
    title: str = Form(...),
    video_url: str = Form(...),
    duration_seconds: int = Form(0),
    is_preview: bool = Form(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(select(CourseSection).filter(CourseSection.id == section_id))
    section = result.scalars().first()
    if not section:
        return RedirectResponse(url="/admin/courses", status_code=status.HTTP_303_SEE_OTHER)

    result_max = await db.execute(select(func.max(Lecture.order_index)).filter(Lecture.section_id == section_id))
    max_order = result_max.scalar() or 0

    new_lecture = Lecture(
        section_id=section_id,
        title=title,
        video_url=video_url,
        duration_seconds=duration_seconds,
        order_index=max_order + 1,
        is_preview=is_preview
    )
    db.add(new_lecture)
    await db.commit()
    return RedirectResponse(url=f"/admin/courses/edit/{section.course_id}", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/lectures/edit/{lecture_id}", response_class=HTMLResponse)
async def edit_lecture_page(
    lecture_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(select(Lecture).options(selectinload(Lecture.section)).filter(Lecture.id == lecture_id))
    lecture = result.scalars().first()
    if not lecture:
        return RedirectResponse(url="/admin/courses", status_code=status.HTTP_303_SEE_OTHER)
        
    return templates.TemplateResponse(
        "lecture_edit.html", 
        {"request": request, "user": current_user, "lecture": lecture, "course_id": lecture.section.course_id}
    )

@router.post("/lectures/edit/{lecture_id}")
async def edit_lecture_post(
    lecture_id: int,
    request: Request,
    title: str = Form(...),
    video_url: str = Form(...),
    duration_seconds: int = Form(0),
    is_preview: bool = Form(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(select(Lecture).options(selectinload(Lecture.section)).filter(Lecture.id == lecture_id))
    lecture = result.scalars().first()
    if not lecture:
        return RedirectResponse(url="/admin/courses", status_code=status.HTTP_303_SEE_OTHER)
        
    lecture.title = title
    lecture.video_url = video_url
    lecture.duration_seconds = duration_seconds
    lecture.is_preview = is_preview
    
    course_id = lecture.section.course_id
    await db.commit()
    
    return RedirectResponse(url=f"/admin/courses/edit/{course_id}", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/lectures/delete/{lecture_id}")
async def delete_lecture(
    lecture_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(select(Lecture).options(selectinload(Lecture.section)).filter(Lecture.id == lecture_id))
    lecture = result.scalars().first()
    if lecture:
        course_id = lecture.section.course_id
        await db.delete(lecture)
        await db.commit()
        return RedirectResponse(url=f"/admin/courses/edit/{course_id}", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/admin/courses", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/appointments", response_class=HTMLResponse)
async def view_appointments(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(
        select(Appointment)
        .options(selectinload(Appointment.user), selectinload(Appointment.service), selectinload(Appointment.files))
        .order_by(Appointment.scheduled_date.asc(), Appointment.scheduled_start_time.asc())
    )
    appointments = result.scalars().all()
    return templates.TemplateResponse("appointments.html", {"request": request, "user": current_user, "appointments": appointments})

@router.post("/appointments/{appointment_id}/complete")
async def complete_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(select(Appointment).filter(Appointment.id == appointment_id))
    appointment = result.scalars().first()
    if appointment and appointment.status == 'scheduled':
        appointment.status = 'completed'
        await db.commit()
    return RedirectResponse(url=f"/admin/appointments?open_attachments={appointment_id}", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/appointments/{appointment_id}/accept")
async def accept_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(select(Appointment).filter(Appointment.id == appointment_id))
    appointment = result.scalars().first()
    if appointment and appointment.status == 'pending':
        appointment.status = 'scheduled'
        await db.commit()
    return RedirectResponse(url="/admin/appointments", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/appointments/{appointment_id}/add_file")
async def add_appointment_file(
    appointment_id: int,
    name: str = Form(...),
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(select(Appointment).filter(Appointment.id == appointment_id))
    appointment = result.scalars().first()
    if appointment and appointment.status == 'completed':
        if file and file.filename:
            import uuid
            ext = file.filename.split('.')[-1] if '.' in file.filename else 'bin'
            filename = f"report_{appointment_id}_{uuid.uuid4().hex[:8]}.{ext}"
            
            # Navigate up from backend/app/api/routers/admin_web.py to backend/static
            static_dir = pathlib.Path(__file__).parent.parent.parent.parent / "static"
            uploads_dir = static_dir / "uploads"
            uploads_dir.mkdir(parents=True, exist_ok=True)
            filepath = uploads_dir / filename
            
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
            new_file = ConsultationFile(
                appointment_id=appointment_id,
                name=name,
                file_url=f"/static/uploads/{filename}",
                is_external=False
            )
            db.add(new_file)
            
        elif url:
            new_file = ConsultationFile(
                appointment_id=appointment_id,
                name=name,
                file_url=url,
                is_external=True
            )
            db.add(new_file)
            
        await db.commit()
        
    return RedirectResponse(url=f"/admin/appointments?open_attachments={appointment_id}", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/appointments/files/{file_id}/delete")
async def delete_appointment_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(select(ConsultationFile).filter(ConsultationFile.id == file_id))
    file_record = result.scalars().first()
    if file_record:
        if not file_record.is_external:
            try:
                static_dir = pathlib.Path(__file__).parent.parent.parent.parent / "static"
                filename = file_record.file_url.replace('/static/uploads/', '')
                filepath = static_dir / "uploads" / filename
                if filepath.exists():
                    filepath.unlink()
            except Exception as e:
                print(f"Error deleting file: {e}")
                
        appointment_id = file_record.appointment_id
        await db.delete(file_record)
        await db.commit()
        return RedirectResponse(url=f"/admin/appointments?open_attachments={appointment_id}", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/admin/appointments", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/appointments/{appointment_id}/delete")
async def delete_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(select(Appointment).filter(Appointment.id == appointment_id))
    appointment = result.scalars().first()
    if appointment:
        # Robustly free up the slot so others can book it
        avail_result = await db.execute(select(AstrologerAvailability).filter(AstrologerAvailability.id == appointment.availability_id))
        availability = avail_result.scalars().first()
        if availability:
            availability.is_booked = False
            
        await db.delete(appointment)
        await db.commit()
    return RedirectResponse(url="/admin/appointments", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/services", response_class=HTMLResponse)
async def view_services(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(select(ServiceType).order_by(ServiceType.id.desc()))
    services = result.scalars().all()
    return templates.TemplateResponse("services.html", {"request": request, "user": current_user, "services": services})

@router.post("/services/create")
async def create_service(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    duration_minutes: int = Form(30),
    base_price: float = Form(0.0),
    category: str = Form("consultation"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    new_service = ServiceType(
        name=name,
        description=description,
        duration_minutes=duration_minutes,
        base_price=base_price,
        category=category
    )
    db.add(new_service)
    await db.commit()
    return RedirectResponse(url="/admin/services", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/services/edit/{service_id}", response_class=HTMLResponse)
async def edit_service_page(
    service_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(select(ServiceType).filter(ServiceType.id == service_id))
    service = result.scalars().first()
    if not service:
        return RedirectResponse(url="/admin/services", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("service_edit.html", {"request": request, "user": current_user, "service": service})

@router.post("/services/edit/{service_id}")
async def edit_service_post(
    service_id: int,
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    duration_minutes: int = Form(30),
    base_price: float = Form(0.0),
    category: str = Form("consultation"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(select(ServiceType).filter(ServiceType.id == service_id))
    service = result.scalars().first()
    if not service:
        return RedirectResponse(url="/admin/services", status_code=status.HTTP_303_SEE_OTHER)
        
    service.name = name
    service.description = description
    service.duration_minutes = duration_minutes
    service.base_price = base_price
    service.category = category
    
    await db.commit()
    return RedirectResponse(url="/admin/services", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/services/delete/{service_id}")
async def delete_service(
    service_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(select(ServiceType).filter(ServiceType.id == service_id))
    service = result.scalars().first()
    if service:
        await db.delete(service)
        await db.commit()
    return RedirectResponse(url="/admin/appointments", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/astrologers", response_class=HTMLResponse)
async def view_astrologers(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    astrologers_result = await db.execute(select(AstrologerProfile).options(selectinload(AstrologerProfile.user), selectinload(AstrologerProfile.astrologer_services)).filter(AstrologerProfile.profile_type == 'astrologer'))
    astrologers = astrologers_result.scalars().all()
    
    # Get users who don't have an astrologer profile yet to show in the create dropdown
    existing_astro_ids = [a.user_id for a in astrologers]
    if existing_astro_ids:
        users_result = await db.execute(select(User).filter(User.id.not_in(existing_astro_ids)))
    else:
        users_result = await db.execute(select(User))
    eligible_users = users_result.scalars().all()
    
    return templates.TemplateResponse("astrologers.html", {
        "request": request, 
        "user": current_user, 
        "astrologers": astrologers,
        "eligible_users": eligible_users
    })

@router.post("/astrologers/create")
async def create_astrologer(
    request: Request,
    user_id: int = Form(...),
    bio: str = Form(""),
    experience_years: int = Form(0),
    price_per_session: float = Form(0.0),
    profile_type: str = Form("astrologer"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    form_data = await request.form()
    service_names = form_data.getlist("service_names[]")
    service_durations = form_data.getlist("service_durations[]")
    service_prices = form_data.getlist("service_prices[]")

    new_profile = AstrologerProfile(
        user_id=user_id,
        bio=bio,
        experience_years=experience_years,
        price_per_session=price_per_session,
        profile_type=profile_type,
        rating_avg=0.0,
        is_available=True
    )
    db.add(new_profile)
    await db.flush()

    from app.models.appointment import AstrologerService
    for i in range(len(service_names)):
        name = service_names[i].strip()
        if name:
            dur_str = service_durations[i] if i < len(service_durations) else "30"
            price_str = service_prices[i] if i < len(service_prices) else "0"
            try:
                dur = int(dur_str)
            except ValueError:
                dur = 30
            try:
                price = float(price_str)
            except ValueError:
                price = 0.0
            db.add(AstrologerService(astrologer_id=user_id, name=name, duration_minutes=dur, price=price))

    await db.commit()
    return RedirectResponse(url="/admin/astrologers", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/astrologers/{astrologer_id}/edit")
async def edit_astrologer(
    astrologer_id: int,
    request: Request,
    name: str = Form(...),
    bio: str = Form(None),
    experience_years: int = Form(0),
    price_per_session: float = Form(0.0),
    rating_avg: float = Form(0.0),
    is_available: bool = Form(False),
    profile_type: str = Form("astrologer"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    form_data = await request.form()
    service_names = form_data.getlist("service_names[]")
    service_durations = form_data.getlist("service_durations[]")
    service_prices = form_data.getlist("service_prices[]")

    result = await db.execute(select(AstrologerProfile).options(selectinload(AstrologerProfile.user)).filter(AstrologerProfile.user_id == astrologer_id))
    astrologer = result.scalars().first()
    if astrologer:
        if astrologer.user:
            astrologer.user.name = name
        astrologer.bio = bio
        astrologer.experience_years = experience_years
        astrologer.price_per_session = price_per_session
        astrologer.rating_avg = rating_avg
        astrologer.is_available = is_available
        astrologer.profile_type = profile_type
        
        from app.models.appointment import AstrologerService
        # Delete old services
        await db.execute(AstrologerService.__table__.delete().where(AstrologerService.astrologer_id == astrologer_id))
        
        # Add new services
        for i in range(len(service_names)):
            svc_name = service_names[i].strip()
            if svc_name:
                dur_str = service_durations[i] if i < len(service_durations) else "30"
                price_str = service_prices[i] if i < len(service_prices) else "0"
                try:
                    dur = int(dur_str)
                except ValueError:
                    dur = 30
                try:
                    price = float(price_str)
                except ValueError:
                    price = 0.0
                db.add(AstrologerService(astrologer_id=astrologer_id, name=svc_name, duration_minutes=dur, price=price))

        await db.commit()
    return RedirectResponse(url="/admin/astrologers", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/purohits", response_class=HTMLResponse)
async def view_purohits(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    purohits_result = await db.execute(select(AstrologerProfile).options(selectinload(AstrologerProfile.user), selectinload(AstrologerProfile.purohita_sevas)).filter(AstrologerProfile.profile_type == 'purohit'))
    purohits = purohits_result.scalars().all()
    
    # Get users who don't have an astrologer profile yet to show in the create dropdown
    existing_astro_ids = [a.user_id for a in purohits]
    if existing_astro_ids:
        users_result = await db.execute(select(User).filter(User.id.not_in(existing_astro_ids)))
    else:
        users_result = await db.execute(select(User))
    eligible_users = users_result.scalars().all()
    
    return templates.TemplateResponse("purohits.html", {
        "request": request, 
        "user": current_user, 
        "purohits": purohits,
        "eligible_users": eligible_users
    })

@router.post("/purohits/create")
async def create_purohit(
    request: Request,
    user_id: int = Form(...),
    bio: str = Form(""),
    experience_years: int = Form(0),
    price_per_session: float = Form(0.0),
    profile_type: str = Form("purohit"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    form_data = await request.form()
    seva_names = form_data.getlist("seva_names[]")
    seva_prices = form_data.getlist("seva_prices[]")

    new_profile = AstrologerProfile(
        user_id=user_id,
        bio=bio,
        experience_years=experience_years,
        price_per_session=price_per_session,
        profile_type=profile_type,
        rating_avg=0.0,
        is_available=True
    )
    db.add(new_profile)
    await db.flush() # get user_id in session
    
    from app.models.appointment import PurohitaSeva
    for i in range(len(seva_names)):
        name = seva_names[i].strip()
        if name:
            price_str = seva_prices[i] if i < len(seva_prices) else "0"
            try:
                price = float(price_str)
            except ValueError:
                price = 0.0
            db.add(PurohitaSeva(purohita_id=user_id, name=name, price=price))

    await db.commit()
    return RedirectResponse(url="/admin/purohits", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/purohits/{astrologer_id}/edit")
async def edit_purohit(
    astrologer_id: int,
    request: Request,
    name: str = Form(...),
    bio: str = Form(""),
    experience_years: int = Form(0),
    price_per_session: float = Form(0.0),
    rating_avg: float = Form(0.0),
    is_available: bool = Form(False),
    profile_type: str = Form("purohit"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    form_data = await request.form()
    seva_names = form_data.getlist("seva_names[]")
    seva_prices = form_data.getlist("seva_prices[]")

    query = select(AstrologerProfile).options(selectinload(AstrologerProfile.user)).filter(AstrologerProfile.user_id == astrologer_id)
    result = await db.execute(query)
    purohit = result.scalars().first()
    
    if purohit:
        if purohit.user:
            purohit.user.name = name
        purohit.bio = bio
        purohit.experience_years = experience_years
        purohit.price_per_session = price_per_session
        purohit.rating_avg = rating_avg
        purohit.is_available = is_available
        purohit.profile_type = profile_type
        
        from app.models.appointment import PurohitaSeva
        # Delete old sevas
        await db.execute(PurohitaSeva.__table__.delete().where(PurohitaSeva.purohita_id == astrologer_id))
        
        # Add new sevas
        for i in range(len(seva_names)):
            name = seva_names[i].strip()
            if name:
                price_str = seva_prices[i] if i < len(seva_prices) else "0"
                try:
                    price = float(price_str)
                except ValueError:
                    price = 0.0
                db.add(PurohitaSeva(purohita_id=astrologer_id, name=name, price=price))

        await db.commit()
    return RedirectResponse(url="/admin/purohits", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/availability", response_class=HTMLResponse)
async def view_availability(
    request: Request,
    error: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    await cleanup_expired_slots(db)
    await ensure_upcoming_3_days_generated(db)
    
    astros_result = await db.execute(select(AstrologerProfile).options(selectinload(AstrologerProfile.user)).filter(AstrologerProfile.profile_type == 'astrologer'))
    astrologers = astros_result.scalars().all()
    
    calendar_result = await db.execute(
        select(ExpertCalendarDay)
        .join(AstrologerProfile, ExpertCalendarDay.expert_id == AstrologerProfile.user_id)
        .filter(AstrologerProfile.profile_type == 'astrologer')
        .order_by(ExpertCalendarDay.specific_date.desc())
    )
    calendar_days = calendar_result.scalars().all()
    
    avail_result = await db.execute(
        select(AstrologerAvailability)
        .join(AstrologerProfile, AstrologerAvailability.astrologer_id == AstrologerProfile.user_id)
        .options(selectinload(AstrologerAvailability.astrologer).selectinload(AstrologerProfile.user))
        .filter(AstrologerProfile.profile_type == 'astrologer')
        .order_by(AstrologerAvailability.specific_date.desc(), AstrologerAvailability.start_time.asc())
    )
    availability = avail_result.scalars().all()
    
    return templates.TemplateResponse("availability.html", {
        "request": request, 
        "user": current_user, 
        "astrologers": astrologers,
        "calendar_days": calendar_days,
        "availability": availability,
        "error": error
    })

@router.post("/availability/calendar")
async def set_calendar_day(
    request: Request,
    astrologer_id: int = Form(...),
    specific_date: date = Form(...),
    status: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    # Check if exists
    result = await db.execute(select(ExpertCalendarDay).filter(
        ExpertCalendarDay.expert_id == astrologer_id,
        ExpertCalendarDay.specific_date == specific_date
    ))
    day = result.scalars().first()
    if day:
        day.status = status
    else:
        new_day = ExpertCalendarDay(expert_id=astrologer_id, specific_date=specific_date, status=status)
        db.add(new_day)
        
    # If leave, clear unbooked slots
    if status == 'leave':
        slots_res = await db.execute(select(AstrologerAvailability).filter(
            AstrologerAvailability.astrologer_id == astrologer_id,
            AstrologerAvailability.specific_date == specific_date,
            AstrologerAvailability.is_booked == False
        ))
        for slot in slots_res.scalars().all():
            await db.delete(slot)
            
    await db.commit()
    # Redirect based on astrologer type to keep them on the right page
    astro_res = await db.execute(select(AstrologerProfile).filter(AstrologerProfile.user_id == astrologer_id))
    astro = astro_res.scalars().first()
    if astro and astro.profile_type == 'purohit':
        return RedirectResponse(url="/admin/purohits_availability", status_code=303)
    return RedirectResponse(url="/admin/availability", status_code=303)

@router.post("/availability/calendar/delete/{day_id}")
async def delete_calendar_day(
    day_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(select(ExpertCalendarDay).filter(ExpertCalendarDay.id == day_id))
    day = result.scalars().first()
    if day:
        # Before deleting, check profile type so we can redirect correctly
        astro_res = await db.execute(select(AstrologerProfile).filter(AstrologerProfile.user_id == day.expert_id))
        astro = astro_res.scalars().first()
        is_purohit = astro and astro.profile_type == 'purohit'
        
        # We also delete all unbooked slots for that date because we are resetting the day.
        # The auto-generator will recreate standard slots if the date is within the next 3 days.
        slots_res = await db.execute(select(AstrologerAvailability).filter(
            AstrologerAvailability.astrologer_id == day.expert_id,
            AstrologerAvailability.specific_date == day.specific_date,
            AstrologerAvailability.is_booked == False
        ))
        for slot in slots_res.scalars().all():
            await db.delete(slot)
            
        await db.delete(day)
        await db.commit()
        
        if is_purohit:
            return RedirectResponse(url="/admin/purohits_availability", status_code=303)
        return RedirectResponse(url="/admin/availability", status_code=303)
        
    return RedirectResponse(url="/admin/availability", status_code=303)

@router.post("/availability/create")
async def create_availability(
    request: Request,
    astrologer_id: int = Form(...),
    specific_date: date = Form(...),
    start_time: time = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    from datetime import datetime
    
    # Calculate end time (+1 hour)
    start_dt = datetime.combine(specific_date, start_time)
    end_dt = start_dt + timedelta(hours=1)
    end_time = end_dt.time()
    
    # Check for overlaps
    overlap_query = select(AstrologerAvailability).filter(
        AstrologerAvailability.astrologer_id == astrologer_id,
        AstrologerAvailability.specific_date == specific_date,
        AstrologerAvailability.start_time < end_time,
        AstrologerAvailability.end_time > start_time
    )
    result = await db.execute(overlap_query)
    if result.scalars().first():
        import urllib.parse
        error_msg = urllib.parse.quote("Time slot overlaps with an existing appointment.")
        return RedirectResponse(url=f"/admin/availability?error={error_msg}", status_code=status.HTTP_303_SEE_OTHER)

    if start_dt < datetime.now():
        import urllib.parse
        error_msg = urllib.parse.quote("Cannot create slots in the past.")
        return RedirectResponse(url=f"/admin/availability?error={error_msg}", status_code=status.HTTP_303_SEE_OTHER)
        
    # Check if calendar day exists and is 'leave'
    cal_res = await db.execute(select(ExpertCalendarDay).filter(
        ExpertCalendarDay.expert_id == astrologer_id,
        ExpertCalendarDay.specific_date == specific_date
    ))
    cal_day = cal_res.scalars().first()
    if cal_day and cal_day.status == 'leave':
        import urllib.parse
        error_msg = urllib.parse.quote("Expert is marked as on Leave on this date. Please change calendar status first.")
        return RedirectResponse(url=f"/admin/availability?error={error_msg}", status_code=status.HTTP_303_SEE_OTHER)

    new_slot = AstrologerAvailability(
        astrologer_id=astrologer_id,
        specific_date=specific_date,
        start_time=start_time,
        end_time=end_time,
        is_booked=False
    )
    db.add(new_slot)
    await db.commit()
    return RedirectResponse(url="/admin/availability", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/availability/delete/{slot_id}")
async def delete_availability(
    slot_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(select(AstrologerAvailability).filter(AstrologerAvailability.id == slot_id))
    slot = result.scalars().first()
    if slot and not slot.is_booked:
        await db.delete(slot)
        await db.commit()
    return RedirectResponse(url="/admin/availability", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/purohits_availability", response_class=HTMLResponse)
async def view_purohits_availability(
    request: Request,
    error: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    await cleanup_expired_slots(db)
    await ensure_upcoming_3_days_generated(db)
    
    purohits_result = await db.execute(select(AstrologerProfile).options(selectinload(AstrologerProfile.user)).filter(AstrologerProfile.profile_type == 'purohit'))
    purohits = purohits_result.scalars().all()
    
    calendar_result = await db.execute(
        select(ExpertCalendarDay)
        .join(AstrologerProfile, ExpertCalendarDay.expert_id == AstrologerProfile.user_id)
        .filter(AstrologerProfile.profile_type == 'purohit')
        .order_by(ExpertCalendarDay.specific_date.desc())
    )
    calendar_days = calendar_result.scalars().all()
    
    avail_result = await db.execute(
        select(AstrologerAvailability)
        .join(AstrologerProfile, AstrologerAvailability.astrologer_id == AstrologerProfile.user_id)
        .options(selectinload(AstrologerAvailability.astrologer).selectinload(AstrologerProfile.user))
        .filter(AstrologerProfile.profile_type == 'purohit')
        .order_by(AstrologerAvailability.specific_date.desc(), AstrologerAvailability.start_time.asc())
    )
    availability = avail_result.scalars().all()
    
    return templates.TemplateResponse("purohits_availability.html", {
        "request": request, 
        "user": current_user, 
        "purohits": purohits,
        "calendar_days": calendar_days,
        "availability": availability,
        "error": error
    })

@router.post("/purohits_availability/create")
async def create_purohits_availability(
    request: Request,
    astrologer_id: int = Form(...),
    specific_date: date = Form(...),
    start_time: time = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    from datetime import datetime
    
    # Calculate end time (+1 hour)
    start_dt = datetime.combine(specific_date, start_time)
    end_dt = start_dt + timedelta(hours=1)
    end_time = end_dt.time()
    
    # Check for overlaps
    overlap_query = select(AstrologerAvailability).filter(
        AstrologerAvailability.astrologer_id == astrologer_id,
        AstrologerAvailability.specific_date == specific_date,
        AstrologerAvailability.start_time < end_time,
        AstrologerAvailability.end_time > start_time
    )
    result = await db.execute(overlap_query)
    if result.scalars().first():
        import urllib.parse
        error_msg = urllib.parse.quote("Time slot overlaps with an existing appointment.")
        return RedirectResponse(url=f"/admin/purohits_availability?error={error_msg}", status_code=status.HTTP_303_SEE_OTHER)

    if start_dt < datetime.now():
        import urllib.parse
        error_msg = urllib.parse.quote("Cannot create slots in the past.")
        return RedirectResponse(url=f"/admin/purohits_availability?error={error_msg}", status_code=status.HTTP_303_SEE_OTHER)

    # Check if calendar day exists and is 'leave'
    cal_res = await db.execute(select(ExpertCalendarDay).filter(
        ExpertCalendarDay.expert_id == astrologer_id,
        ExpertCalendarDay.specific_date == specific_date
    ))
    cal_day = cal_res.scalars().first()
    if cal_day and cal_day.status == 'leave':
        import urllib.parse
        error_msg = urllib.parse.quote("Expert is marked as on Leave on this date. Please change calendar status first.")
        return RedirectResponse(url=f"/admin/purohits_availability?error={error_msg}", status_code=status.HTTP_303_SEE_OTHER)

    new_slot = AstrologerAvailability(
        astrologer_id=astrologer_id,
        specific_date=specific_date,
        start_time=start_time,
        end_time=end_time,
        is_booked=False
    )
    db.add(new_slot)
    await db.commit()
    return RedirectResponse(url="/admin/purohits_availability", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/purohits_availability/delete/{slot_id}")
async def delete_purohits_availability(
    slot_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_cookie)
):
    result = await db.execute(select(AstrologerAvailability).filter(AstrologerAvailability.id == slot_id))
    slot = result.scalars().first()
    if slot and not slot.is_booked:
        await db.delete(slot)
        await db.commit()
    return RedirectResponse(url="/admin/purohits_availability", status_code=status.HTTP_303_SEE_OTHER)
