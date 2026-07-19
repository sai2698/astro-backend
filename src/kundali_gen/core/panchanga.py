"""
Panchanga calculations: Sunrise/Sunset, Tithi, Nakshatra, Yoga, Karana, Hindu Calendar.
"""
import swisseph as swe
from datetime import datetime, timedelta
from kundali_gen.data.constants import (
    TITHI_NAMES, YOGA_NAMES, KARANA_NAMES, HINDU_MONTHS,
    AYANA, RITU_NAMES, HINDU_YEAR_NAMES, NAKSHATRAS, NAKSHATRA_NADI_NAME,
    NAKSHATRA_GANA, NAKSHATRA_YONI, SIGN_LORD, SIGNS
)

def get_sunrise_sunset(jd, lat, lon):
    """Returns (sunrise_jd, sunset_jd) as Julian Day numbers."""
    try:
        ret_rise, t_rise = swe.rise_trans(jd - 1, swe.SUN, lon, lat, 0, 0, 0, swe.CALC_RISE)
        ret_set, t_set = swe.rise_trans(jd - 1, swe.SUN, lon, lat, 0, 0, 0, swe.CALC_SET)
        return t_rise[0], t_set[0]
    except Exception:
        return jd + 0.25, jd + 0.75  # fallback: 6am/6pm

def jd_to_time_str(jd):
    """Convert Julian Day to HH:MM:SS string."""
    ut = swe.jdut1_to_utc(jd, 1)
    return f"{int(ut[3]):02d}:{int(ut[4]):02d}:{int(ut[5]):02d}"

def jd_to_duration_str(diff_jd):
    """Convert Julian Day difference to HH:MM:SS."""
    total_sec = round(diff_jd * 86400)
    h = total_sec // 3600
    m = (total_sec % 3600) // 60
    s = total_sec % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def calc_tithi(sun_long, moon_long):
    """Returns (tithi_number 1-30, paksha 'Shukla'/'Krishna', tithi_name)."""
    diff = (moon_long - sun_long) % 360
    tithi_num = int(diff / 12) + 1  # 1-30
    if tithi_num <= 15:
        paksha = "Shukla"
        name = TITHI_NAMES[tithi_num - 1]
    else:
        paksha = "Krishna"
        name = TITHI_NAMES[tithi_num - 16]
    return tithi_num, paksha, f"{paksha}-{name}"

def calc_yoga(sun_long, moon_long):
    """Returns yoga index (0-26) and name."""
    combined = (sun_long + moon_long) % 360
    idx = int(combined / (360 / 27))
    return idx, YOGA_NAMES[idx]

def calc_karana(sun_long, moon_long):
    """Returns karana name."""
    diff = (moon_long - sun_long) % 360
    karana_num = int(diff / 6)  # 0-59
    fixed_karanas = {0: "Kimstughna", 57: "Shakuni", 58: "Chatushpada", 59: "Naga"}
    if karana_num in fixed_karanas:
        return fixed_karanas[karana_num]
    movable_idx = (karana_num - 1) % 7
    movable = ["Bava", "Balava", "Kaulava", "Taitula", "Gara", "Vanija", "Vishti"]
    return movable[movable_idx]

def calc_nakshatra(moon_long):
    """Returns (nakshatra_idx 0-26, pada 1-4, name, lord, pada_str)."""
    nak_span = 360 / 27
    idx = int(moon_long / nak_span)
    pos_in_nak = moon_long % nak_span
    pada = int(pos_in_nak / (nak_span / 4)) + 1
    nak = NAKSHATRAS[idx]
    return idx, pada, nak["name"], nak["lord"], f"{nak['name']}-{pada}"

def calc_moon_sign(moon_long):
    sign_idx = int(moon_long / 30)
    return sign_idx, SIGNS[sign_idx]

def calc_hindu_year(utc_dt):
    """Returns Kali Year, Saka Year, Hindu Year name."""
    year = utc_dt.year
    kali = year + 3101
    saka = year - 78
    jovian_idx = (year - 1987) % 60  # Vishvavasu = 1987 base
    hindu_year = HINDU_YEAR_NAMES[jovian_idx % 60]
    return kali, saka, hindu_year

def calc_ayana(sun_long):
    """Returns Ayana string."""
    # Uttarayana: Capricorn to Gemini (270-90°), Dakshinayana: Cancer to Sagittarius
    if 270 <= sun_long < 360 or 0 <= sun_long < 90:
        return "Uttarayana"
    return "Dakshinayana"

def calc_ritu(sun_long):
    """Returns season (Ritu) name based on Sun's sign."""
    sign_idx = int(sun_long / 30)
    # Pairs of signs: (0,1)=Vasanta, (2,3)=Grishma, (4,5)=Varsha, (6,7)=Sharad, (8,9)=Hemanta, (10,11)=Shishira
    ritu_map = {0:"Vasanta Ritu",1:"Vasanta Ritu",2:"Grishma Ritu",3:"Grishma Ritu",
                4:"Varsha Ritu",5:"Varsha Ritu",6:"Sharad Ritu",7:"Sharad Ritu",
                8:"Hemanta Ritu",9:"Hemanta Ritu",10:"Shishira Ritu",11:"Shishira Ritu"}
    return ritu_map[sign_idx]

def calc_hindu_month(sun_long):
    """Returns Hindu month name based on Sun's sign."""
    sun_sign = int(sun_long / 30)
    # Month starts when Sun enters Aries
    month_map = {0:"Chaitra",1:"Vaishakha",2:"Jyeshtha",3:"Ashadha",
                 4:"Shravana",5:"Bhadrapada",6:"Ashwina",7:"Kartika",
                 8:"Margashirsha",9:"Pausha",10:"Magha",11:"Phalguna"}
    return month_map[sun_sign]

def calc_weekday(utc_dt, tz_offset):
    """Returns English weekday and Vedic weekday."""
    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    en_day = days[utc_dt.weekday()]
    # Vedic day: starts at sunrise, so before sunrise = previous day
    return en_day, en_day  # simplified; proper vedic needs sunrise check

def calc_janmakshar(moon_long, nakshatra_idx):
    """Returns Janmakshar (first syllable) based on Nakshatra-Pada."""
    # Classical syllables for each nakshatra pada
    syllables = {
        "Ashwini": ["Chu","Che","Cho","La"],
        "Bharani": ["Li","Lu","Le","Lo"],
        "Krittika": ["A","I","U","E"],
        "Rohini": ["O","Va","Vi","Vu"],
        "Mrigashira": ["Ve","Vo","Ka","Ki"],
        "Ardra": ["Ku","Gha","Ing","Ja"],
        "Punarvasu": ["Ki","Ku","Ke","Ko"],  # simplified
        "Pushya": ["Hu","He","Ho","Da"],
        "Ashlesha": ["Di","Du","De","Do"],
        "Magha": ["Ma","Mi","Mu","Me"],
        "Purva Phalguni": ["Mo","Ta","Ti","Tu"],
        "Uttara Phalguni": ["Te","To","Pa","Pi"],
        "Hasta": ["Pu","Sha","Na","Tha"],
        "Chitra": ["Pe","Po","Ra","Ri"],
        "Swati": ["Ru","Re","Ro","Ta"],
        "Vishakha": ["Ti","Tu","Te","To"],
        "Anuradha": ["Na","Ni","Nu","Ne"],
        "Jyeshtha": ["No","Ya","Yi","Yu"],
        "Mula": ["Ye","Yo","Ba","Bi"],
        "Purva Ashadha": ["Bu","Dha","Pha","Da"],
        "Uttara Ashadha": ["Be","Bo","Ja","Ji"],
        "Shravana": ["Khi","Khu","Khe","Kho"],
        "Dhanishtha": ["Ga","Gi","Gu","Ge"],
        "Shatabhisha": ["Go","Sa","Si","Su"],
        "Purva Bhadrapada": ["Se","So","Da","Di"],
        "Uttara Bhadrapada": ["Du","Tha","Ja","Jha"],
        "Revati": ["De","Do","Cha","Chi"],
    }
    nak_name = NAKSHATRAS[nakshatra_idx]["name"]
    padas = syllables.get(nak_name, ["Ka","Ki","Ku","Ke"])
    moon_span = 360 / 27
    pos_in_nak = moon_long % moon_span
    pada = int(pos_in_nak / (moon_span / 4))
    return padas[min(pada, 3)]

def get_full_panchanga(calc_data):
    """
    Given the calc_data dict from astro_calc.calc_all(), compute full Panchanga.
    Returns a panchanga dict.
    """
    jd = calc_data["jd"]
    lat = calc_data["lat"]
    lon = calc_data["lon"]
    utc_dt = calc_data["utc_dt"]
    tz_offset = calc_data["tz_offset"]
    planets = calc_data["planets"]

    sun_long = planets["Sun"]["longitude"]
    moon_long = planets["Moon"]["longitude"]

    sunrise_jd, sunset_jd = get_sunrise_sunset(jd, lat, lon)
    sunrise_str = jd_to_time_str(sunrise_jd)
    sunset_str = jd_to_time_str(sunset_jd)
    day_len = jd_to_duration_str(sunset_jd - sunrise_jd)
    night_len = jd_to_duration_str(1 - (sunset_jd - sunrise_jd))

    tithi_num, paksha, tithi_name = calc_tithi(sun_long, moon_long)
    yoga_idx, yoga_name = calc_yoga(sun_long, moon_long)
    karana_name = calc_karana(sun_long, moon_long)
    nak_idx, pada, nak_name, nak_lord, nak_pada_str = calc_nakshatra(moon_long)
    moon_sign_idx, moon_sign = calc_moon_sign(moon_long)
    kali, saka, hindu_year = calc_hindu_year(utc_dt)
    ayana = calc_ayana(sun_long)
    ritu = calc_ritu(sun_long)
    hindu_month = calc_hindu_month(sun_long)
    en_weekday, vedic_weekday = calc_weekday(utc_dt, tz_offset)
    janmakshar = calc_janmakshar(moon_long, nak_idx)

    # Nadi (middle) based on nakshatra
    nadi_map = {0:"Adya",1:"Madhya",2:"Antya"}
    nadi = nadi_map.get(nak_idx % 3, "Madhya")

    # Gana
    gana = NAKSHATRA_GANA[nak_idx]

    # Yoni
    yoni = NAKSHATRA_YONI[nak_idx]

    # Moon sign lord
    rashi_lord = SIGN_LORD[moon_sign_idx]

    return {
        "sunrise": sunrise_str,
        "sunset": sunset_str,
        "day_length": day_len,
        "night_length": night_len,
        "kali_year": kali,
        "saka_year": saka,
        "hindu_year": hindu_year,
        "ayana": ayana,
        "ritu": ritu,
        "hindu_month": hindu_month,
        "tithi_num": tithi_num,
        "paksha": paksha,
        "tithi": tithi_name,
        "weekday": en_weekday,
        "vedic_weekday": vedic_weekday,
        "nakshatra": nak_name,
        "nakshatra_pada": nak_pada_str,
        "nakshatra_lord": nak_lord,
        "yoga": yoga_name,
        "karana": karana_name,
        "moon_sign": moon_sign,
        "moon_sign_idx": moon_sign_idx,
        "janmakshar": janmakshar,
        "nadi": nadi,
        "gana": gana,
        "yoni": yoni,
        "rashi_lord": rashi_lord,
    }
