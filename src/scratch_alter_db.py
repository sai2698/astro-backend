import asyncio
import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

async def run():
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
    async with engine.begin() as conn:
        await conn.execute(sqlalchemy.text('ALTER TABLE appointments ADD COLUMN IF NOT EXISTS report_file_url VARCHAR(255);'))
    print('Done')

if __name__ == "__main__":
    asyncio.run(run())
