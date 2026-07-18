from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class EnrollmentProgressUpdate(BaseModel):
    progress_percent: int = Field(ge=0, le=100)

class OrderCreate(BaseModel):
    course_id: int

class OrderVerify(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    course_id: int

class Order(BaseModel):
    id: int
    amount: float
    razorpay_order_id: Optional[str] = None
    status: str
    
    class Config:
        from_attributes = True

class CourseSnippet(BaseModel):
    id: int
    title: str
    thumbnail_url: Optional[str] = None
    level: str = "beginner"
    rating_avg: float = 0.0
    total_duration_minutes: int = 0

    class Config:
        from_attributes = True

class Enrollment(BaseModel):
    id: int
    user_id: int
    course_id: int
    progress_percent: int
    enrolled_at: datetime
    course_title: Optional[str] = None
    course: Optional[CourseSnippet] = None
    status: Optional[str] = None
    
    class Config:
        from_attributes = True
