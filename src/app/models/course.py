from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    icon = Column(String, nullable=True)

    courses = relationship("Course", back_populates="category")

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    subtitle = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    price = Column(Float, nullable=False, default=0.0)
    discount_price = Column(Float, nullable=True)
    
    instructor_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    level = Column(String, default="beginner") # beginner/intermediate/advanced
    language = Column(String, default="english")
    rating_avg = Column(Float, default=0.0)
    total_students = Column(Integer, default=0)
    total_duration_minutes = Column(Integer, default=0)
    is_published = Column(Boolean, default=False)

    category = relationship("Category", back_populates="courses")
    instructor = relationship("User")
    sections = relationship("CourseSection", back_populates="course", cascade="all, delete-orphan", order_by="CourseSection.order_index")
    reviews = relationship("CourseReview", back_populates="course", cascade="all, delete-orphan")

class CourseSection(Base):
    __tablename__ = "course_sections"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String, nullable=False)
    order_index = Column(Integer, default=0)

    course = relationship("Course", back_populates="sections")
    lectures = relationship("Lecture", back_populates="section", cascade="all, delete-orphan", order_by="Lecture.order_index")

class Lecture(Base):
    __tablename__ = "lectures"

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("course_sections.id"))
    title = Column(String, nullable=False)
    video_url = Column(String, nullable=True) # S3/R2 Key
    duration_seconds = Column(Integer, default=0)
    order_index = Column(Integer, default=0)
    is_preview = Column(Boolean, default=False)

    section = relationship("CourseSection", back_populates="lectures")

class CourseReview(Base):
    __tablename__ = "course_reviews"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Integer, nullable=False) # 1-5
    comment = Column(Text, nullable=True)

    course = relationship("Course", back_populates="reviews")
    user = relationship("User")

class Wishlist(Base):
    __tablename__ = "wishlists"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)
