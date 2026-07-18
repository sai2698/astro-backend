import asyncio
import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.config import settings
from app.models.appointment import AstrologerAvailability
from app.models.user import User
from sqlalchemy.future import select

async def run():
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
    async with AsyncSession(engine) as session:
        result = await session.execute(select(AstrologerAvailability))
        slots = result.scalars().all()
        for slot in slots:
            slot.is_booked = False
        await session.commit()
    print('Slots reset')

if __name__ == "__main__":
    asyncio.run(run())
