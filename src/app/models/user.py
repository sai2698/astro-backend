from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time, Float
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=False)
    
    # Astrology specific
    dob = Column(Date, nullable=True)
    time_of_birth = Column(Time, nullable=True)
    place_of_birth = Column(String, nullable=True)
    birth_lat = Column(Float, nullable=True)
    birth_lon = Column(Float, nullable=True)
    
    role = Column(String, default="student") # student, astrologer, admin
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
