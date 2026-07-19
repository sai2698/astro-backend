import asyncio
from sqlalchemy import text
from app.core.database import engine

async def run_migration():
    async with engine.begin() as conn:
        print("Adding selected_seva column to appointments...")
        try:
            await conn.execute(text("ALTER TABLE appointments ADD COLUMN selected_seva TEXT;"))
            print("Successfully added selected_seva column.")
        except Exception as e:
            print(f"Error (might already exist): {e}")

if __name__ == "__main__":
    asyncio.run(run_migration())
