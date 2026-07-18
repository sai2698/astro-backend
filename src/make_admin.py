import asyncio
from sqlalchemy.future import select
from sqlalchemy import update
from app.core.database import AsyncSessionLocal
from app.models.user import User

async def main():
    async with AsyncSessionLocal() as db:
        await db.execute(update(User).where(User.email == "expert@astrology.com").values(role="admin"))
        await db.commit()
        print("Updated expert@astrology.com to admin")

if __name__ == "__main__":
    asyncio.run(main())
