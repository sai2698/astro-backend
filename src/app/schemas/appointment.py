from pydantic import BaseModel
from typing import Optional, List
from datetime import date, time, datetime

class ServiceTypeBase(BaseModel):
    name: str
    description: Optional[str] = None
    duration_minutes: int
    base_price: float

class ServiceType(ServiceTypeBase):
    id: int
    class Config:
        from_attributes = True

class AstrologerProfileBase(BaseModel):
    bio: Optional[str] = None
    experience_years: int
    price_per_session: float
    is_available: bool = True

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
    service_id: int
    availability_id: int

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
    service_id: int
    availability_id: int
    scheduled_date: date
    scheduled_start_time: time
    status: str
    google_meet_link: Optional[str] = None
    report_file_url: Optional[str] = None
    files: List[ConsultationFileSchema] = []
    created_at: datetime
    
    astrologer_name: Optional[str] = None
    service_name: Optional[str] = None
    
    class Config:
        from_attributes = True
