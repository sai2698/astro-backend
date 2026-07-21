import sys
sys.path.append('.')
import asyncio
from app.api.routers.kundali import get_current_moudya

async def main():
    print(await get_current_moudya())

asyncio.run(main())
