import asyncio
from sqlalchemy import text
from app.core.database import engine

async def run_migration():
    async with engine.begin() as conn:
        print("Adding sevas column to astrologer_profiles...")
        try:
            await conn.execute(text("ALTER TABLE astrologer_profiles ADD COLUMN sevas TEXT;"))
            print("Successfully added sevas column.")
        except Exception as e:
            print(f"Error (might already exist): {e}")

if __name__ == "__main__":
    asyncio.run(run_migration())
