from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, time, datetime

class UserBase(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    dob: Optional[date] = None
    time_of_birth: Optional[time] = None
    place_of_birth: Optional[str] = None
    birth_lat: Optional[float] = None
    birth_lon: Optional[float] = None

class UserCreate(UserBase):
    email: EmailStr
    password: str

class UserUpdate(UserBase):
    pass

class GoogleToken(BaseModel):
    id_token: str

class UserInDBBase(UserBase):
    id: int
    role: str
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass
