import asyncio
import sys
import os

# Add the backend dir to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy import update
from app.core.database import AsyncSessionLocal
from app.models.user import User  # IMPORT THIS
from app.models.course import Lecture

async def main():
    async with AsyncSessionLocal() as db:
        stmt = (
            update(Lecture)
            .where(Lecture.video_url.contains("commondatastorage.googleapis.com"))
            .values(video_url="https://media.w3.org/2010/05/sintel/trailer.mp4")
        )
        result = await db.execute(stmt)
        await db.commit()
        print(f"Updated video URLs in database.")

if __name__ == "__main__":
    asyncio.run(main())
