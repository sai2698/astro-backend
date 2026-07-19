from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import traceback

from kundali_gen.core.astro_calc import calc_all
from kundali_gen.core.panchanga import get_full_panchanga
from kundali_gen.core.divisional import calc_all_vargas
from kundali_gen.core.dasha import generate_vimshottari_dasha
from kundali_gen.core.ashtakavarga import calc_all_ashtakavarga
from kundali_gen.core.yogas import (
    check_kaal_sarp, check_mangal_dosha,
    get_jaimini_karakas
)
from kundali_gen.pdf.html_template import build_html
from kundali_gen.pdf.json_builder import build_json

router = APIRouter()

class KundaliRequest(BaseModel):
    name: str = Field(..., example="Vineetha Knachi")
    gender: str = Field(default="Male", example="Male")
    dob: str = Field(..., example="2000-03-11", description="YYYY-MM-DD")
    time: str = Field(..., example="20:55", description="HH:MM 24h")
    place: str = Field(..., example="Hyderabad, India")
    lat: Optional[float] = None
    lon: Optional[float] = None
    tz: Optional[str] = None
    charttype: str = Field(default="custom", description="full or custom")
    language: str = Field(default="en", description="en or te")
    output_type: str = Field(default="html", description="html or json")

@router.post("/generate")
async def generate_kundali(request: KundaliRequest):
    try:
        calc = calc_all(
            request.dob, request.time, request.place, 
            lat=request.lat, lon=request.lon, tz_str=request.tz
        )
        calc["name"] = request.name
        calc["gender"] = request.gender
        try:
            dt = datetime.strptime(request.dob, "%Y-%m-%d")
            calc["dob_display"] = dt.strftime("%d/%m/%Y")
        except Exception:
            calc["dob_display"] = request.dob

        planets = calc["planets"]
        ascendant = calc["ascendant"]
        birth_dt = calc["utc_dt"]

        panchanga = get_full_panchanga(calc)

        all_vargas = calc_all_vargas(planets, ascendant)
        for p_name, p_data in planets.items():
            p_data["nav_sign_idx"] = all_vargas["D9"].get(p_name, 0)
        ascendant["nav_sign_idx"] = all_vargas["D9"].get("Ascendant", 0)

        moon_long = planets["Moon"]["longitude"]
        dasha_rows_3, dasha_lord, balance_str = generate_vimshottari_dasha(birth_dt, moon_long, levels=3)
        dasha_rows_4, _, _ = generate_vimshottari_dasha(birth_dt, moon_long, levels=4)
        cutoff = birth_dt.replace(year=birth_dt.year + 1)
        sookshma_1yr = [r for r in dasha_rows_4 if r["start"] <= cutoff]
        
        calc["dasha_lord"] = dasha_lord
        calc["balance_str"] = balance_str

        av_data = calc_all_ashtakavarga(planets, ascendant)

        kaal_sarp = check_kaal_sarp(planets)
        mangal = check_mangal_dosha(planets, ascendant["sign_idx"])
        jaimini_karakas = get_jaimini_karakas(planets)

        if request.output_type == "json":
            json_data = build_json(
                data=calc,
                panchanga=panchanga,
                planets=planets,
                ascendant=ascendant,
                all_vargas=all_vargas,
                dasha_rows_3=dasha_rows_3,
                sookshma_1yr=sookshma_1yr,
                av_data=av_data,
                kaal_sarp=kaal_sarp,
                mangal=mangal,
                jaimini_karakas=jaimini_karakas,
                charttype=request.charttype,
                language=request.language
            )
            return json_data

        html_str = build_html(
            data=calc,
            panchanga=panchanga,
            planets=planets,
            ascendant=ascendant,
            all_vargas=all_vargas,
            dasha_rows_3=dasha_rows_3,
            sookshma_1yr=sookshma_1yr,
            av_data=av_data,
            kaal_sarp=kaal_sarp,
            mangal=mangal,
            jaimini_karakas=jaimini_karakas,
            charttype=request.charttype,
            language=request.language
        )
        
        return HTMLResponse(content=html_str)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
