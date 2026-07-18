import asyncio
from app.core.database import engine
from sqlalchemy import text

async def alter_table():
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN birth_lat FLOAT;"))
            print("Added birth_lat")
        except Exception as e:
            print(f"Error adding birth_lat: {e}")
            
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN birth_lon FLOAT;"))
            print("Added birth_lon")
        except Exception as e:
            print(f"Error adding birth_lon: {e}")

if __name__ == "__main__":
    asyncio.run(alter_table())
