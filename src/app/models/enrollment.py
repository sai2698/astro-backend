from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint('user_id', 'course_id', name='uq_enrollment_user_course'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    progress_percent = Column(Integer, default=0)
    is_active = Column(Boolean, default=False)
    status = Column(String, default="pending") # pending, approved, expired

    user = relationship("User")
    course = relationship("Course")

class LectureProgress(Base):
    __tablename__ = "lecture_progress"
    __table_args__ = (
        UniqueConstraint('user_id', 'lecture_id', name='uq_lecture_progress_user_lecture'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lecture_id = Column(Integer, ForeignKey("lectures.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    progress_percent = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User")
    lecture = relationship("Lecture")
    course = relationship("Course")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True) # or appointment_id
    amount = Column(Float, nullable=False)
    razorpay_order_id = Column(String, index=True, nullable=True)
    status = Column(String, default="created") # created, paid, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    course = relationship("Course")
