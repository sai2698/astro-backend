from pydantic import BaseModel
from typing import Optional, List

class CategoryBase(BaseModel):
    name: str
    icon: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    class Config:
        from_attributes = True

class LectureBase(BaseModel):
    title: str
    video_url: Optional[str] = None
    duration_seconds: int = 0
    order_index: int = 0
    is_preview: bool = False

class LectureCreate(LectureBase):
    section_id: int

class Lecture(LectureBase):
    id: int
    section_id: int
    progress_percent: int = 0
    class Config:
        from_attributes = True

class CourseSectionBase(BaseModel):
    title: str
    order_index: int = 0

class CourseSectionCreate(CourseSectionBase):
    course_id: int

class CourseSection(CourseSectionBase):
    id: int
    course_id: int
    lectures: List[Lecture] = []
    class Config:
        from_attributes = True

class CourseBase(BaseModel):
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    price: float = 0.0
    discount_price: Optional[float] = None
    level: str = "beginner"
    language: str = "english"
    is_published: bool = False
    category_id: int

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    price: Optional[float] = None
    discount_price: Optional[float] = None
    level: Optional[str] = None
    language: Optional[str] = None
    is_published: Optional[bool] = None
    category_id: Optional[int] = None

class Course(CourseBase):
    id: int
    instructor_id: int
    rating_avg: float
    total_students: int
    total_duration_minutes: int
    is_enrolled: bool = False
    enrollment_status: Optional[str] = None
    class Config:
        from_attributes = True

class CourseDetail(Course):
    sections: List[CourseSection] = []
    class Config:
        from_attributes = True

class CourseReviewBase(BaseModel):
    rating: int
    comment: Optional[str] = None

class CourseReviewCreate(CourseReviewBase):
    pass

class CourseReview(CourseReviewBase):
    id: int
    course_id: int
    user_id: int
    class Config:
        from_attributes = True
