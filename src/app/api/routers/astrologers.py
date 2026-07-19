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
from app.api.routers.utils import ensure_upcoming_3_days_generated

router = APIRouter()

from sqlalchemy.orm import selectinload

@router.get("/", response_model=List[AstrologerProfileSchema])
async def list_astrologers(type: str = None, db: AsyncSession = Depends(get_db)):
    # Join with User to get names, load purohita_sevas and astrologer_services
    query = select(AstrologerProfile, User.name).join(User, AstrologerProfile.user_id == User.id).options(selectinload(AstrologerProfile.purohita_sevas), selectinload(AstrologerProfile.astrologer_services))
    if type:
        query = query.filter(AstrologerProfile.profile_type == type)
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
            "profile_type": profile.profile_type,
            "sevas": profile.sevas,
            "purohita_sevas": [
                {"id": s.id, "name": s.name, "price": s.price} 
                for s in profile.purohita_sevas
            ],
            "astrologer_services": [
                {"id": s.id, "name": s.name, "price": s.price, "duration_minutes": s.duration_minutes}
                for s in profile.astrologer_services
            ],
            "name": name
        }
        astrologers.append(AstrologerProfileSchema(**profile_dict))
    
    return astrologers

@router.get("/{astrologer_id}/availability", response_model=List[AstrologerAvailabilitySchema])
async def get_availability(astrologer_id: int, db: AsyncSession = Depends(get_db)):
    await ensure_upcoming_3_days_generated(db)
    
    query = select(AstrologerAvailability).filter(
        AstrologerAvailability.astrologer_id == astrologer_id,
        AstrologerAvailability.is_booked == False
    )
    result = await db.execute(query)
    slots = result.scalars().all()
    
    from datetime import datetime
    now = datetime.now()
    valid_slots = [
        s for s in slots 
        if datetime.combine(s.specific_date, s.start_time) >= now
    ]
    return valid_slots

@router.get("/services", response_model=List[ServiceTypeSchema])
async def list_services(category: str = None, db: AsyncSession = Depends(get_db)):
    query = select(ServiceType)
    if category:
        query = query.filter(ServiceType.category == category)
    result = await db.execute(query)
    services = result.scalars().all()
    
    # Auto-create default service if none exists
    if not services and category == 'purohita_seva':
        default_service = ServiceType(
            name="Purohita Seva",
            description="Custom Purohita Seva",
            duration_minutes=60,
            base_price=0.0,
            category="purohita_seva"
        )
        db.add(default_service)
        await db.commit()
        await db.refresh(default_service)
        services = [default_service]
        
    return services
