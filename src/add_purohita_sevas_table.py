import asyncio
from app.core.database import engine, Base
from app.models.appointment import PurohitaSeva

async def run_migration():
    async with engine.begin() as conn:
        print("Creating purohita_sevas table...")
        try:
            await conn.run_sync(Base.metadata.create_all)
            print("Successfully created purohita_sevas table.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_migration())
