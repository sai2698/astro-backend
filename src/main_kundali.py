"""
Kundali PDF Generator - Main Entry Point
Usage: python main.py --name "Sai Naveen" --gender Male --dob 2026-02-26 --time 06:30 --place "Raniganj, Hyderabad, India" --output Kundali.pdf
"""
import argparse
from datetime import datetime

from kundali_gen.core.astro_calc import calc_all
from kundali_gen.core.panchanga import get_full_panchanga
from kundali_gen.core.divisional import calc_all_vargas
from kundali_gen.core.dasha import generate_vimshottari_dasha
from kundali_gen.core.ashtakavarga import calc_all_ashtakavarga
from kundali_gen.core.yogas import (
    check_kaal_sarp, check_mangal_dosha,
    get_jaimini_karakas, get_jaimini_arudhas
)
from kundali_gen.pdf.html_renderer import render_html_pdf


def main():
    parser = argparse.ArgumentParser(description="Generate a comprehensive Vedic Kundali PDF")
    parser.add_argument("--name", default="Sai Naveen")
    parser.add_argument("--gender", default="Male")
    parser.add_argument("--dob", default="2026-02-26", help="YYYY-MM-DD")
    parser.add_argument("--time", default="06:30", help="HH:MM 24h")
    parser.add_argument("--place", default="Hyderabad, Telangana, India")
    parser.add_argument("--lat", type=float, default=None, help="Latitude (optional bypass for geocoding)")
    parser.add_argument("--lon", type=float, default=None, help="Longitude (optional bypass)")
    parser.add_argument("--tz", default=None, help="Timezone string e.g. 'Asia/Kolkata'")
    parser.add_argument("--output", default="Kundali_Full.pdf")
    parser.add_argument("--charttype", choices=["full", "custom"], default="full", help="Type of chart to generate: full or custom")
    args = parser.parse_args()

    print("[1/7] Geocoding and calculating planetary positions...")
    calc = calc_all(args.dob, args.time, args.place, lat=args.lat, lon=args.lon, tz_str=args.tz)
    calc["name"] = args.name
    calc["gender"] = args.gender
    try:
        dt = datetime.strptime(args.dob, "%Y-%m-%d")
        calc["dob_display"] = dt.strftime("%d/%m/%Y")
    except Exception:
        calc["dob_display"] = args.dob

    planets = calc["planets"]
    ascendant = calc["ascendant"]
    birth_dt = calc["utc_dt"]

    print("[2/7] Computing Panchanga...")
    panchanga = get_full_panchanga(calc)

    print("[3/7] Computing Divisional Charts...")
    all_vargas = calc_all_vargas(planets, ascendant)
    for p_name, p_data in planets.items():
        p_data["nav_sign_idx"] = all_vargas["D9"].get(p_name, 0)
    ascendant["nav_sign_idx"] = all_vargas["D9"].get("Ascendant", 0)

    print("[4/7] Computing Vimshottari Dasha...")
    moon_long = planets["Moon"]["longitude"]
    dasha_rows_3, dasha_lord, balance_str = generate_vimshottari_dasha(birth_dt, moon_long, levels=3)
    dasha_rows_4, _, _ = generate_vimshottari_dasha(birth_dt, moon_long, levels=4)
    cutoff = birth_dt.replace(year=birth_dt.year + 1)
    sookshma_1yr = [r for r in dasha_rows_4 if r["start"] <= cutoff]
    
    calc["dasha_lord"] = dasha_lord
    calc["balance_str"] = balance_str

    print("[5/7] Computing Ashtakavarga...")
    av_data = calc_all_ashtakavarga(planets, ascendant)

    print("[6/7] Computing Yogas & Karakas...")
    kaal_sarp = check_kaal_sarp(planets)
    mangal = check_mangal_dosha(planets, ascendant["sign_idx"])
    jaimini_karakas = get_jaimini_karakas(planets)

    print("[7/7] Rendering HTML PDF...")
    render_html_pdf(
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
        output_path=args.output,
        charttype=args.charttype,
    )
    print(f"\n[DONE] Kundali PDF generated: {args.output}")
    print(f"       Name: {args.name} | DOB: {args.dob} {args.time} | Place: {args.place}")


if __name__ == "__main__":
    main()
