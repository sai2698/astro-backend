import asyncio
from app.core.database import engine, Base
from app.models.appointment import AstrologerService, Appointment
from sqlalchemy import text

async def run_migration():
    async with engine.begin() as conn:
        print("Creating astrologer_services table and updating appointments...")
        try:
            await conn.run_sync(Base.metadata.create_all)
            print("Successfully created astrologer_services table.")
            
            # Alter appointments table to add selected_service and make service_id nullable
            await conn.execute(text("ALTER TABLE appointments ADD COLUMN IF NOT EXISTS selected_service VARCHAR;"))
            await conn.execute(text("ALTER TABLE appointments ALTER COLUMN service_id DROP NOT NULL;"))
            print("Successfully updated appointments table.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_migration())
