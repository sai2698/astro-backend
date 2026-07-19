from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta, time
from app.models.appointment import AstrologerProfile, ExpertCalendarDay, AstrologerAvailability

async def ensure_upcoming_3_days_generated(db: AsyncSession):
    """
    Lazy-initializes availability slots for the next 3 days (today, tomorrow, day 3)
    for all active Astrologers and Purohitas.
    
    Rules:
    - 9-12 (9, 10, 11 AM slots)
    - 2-7 (14, 15, 16, 17, 18 PM slots)
    - If a calendar day is already initialized (working or leave), it does NOT regenerate.
      This respects manual deletions and leave days.
    """
    now = datetime.now()
    dates_to_check = [now.date() + timedelta(days=i) for i in range(3)]
    
    # 1. Fetch all active experts
    experts_res = await db.execute(
        select(AstrologerProfile).filter(AstrologerProfile.is_available == True)
    )
    experts = experts_res.scalars().all()
    
    if not experts:
        return
        
    slots_to_create = []
    days_to_create = []
    
    # Pre-fetch all calendar days for these 3 dates to avoid N+1 queries
    cal_res = await db.execute(
        select(ExpertCalendarDay).filter(ExpertCalendarDay.specific_date.in_(dates_to_check))
    )
    existing_calendar_days = cal_res.scalars().all()
    
    # Build a set of (expert_id, specific_date) that are already initialized
    initialized_days = {(d.expert_id, d.specific_date) for d in existing_calendar_days}
    
    # Standard slot start times
    default_start_hours = [9, 10, 11, 14, 15, 16, 17, 18]
    
    # Pre-fetch existing slots to know if a working day is empty
    slots_res = await db.execute(
        select(AstrologerAvailability).filter(AstrologerAvailability.specific_date.in_(dates_to_check))
    )
    existing_slots = slots_res.scalars().all()
    
    # Map (expert_id, date) -> count of slots
    slot_counts = {}
    for s in existing_slots:
        key = (s.astrologer_id, s.specific_date)
        slot_counts[key] = slot_counts.get(key, 0) + 1
        
    for expert in experts:
        for target_date in dates_to_check:
            is_initialized = (expert.user_id, target_date) in initialized_days
            day_status = 'working'
            
            if is_initialized:
                # Find the existing calendar day to check its status
                existing_day = next(d for d in existing_calendar_days if d.expert_id == expert.user_id and d.specific_date == target_date)
                day_status = existing_day.status
                
            if day_status == 'leave':
                continue
                
            # We generate slots if:
            # 1. Day is NOT initialized at all
            # OR 2. Day is initialized as 'working' BUT has 0 slots (e.g. Admin manually set to Working but didn't add slots)
            existing_count = slot_counts.get((expert.user_id, target_date), 0)
            
            if not is_initialized or existing_count == 0:
                if not is_initialized:
                    new_day = ExpertCalendarDay(
                        expert_id=expert.user_id,
                        specific_date=target_date,
                        status='working'
                    )
                    days_to_create.append(new_day)
                    
                # 2. Generate standard slots
                for hour in default_start_hours:
                    start_t = time(hour, 0)
                    end_t = time(hour + 1, 0)
                    
                    # Prevent generating slots in the past for TODAY
                    slot_dt = datetime.combine(target_date, start_t)
                    if slot_dt < now:
                        continue
                        
                    slots_to_create.append(
                        AstrologerAvailability(
                            astrologer_id=expert.user_id,
                            specific_date=target_date,
                            start_time=start_t,
                            end_time=end_t,
                            is_booked=False
                        )
                    )
                    
    # Bulk insert for performance
    if days_to_create:
        db.add_all(days_to_create)
    if slots_to_create:
        db.add_all(slots_to_create)
        
    if days_to_create or slots_to_create:
        await db.commit()
