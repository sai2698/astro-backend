from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Date, Time, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class ServiceType(Base):
    __tablename__ = "service_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, default=30)
    base_price = Column(Float, nullable=False)
    category = Column(String, default="consultation") # 'consultation' or 'purohita_seva'

class AstrologerProfile(Base):
    __tablename__ = "astrologer_profiles"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    bio = Column(Text, nullable=True)
    experience_years = Column(Integer, default=0)
    price_per_session = Column(Float, nullable=False)
    rating_avg = Column(Float, default=0.0)
    is_available = Column(Boolean, default=True)
    profile_type = Column(String, default="astrologer") # 'astrologer' or 'purohit'
    sevas = Column(Text, nullable=True) # comma-separated list of sevas (deprecated, use purohita_sevas)
    
    user = relationship("User")
    purohita_sevas = relationship("PurohitaSeva", back_populates="purohita", cascade="all, delete-orphan")
    astrologer_services = relationship("AstrologerService", back_populates="astrologer", cascade="all, delete-orphan")

class AstrologerService(Base):
    __tablename__ = "astrologer_services"

    id = Column(Integer, primary_key=True, index=True)
    astrologer_id = Column(Integer, ForeignKey("astrologer_profiles.user_id"), nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False, default=0.0)
    duration_minutes = Column(Integer, default=30)

    astrologer = relationship("AstrologerProfile", back_populates="astrologer_services")

class PurohitaSeva(Base):
    __tablename__ = "purohita_sevas"

    id = Column(Integer, primary_key=True, index=True)
    purohita_id = Column(Integer, ForeignKey("astrologer_profiles.user_id"), nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False, default=0.0)

    purohita = relationship("AstrologerProfile", back_populates="purohita_sevas")

class ExpertCalendarDay(Base):
    __tablename__ = "expert_calendar_days"

    id = Column(Integer, primary_key=True, index=True)
    expert_id = Column(Integer, ForeignKey("astrologer_profiles.user_id"), nullable=False)
    specific_date = Column(Date, nullable=False)
    status = Column(String, default="working") # 'working' or 'leave'

    expert = relationship("AstrologerProfile")

class AstrologerAvailability(Base):
    __tablename__ = "astrologer_availability"

    id = Column(Integer, primary_key=True, index=True)
    astrologer_id = Column(Integer, ForeignKey("astrologer_profiles.user_id"), nullable=False)
    specific_date = Column(Date, nullable=False) # e.g., '2023-10-15'
    start_time = Column(Time, nullable=False) # e.g., '10:00:00'
    end_time = Column(Time, nullable=False) # e.g., '11:00:00'
    is_booked = Column(Boolean, default=False)

    astrologer = relationship("AstrologerProfile")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    astrologer_id = Column(Integer, ForeignKey("astrologer_profiles.user_id"), nullable=False)
    service_id = Column(Integer, ForeignKey("service_types.id"), nullable=True) # Nullable because of AstrologerService
    availability_id = Column(Integer, ForeignKey("astrologer_availability.id"), nullable=False)
    
    scheduled_date = Column(Date, nullable=False)
    scheduled_start_time = Column(Time, nullable=False)
    
    status = Column(String, default="pending") # pending, scheduled, completed, cancelled, payment_pending
    google_meet_link = Column(String, nullable=True) # uniquely identifies the video room
    report_file_url = Column(String, nullable=True) # Deprecated, use ConsultationFile
    selected_seva = Column(String, nullable=True) # The specific seva selected by the user
    selected_service = Column(String, nullable=True) # The specific astrologer service selected
    razorpay_order_id = Column(String, index=True, nullable=True)
    amount = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", foreign_keys=[user_id])
    astrologer = relationship("AstrologerProfile", foreign_keys=[astrologer_id])
    service = relationship("ServiceType")
    files = relationship("ConsultationFile", back_populates="appointment", cascade="all, delete-orphan")

class ConsultationFile(Base):
    __tablename__ = "consultation_files"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False)
    name = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    is_external = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    appointment = relationship("Appointment", back_populates="files")
