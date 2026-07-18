import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from app.models.user import User  # Must import to resolve relationship
from app.models.appointment import AstrologerAvailability, AstrologerProfile
from app.core.config import settings

async def run():
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
    async_session = sessionmaker(engine, class_=AsyncSession)
    async with async_session() as session:
        res = await session.execute(select(AstrologerAvailability))
        slots = res.scalars().all()
        for s in slots:
            print(f"ID: {s.id}, Booked: {s.is_booked}, Type of Booked: {type(s.is_booked)}")

if __name__ == "__main__":
    asyncio.run(run())
