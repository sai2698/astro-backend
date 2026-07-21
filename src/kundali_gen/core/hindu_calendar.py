#!/usr/bin/env python3
import argparse
import math
from datetime import datetime, timedelta

import swisseph as swe

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------

VARA_NAMES = [
    "Somavara (Monday)", "Mangalavara (Tuesday)", "Budhavara (Wednesday)",
    "Guruvara (Thursday)", "Shukravara (Friday)", "Shanivara (Saturday)",
    "Ravivara (Sunday)",
]
# swe.calc weekday: we'll compute vara independently from the Python date.
WEEKDAY_NAMES = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada",
    "Revati",
]

YOGAS = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
    "Sukarma", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata",
    "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana", "Parigha",
    "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra",
    "Vaidhriti",
]

# Karana: 4 "fixed" karanas occur only once a lunar month (at the very
# start/end), and 7 "movable" karanas repeat 8 times each to fill the rest.
KARANA_FIXED = {1: "Kimstughna", 58: "Shakuni", 59: "Chatushpada", 60: "Naga"}
KARANA_MOVABLE = ["Bava", "Balava", "Kaulava", "Taitila", "Garija", "Vanija", "Vishti (Bhadra)"]

# Rashi (sidereal zodiac sign) -> Amanta lunar month name traditionally
# associated with the New Moon occurring while the Sun transits that sign.
RASHI_TO_MONTH = [
    "Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada",
    "Ashwin", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna",
]
RASHI_NAMES = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", "Tula",
    "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena",
]

def purnimanta_name(amanta_month, paksha):
    if paksha == "Shukla":
        return amanta_month
    idx = RASHI_TO_MONTH.index(amanta_month)
    return RASHI_TO_MONTH[(idx + 1) % 12]

FESTIVALS = {
    ("Chaitra", "Shukla", 1): "Ugadi / Gudi Padwa (Chaitra Shukla Pratipada)",
    ("Chaitra", "Shukla", 9): "Sri Rama Navami",
    ("Vaishakha", "Shukla", 3): "Akshaya Tritiya",
    ("Jyeshtha", "Shukla", 15): "Vat Purnima",
    ("Ashadha", "Shukla", 2): "Ratha Yatra (Puri tradition)",
    ("Shravana", "Shukla", 15): "Raksha Bandhan / Shravana Purnima",
    ("Shravana", "Krishna", 8): "Krishna Janmashtami",
    ("Bhadrapada", "Shukla", 4): "Vinayaka Chavithi / Ganesh Chaturthi",
    ("Bhadrapada", "Krishna", 8): "Pitru Paksha begins (approx.)",
    ("Ashwin", "Shukla", 1): "Navaratri begins",
    ("Ashwin", "Shukla", 9): "Maha Navami",
    ("Ashwin", "Shukla", 10): "Vijayadashami / Dussehra",
    ("Ashwin", "Krishna", 15): "Diwali / Lakshmi Puja (Amavasya)",
    ("Kartika", "Shukla", 1): "Bali Padyami / Govardhan Puja",
    ("Kartika", "Shukla", 2): "Bhai Dooj / Yama Dwitiya",
    ("Kartika", "Shukla", 11): "Kartika Ekadashi",
    ("Kartika", "Shukla", 15): "Kartika Purnima",
    ("Margashirsha", "Shukla", 11): "Vaikuntha / Mokshada Ekadashi",
    ("Pausha", "Krishna", 5): "Sankashti Chaturthi (typical)",
    ("Magha", "Shukla", 5): "Vasant Panchami",
    ("Magha", "Krishna", 14): "Maha Shivaratri (many traditions)",
    ("Phalguna", "Shukla", 15): "Holika Dahan / Holi",
}

GENERIC_TITHI_NOTES = {
    11: "Ekadashi (fasting day)",
    15: None, 
}

FLAG = swe.FLG_MOSEPH | swe.FLG_SIDEREAL

def sidereal_lonlat(jd_ut, body):
    res, _ = swe.calc_ut(jd_ut, body, FLAG)
    return res[0] 

def sun_moon_lon(jd_ut):
    return sidereal_lonlat(jd_ut, swe.SUN), sidereal_lonlat(jd_ut, swe.MOON)

def local_sunrise_jd(jd_midnight_ut, lat, lon):
    geopos = (lon, lat, 0.0)
    rflag = swe.CALC_RISE | swe.BIT_DISC_CENTER
    res = swe.rise_trans(jd_midnight_ut, swe.SUN, rsmi=rflag, geopos=geopos, flags=FLAG)
    if res[0] < 0:
        return jd_midnight_ut + 0.25
    return res[1][0]

def tithi_details(jd_ut):
    sun_lon, moon_lon = sun_moon_lon(jd_ut)
    diff = (moon_lon - sun_lon) % 360.0
    tithi_abs = int(diff // 12) + 1
    if tithi_abs <= 15:
        paksha = "Shukla"
        tithi_in_paksha = tithi_abs
    else:
        paksha = "Krishna"
        tithi_in_paksha = tithi_abs - 15
    karana_num = int(diff // 6) + 1
    return {
        "sun_lon": sun_lon,
        "moon_lon": moon_lon,
        "tithi_abs": tithi_abs,
        "paksha": paksha,
        "tithi": tithi_in_paksha,
        "karana_num": karana_num,
    }

def nakshatra_name(moon_lon):
    seg = 360.0 / 27.0
    idx = int(moon_lon // seg) % 27
    return NAKSHATRAS[idx]

def yoga_name(sun_lon, moon_lon):
    seg = 360.0 / 27.0
    idx = int(((sun_lon + moon_lon) % 360.0) // seg) % 27
    return YOGAS[idx]

def karana_name(karana_num):
    if karana_num in KARANA_FIXED:
        return KARANA_FIXED[karana_num]
    return KARANA_MOVABLE[(karana_num - 2) % 7]

def rashi_of_sun(sun_lon):
    return int(sun_lon // 30) % 12

def jd_of_next_new_moon(jd_start_ut):
    step = 0.25 
    jd = jd_start_ut
    sun0, moon0 = sun_moon_lon(jd)
    prev_diff = (moon0 - sun0) % 360.0
    for _ in range(400):
        jd_next = jd + step
        sun1, moon1 = sun_moon_lon(jd_next)
        diff = (moon1 - sun1) % 360.0
        if prev_diff > 300 and diff < 60:
            lo, hi = jd, jd_next
            for _ in range(40):
                mid = (lo + hi) / 2
                s, m = sun_moon_lon(mid)
                d = (m - s) % 360.0
                if d > 300:
                    lo = mid
                else:
                    hi = mid
            return hi
        prev_diff = diff
        jd = jd_next
    raise RuntimeError("New moon not found in search window")

def amanta_month_for_date(jd_ut):
    nm_jd = jd_of_next_new_moon(jd_ut)
    sun_lon, _ = sun_moon_lon(nm_jd)
    rashi = rashi_of_sun(sun_lon)
    return RASHI_TO_MONTH[rashi]

def festival_for(amanta_month, paksha, tithi_in_paksha):
    notes = []
    key = (amanta_month, paksha, tithi_in_paksha)
    if key in FESTIVALS:
        notes.append(FESTIVALS[key])
    if tithi_in_paksha == 11:
        notes.append("Ekadashi (fasting day)")
    if tithi_in_paksha == 15:
        notes.append("Purnima (Full Moon)" if paksha == "Shukla" else "Amavasya (New Moon)")
    return notes

def build_calendar(year, month, lat, lon, tz_offset_hours, place_name):
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    first_day = datetime(year, month, 1)
    if month == 12:
        next_month_first = datetime(year + 1, 1, 1)
    else:
        next_month_first = datetime(year, month + 1, 1)
    num_days = (next_month_first - first_day).days

    rows = []
    day = first_day
    prev_rashi = None
    for _ in range(num_days):
        jd_midnight_local_as_ut = swe.julday(day.year, day.month, day.day, 0.0) - tz_offset_hours / 24.0
        jd_sunrise = local_sunrise_jd(jd_midnight_local_as_ut, lat, lon)

        td = tithi_details(jd_sunrise)
        nak = nakshatra_name(td["moon_lon"])
        yg = yoga_name(td["sun_lon"], td["moon_lon"])
        kn = karana_name(td["karana_num"])
        amanta = amanta_month_for_date(jd_sunrise)
        purnimanta = purnimanta_name(amanta, td["paksha"])
        rashi_idx = rashi_of_sun(td["sun_lon"])
        rashi = RASHI_NAMES[rashi_idx]

        sankranti_note = None
        if prev_rashi is not None and rashi_idx != prev_rashi:
            sankranti_note = f"{rashi} Sankranti (Sun enters {rashi})"
        prev_rashi = rashi_idx

        festivals = festival_for(amanta, td["paksha"], td["tithi"])
        if sankranti_note:
            festivals.append(sankranti_note)

        weekday = WEEKDAY_NAMES[day.weekday()]

        rows.append({
            "date": day,
            "weekday": weekday,
            "amanta_month": amanta,
            "purnimanta_month": purnimanta,
            "paksha": td["paksha"],
            "tithi": td["tithi"],
            "nakshatra": nak,
            "yoga": yg,
            "karana": kn,
            "rashi": rashi,
            "festivals": festivals,
        })
        day += timedelta(days=1)

    return rows
