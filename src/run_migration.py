import asyncio
from app.core.database import engine, Base
import app.models.appointment # Import to ensure models are registered
import app.models.user
import app.models.course
import app.models.enrollment

async def create_tables():
    async with engine.begin() as conn:
        print("Creating new tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully.")

if __name__ == "__main__":
    asyncio.run(create_tables())
