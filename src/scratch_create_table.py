import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.models.appointment import ConsultationFile

async def run():
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
    async with engine.begin() as conn:
        await conn.run_sync(ConsultationFile.__table__.create, checkfirst=True)
    print("Table created.")

if __name__ == "__main__":
    asyncio.run(run())
