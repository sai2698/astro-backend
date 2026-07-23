import sys
import os
import asyncio
from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.enrollment import Enrollment
from app.services import drive_service

async def run_expiration():
    print(f"[{datetime.now()}] Starting enrollment expiration job...")
    
    async with SessionLocal() as db:
        # Find all active enrollments where expiry_date has passed
        query = select(Enrollment).options(selectinload(Enrollment.course)).filter(
            Enrollment.is_active == True,
            Enrollment.expiry_date != None,
            Enrollment.expiry_date <= datetime.now()
        )
        
        result = await db.execute(query)
        expired_enrollments = result.scalars().all()
        
        if not expired_enrollments:
            print(f"[{datetime.now()}] No expired enrollments found. Job complete.")
            return
            
        print(f"[{datetime.now()}] Found {len(expired_enrollments)} expired enrollments to process.")
        
        for enrollment in expired_enrollments:
            print(f"Processing expiration for enrollment ID: {enrollment.id}")
            
            # Update database status
            enrollment.is_active = False
            enrollment.status = "expired"
            
        await db.commit()
        print(f"[{datetime.now()}] Job complete. Processed {len(expired_enrollments)} enrollments.")

if __name__ == "__main__":
    asyncio.run(run_expiration())
