from pydantic import BaseModel
from typing import Optional, List
from datetime import date, time, datetime
from app.schemas.user import User as UserSchema

class ServiceTypeBase(BaseModel):
    name: str
    description: Optional[str] = None
    duration_minutes: int
    base_price: float
    category: str = "consultation"

class ServiceType(ServiceTypeBase):
    id: int
    class Config:
        from_attributes = True

class PurohitaSevaSchema(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        from_attributes = True

class AstrologerServiceSchema(BaseModel):
    id: int
    name: str
    price: float
    duration_minutes: Optional[int] = 30

    class Config:
        from_attributes = True

class AstrologerProfileBase(BaseModel):
    bio: Optional[str] = None
    experience_years: int
    price_per_session: float
    rating_avg: float = 0.0
    is_available: bool = True
    profile_type: str = "astrologer"
    sevas: Optional[str] = None
    purohita_sevas: List[PurohitaSevaSchema] = []
    astrologer_services: List[AstrologerServiceSchema] = []

class AstrologerProfile(AstrologerProfileBase):
    user_id: int
    rating_avg: float
    name: Optional[str] = None # Added via join
    class Config:
        from_attributes = True

class AstrologerAvailabilityBase(BaseModel):
    specific_date: date
    start_time: time
    end_time: time

class AstrologerAvailability(AstrologerAvailabilityBase):
    id: int
    astrologer_id: int
    is_booked: bool
    class Config:
        from_attributes = True

class AppointmentCreate(BaseModel):
    astrologer_id: int
    service_id: Optional[int] = None
    availability_id: int
    selected_seva: Optional[str] = None
    selected_service: Optional[str] = None

class AppointmentVerifyPayment(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    appointment_id: int

class ConsultationFileSchema(BaseModel):
    id: int
    name: str
    file_url: str
    is_external: bool

    class Config:
        from_attributes = True

class Appointment(BaseModel):
    id: int
    user_id: int
    astrologer_id: int
    service_id: Optional[int] = None
    availability_id: int
    scheduled_date: date
    scheduled_start_time: time
    status: str
    google_meet_link: Optional[str] = None
    report_file_url: Optional[str] = None
    selected_seva: Optional[str] = None
    selected_service: Optional[str] = None
    razorpay_order_id: Optional[str] = None
    amount: Optional[float] = None
    created_at: datetime
    
    user: Optional[UserSchema] = None
    files: List[ConsultationFileSchema] = []
    
    astrologer_name: Optional[str] = None
    service_name: Optional[str] = None
    
    class Config:
        from_attributes = True
