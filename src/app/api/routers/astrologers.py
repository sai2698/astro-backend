from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.core.database import get_db
from app.models.appointment import AstrologerProfile, AstrologerAvailability, ServiceType
from app.models.user import User
from app.schemas.appointment import AstrologerProfile as AstrologerProfileSchema
from app.schemas.appointment import AstrologerAvailability as AstrologerAvailabilitySchema
from app.schemas.appointment import ServiceType as ServiceTypeSchema

router = APIRouter()

@router.get("/", response_model=List[AstrologerProfileSchema])
async def list_astrologers(db: AsyncSession = Depends(get_db)):
    # Join with User to get names
    query = select(AstrologerProfile, User.name).join(User, AstrologerProfile.user_id == User.id)
    result = await db.execute(query)
    
    astrologers = []
    for profile, name in result.all():
        profile_dict = {
            "user_id": profile.user_id,
            "bio": profile.bio,
            "experience_years": profile.experience_years,
            "price_per_session": profile.price_per_session,
            "rating_avg": profile.rating_avg,
            "is_available": profile.is_available,
            "name": name
        }
        astrologers.append(AstrologerProfileSchema(**profile_dict))
    
    return astrologers

@router.get("/{astrologer_id}/availability", response_model=List[AstrologerAvailabilitySchema])
async def get_availability(astrologer_id: int, db: AsyncSession = Depends(get_db)):
    query = select(AstrologerAvailability).filter(
        AstrologerAvailability.astrologer_id == astrologer_id,
        AstrologerAvailability.is_booked == False
    )
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/services", response_model=List[ServiceTypeSchema])
async def list_services(db: AsyncSession = Depends(get_db)):
    query = select(ServiceType)
    result = await db.execute(query)
    return result.scalars().all()
