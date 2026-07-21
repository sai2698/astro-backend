import sys
sys.path.append('.')
import asyncio
from app.api.routers.calendar import get_monthly_calendar

async def test():
    res = await get_monthly_calendar(year=2026, month=3, lat=17.385, lon=78.4867, tz=5.5)
    print(f"Year: {res['year']}, Month: {res['month']}, Days: {len(res['days'])}")
    print("Day 1:", res['days'][0])

asyncio.run(test())
