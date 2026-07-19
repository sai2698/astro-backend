import asyncio
import os
import sys

# Add the backend directory to sys.path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from sqlalchemy import text

async def migrate():
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=True)
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE service_types ADD COLUMN category VARCHAR DEFAULT 'consultation'"))
            print("Successfully added category column to service_types")
        except Exception as e:
            print(f"Error altering service_types (column might exist): {e}")

        try:
            await conn.execute(text("ALTER TABLE astrologer_profiles ADD COLUMN profile_type VARCHAR DEFAULT 'astrologer'"))
            print("Successfully added profile_type column to astrologer_profiles")
        except Exception as e:
            print(f"Error altering astrologer_profiles (column might exist): {e}")

if __name__ == "__main__":
    asyncio.run(migrate())
