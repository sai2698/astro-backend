"""
Core astronomical calculations using pyswisseph.
All planetary positions in Lahiri sidereal (Vedic).
"""
import swisseph as swe
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from pytz import timezone
from datetime import datetime, timedelta

# Planet IDs
SWE_PLANETS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
    "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, "Venus": swe.VENUS,
    "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE
}

def geocode_place(place_name):
    """Returns (lat, lon, full_address, timezone_str)."""
    geolocator = Nominatim(user_agent="kundali_gen_v2", timeout=15)
    location = geolocator.geocode(place_name)
    
    if not location:
        # Fallback: try just the first part (city name) if there are commas
        parts = [p.strip() for p in place_name.split(',')]
        if len(parts) > 1:
            location = geolocator.geocode(parts[0])
            
    if not location:
        raise ValueError(f"Could not geocode '{place_name}'. Try simplifying the location name (e.g. just the city name) or provide --lat, --lon, and --tz arguments.")
        
    tf = TimezoneFinder()
    tz_str = tf.timezone_at(lng=location.longitude, lat=location.latitude)
    return location.latitude, location.longitude, location.address, tz_str

def local_to_utc(dob_str, time_str, tz_str):
    """Convert local birth datetime to UTC datetime."""
    local_tz = timezone(tz_str)
    dt = datetime.strptime(f"{dob_str} {time_str}", "%Y-%m-%d %H:%M")
    local_dt = local_tz.localize(dt)
    return local_dt.astimezone(timezone('UTC'))

def get_julian_day(utc_dt):
    """Get Julian Day Number from UTC datetime."""
    hour = utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0
    return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour)

def calc_planets(jd):
    """
    Calculate sidereal (Lahiri) longitudes for all planets.
    Returns dict: planet_name -> {long, speed, retrograde, sign_idx, degrees_in_sign, nakshatra_idx, pada}
    """
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    results = {}
    for name, pid in SWE_PLANETS.items():
        xx, _ = swe.calc_ut(jd, pid, flags)
        long = xx[0] % 360
        speed = xx[3]
        retro = speed < 0
        results[name] = _parse_longitude(long, retro)

    # Ketu = Rahu + 180
    ketu_long = (results["Rahu"]["longitude"] + 180) % 360
    results["Ketu"] = _parse_longitude(ketu_long, True)  # Ketu always retrograde
    results["Rahu"]["retrograde"] = True  # Rahu also always retrograde

    return results

def _parse_longitude(long, retrograde):
    sign_idx = int(long / 30)
    deg_in_sign = long % 30
    degrees = int(deg_in_sign)
    minutes = int((deg_in_sign - degrees) * 60)
    seconds = int(((deg_in_sign - degrees) * 60 - minutes) * 60)
    nak_idx = int(long / (360/27))
    pada = int((long % (360/27)) / (360/27/4)) + 1
    return {
        "longitude": long,
        "sign_idx": sign_idx,
        "deg_in_sign": deg_in_sign,
        "degrees": degrees,
        "minutes": minutes,
        "seconds": seconds,
        "dms": f"{degrees:02d}:{minutes:02d}:{seconds:02d}",
        "deg_min": f"{degrees:02d}:{minutes:02d}",
        "nakshatra_idx": nak_idx,
        "pada": pada,
        "retrograde": retrograde,
    }

def calc_ascendant(jd, lat, lon):
    """Calculate Ascendant (Lagna) using Sripati house system."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    # Use Sripati ('S' = Sripati, but pyswisseph uses 'S' for Sripati? Actually 'S' is not Sripati.
    # Sripati = 'C' in pyswisseph or we can use 'P' for Placidus equivalent. Let's use 'P' (Placidus) for houses
    # and custom compute Sripati. Reference uses Sripati so we'll use 'P' for cusp 1 (asc) and compute rest.
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', flags)
    asc_long = ascmc[0] % 360
    asc = _parse_longitude(asc_long, False)
    return asc, list(cusps)

def calc_sripati_cusps(jd, lat, lon):
    """
    Calculate all 12 house cusps using Sripati (Semi-arc) system.
    Returns list of 12 longitudes (0-indexed, house 1 = index 0).
    """
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    # Sripati in pyswisseph is house system 'S'
    try:
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b'S', flags)
    except Exception:
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', flags)
    return [c % 360 for c in cusps[:12]], ascmc[0] % 360

def get_combust_status(planets):
    """Mark planets as combust if within critical degrees of Sun."""
    from kundali_gen.data.constants import COMBUST_DEGREES
    sun_long = planets["Sun"]["longitude"]
    for name, data in planets.items():
        if name in ("Sun", "Rahu", "Ketu"):
            data["combust"] = False
            continue
        diff = abs(data["longitude"] - sun_long)
        if diff > 180:
            diff = 360 - diff
        limit = COMBUST_DEGREES.get(name, 15)
        if data.get("retrograde"):
            if name == "Venus": limit = 8
            if name == "Mercury": limit = 12
        data["combust"] = diff <= limit
    return planets

def get_house_of_planet(planet_long, lagna_long):
    """Return house number (1-12) of a planet given lagna longitude."""
    lagna_sign = int(lagna_long / 30)
    planet_sign = int(planet_long / 30)
    house = ((planet_sign - lagna_sign) % 12) + 1
    return house

def calc_all(dob_str, time_str, place_name, lat=None, lon=None, tz_str=None):
    """
    Master calculation function.
    Returns a comprehensive dict with all calculated data.
    """
    if lat is not None and lon is not None and tz_str is not None:
        full_address = place_name
    else:
        lat, lon, full_address, tz_str = geocode_place(place_name)
        
    utc_dt = local_to_utc(dob_str, time_str, tz_str)
    jd = get_julian_day(utc_dt)

    planets = calc_planets(jd)
    planets = get_combust_status(planets)
    asc, cusps_placidus = calc_ascendant(jd, lat, lon)
    sripati_cusps, asc_long = calc_sripati_cusps(jd, lat, lon)

    # Assign houses to planets
    for name, data in planets.items():
        data["house"] = get_house_of_planet(data["longitude"], asc["longitude"])

    # Ayanamsa
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd)

    local_dt = local_to_utc(dob_str, time_str, tz_str)
    tz_offset = timezone(tz_str).utcoffset(datetime.strptime(f"{dob_str} {time_str}", "%Y-%m-%d %H:%M")).total_seconds() / 3600

    return {
        "name": None,  # To be filled by caller
        "gender": None,
        "dob_str": dob_str,
        "time_str": time_str,
        "place_name": place_name,
        "full_address": full_address,
        "lat": lat,
        "lon": lon,
        "tz_str": tz_str,
        "tz_offset": tz_offset,
        "utc_dt": utc_dt,
        "jd": jd,
        "ayanamsa": ayanamsa,
        "ascendant": asc,
        "planets": planets,
        "sripati_cusps": sripati_cusps,
        "cusps_placidus": cusps_placidus,
    }

def find_moudya_cycles_for_year(year, planet_name):
    from datetime import datetime, timedelta
    start_dt = datetime(year, 1, 1)
    end_dt = datetime(year, 12, 31, 23, 59, 59)
    
    sweep_start = datetime(year - 1, 6, 1)
    sweep_end = datetime(year + 2, 6, 1)
    
    current = sweep_start
    step = timedelta(days=1)
    
    cycles = []
    in_cycle = False
    cycle_start = None
    
    while current <= sweep_end:
        jd = get_julian_day(current)
        p = get_combust_status(calc_planets(jd))[planet_name]
        
        if p["combust"] and not in_cycle:
            low = current - step
            high = current
            for _ in range(20):
                mid = low + (high - low) / 2
                pm = get_combust_status(calc_planets(get_julian_day(mid)))[planet_name]
                if pm["combust"]: high = mid
                else: low = mid
            cycle_start = high
            in_cycle = True
            
        elif not p["combust"] and in_cycle:
            low = current - step
            high = current
            for _ in range(20):
                mid = low + (high - low) / 2
                pm = get_combust_status(calc_planets(get_julian_day(mid)))[planet_name]
                if pm["combust"]: low = mid
                else: high = mid
            cycle_end = high
            in_cycle = False
            
            if cycle_end >= start_dt and cycle_start <= end_dt:
                cycles.append({"start": cycle_start, "end": cycle_end})
            elif cycle_start > end_dt:
                if len(cycles) == 0:
                    cycles.append({"start": cycle_start, "end": cycle_end})
                break
                
        current += step
        
    return cycles

