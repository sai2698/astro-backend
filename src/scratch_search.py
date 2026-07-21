from datetime import datetime, timedelta
import swisseph as swe
import sys
sys.path.append('.')
from kundali_gen.core.astro_calc import get_julian_day, calc_planets, get_combust_status

def find_moudya_cycle(start_utc, planet_name, max_days=1000):
    current_dt = start_utc
    jd = get_julian_day(current_dt)
    planets = calc_planets(jd)
    planets = get_combust_status(planets)
    
    is_currently_combust = planets[planet_name]["combust"]
    
    start_moudya = None
    end_moudya = None
    
    if is_currently_combust:
        # Find when it started (sweep back)
        step = timedelta(days=1)
        temp_dt = current_dt
        while True:
            temp_dt -= step
            jd = get_julian_day(temp_dt)
            p = get_combust_status(calc_planets(jd))[planet_name]
            if not p["combust"]:
                break
        
        # Binary search for exact start
        low = temp_dt
        high = temp_dt + step
        for _ in range(20):
            mid = low + (high - low) / 2
            p = get_combust_status(calc_planets(get_julian_day(mid)))[planet_name]
            if p["combust"]:
                high = mid
            else:
                low = mid
        start_moudya = high
        
        # Find when it ends (sweep forward)
        temp_dt = current_dt
        while True:
            temp_dt += step
            jd = get_julian_day(temp_dt)
            p = get_combust_status(calc_planets(jd))[planet_name]
            if not p["combust"]:
                break
                
        low = temp_dt - step
        high = temp_dt
        for _ in range(20):
            mid = low + (high - low) / 2
            p = get_combust_status(calc_planets(get_julian_day(mid)))[planet_name]
            if p["combust"]:
                low = mid
            else:
                high = mid
        end_moudya = high
        
    else:
        # Sweep forward to find next start
        step = timedelta(days=1)
        temp_dt = current_dt
        for _ in range(max_days):
            temp_dt += step
            jd = get_julian_day(temp_dt)
            p = get_combust_status(calc_planets(jd))[planet_name]
            if p["combust"]:
                break
                
        # Binary search for exact start
        low = temp_dt - step
        high = temp_dt
        for _ in range(20):
            mid = low + (high - low) / 2
            p = get_combust_status(calc_planets(get_julian_day(mid)))[planet_name]
            if p["combust"]:
                high = mid
            else:
                low = mid
        start_moudya = high
        
        # Now find end
        temp_dt = start_moudya
        for _ in range(300):
            temp_dt += step
            jd = get_julian_day(temp_dt)
            p = get_combust_status(calc_planets(jd))[planet_name]
            if not p["combust"]:
                break
                
        low = temp_dt - step
        high = temp_dt
        for _ in range(20):
            mid = low + (high - low) / 2
            p = get_combust_status(calc_planets(get_julian_day(mid)))[planet_name]
            if p["combust"]:
                low = mid
            else:
                high = mid
        end_moudya = high

    return start_moudya, end_moudya

now = datetime(2026, 1, 1) # Test for 2026
for p in ["Jupiter", "Venus", "Saturn", "Mars", "Mercury"]:
    s, e = find_moudya_cycle(now, p)
    print(f"{p}: Starts {s}, Ends {e}")

