from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import traceback
import pytz

from kundali_gen.core.hindu_calendar import build_calendar
from kundali_gen.core.astro_calc import geocode_place

router = APIRouter()

@router.get("/month")
async def get_monthly_calendar(
    year: int = Query(..., description="Year (e.g. 2026)"),
    month: int = Query(..., description="Month (1-12)"),
    lat: Optional[float] = Query(28.6139, description="Latitude"),
    lon: Optional[float] = Query(77.2090, description="Longitude"),
    tz: Optional[float] = Query(5.5, description="Timezone offset from UTC in hours"),
    place: Optional[str] = Query(None, description="Place name to geocode")
):
    try:
        if month < 1 or month > 12:
            raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
            
        location_name = "New Delhi, India"
        
        if place:
            try:
                g_lat, g_lon, g_address, g_tz_str = geocode_place(place)
                lat = g_lat
                lon = g_lon
                location_name = g_address
                
                # Get timezone offset for the 1st of the month
                tz_obj = pytz.timezone(g_tz_str)
                dt = datetime(year, month, 1)
                tz = tz_obj.utcoffset(dt).total_seconds() / 3600.0
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Could not resolve location: {str(e)}")

        rows = build_calendar(year, month, lat, lon, tz, location_name)
        
        # Serialize the date object
        serialized_rows = []
        for r in rows:
            serialized_rows.append({
                "date": r["date"].isoformat(),
                "weekday": r["weekday"],
                "amanta_month": r["amanta_month"],
                "purnimanta_month": r["purnimanta_month"],
                "paksha": r["paksha"],
                "tithi": r["tithi"],
                "nakshatra": r["nakshatra"],
                "yoga": r["yoga"],
                "karana": r["karana"],
                "rashi": r["rashi"],
                "festivals": r["festivals"]
            })
            
        return {
            "year": year,
            "month": month,
            "location_name": location_name,
            "lat": lat,
            "lon": lon,
            "days": serialized_rows
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
