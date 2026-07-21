import sys
sys.path.append('.')
from datetime import datetime, timedelta
from kundali_gen.core.astro_calc import get_julian_day, calc_planets

def get_combust_status_custom(planets):
    sun_long = planets["Sun"]["longitude"]
    limits = {"Moon": 12, "Mars": 17, "Mercury": 14, "Jupiter": 11, "Venus": 10, "Saturn": 15}
    for name, data in planets.items():
        if name in ("Sun", "Rahu", "Ketu"):
            data["combust"] = False
            continue
        diff = abs(data["longitude"] - sun_long)
        if diff > 180:
            diff = 360 - diff
        limit = limits.get(name, 15)
        if data.get("retrograde"):
            if name == "Venus": limit = 8
            if name == "Mercury": limit = 12
        data["combust"] = diff <= limit
    return planets

def find_moudya_cycles_for_year(year, planet_name):
    start_dt = datetime(year, 1, 1)
    end_dt = datetime(year, 12, 31, 23, 59, 59)
    
    # We also want cycles that started before Jan 1 but end after Jan 1.
    # To find those, we can start sweeping from 400 days before Jan 1 (Mars can be combust for a long time, maybe 4-5 months max? 400 days is safe)
    # Actually, if we just step day by day from (year-1) mid year to (year+2)
    # That's 1000 days.
    
    sweep_start = datetime(year - 1, 6, 1)
    sweep_end = datetime(year + 2, 6, 1) # sweep ahead 2 years just in case
    
    current = sweep_start
    step = timedelta(days=1)
    
    cycles = []
    in_cycle = False
    cycle_start = None
    
    while current <= sweep_end:
        jd = get_julian_day(current)
        p = get_combust_status_custom(calc_planets(jd))[planet_name]
        
        if p["combust"] and not in_cycle:
            # Found a start! Let's binary search backwards to find exact start
            low = current - step
            high = current
            for _ in range(20):
                mid = low + (high - low) / 2
                pm = get_combust_status_custom(calc_planets(get_julian_day(mid)))[planet_name]
                if pm["combust"]: high = mid
                else: low = mid
            cycle_start = high
            in_cycle = True
            
        elif not p["combust"] and in_cycle:
            # Found an end! Binary search
            low = current - step
            high = current
            for _ in range(20):
                mid = low + (high - low) / 2
                pm = get_combust_status_custom(calc_planets(get_julian_day(mid)))[planet_name]
                if pm["combust"]: low = mid
                else: high = mid
            cycle_end = high
            in_cycle = False
            
            # Check if this cycle overlaps with the target year
            if cycle_end >= start_dt and cycle_start <= end_dt:
                cycles.append({"start": cycle_start, "end": cycle_end})
            elif cycle_start > end_dt:
                # If we've already passed the target year and found no cycles for the target year
                # we keep this one as the "upcoming" one and break!
                if len(cycles) == 0:
                    cycles.append({"start": cycle_start, "end": cycle_end})
                break
                
        current += step
        
    return cycles

print("Jupiter 2026:")
for c in find_moudya_cycles_for_year(2026, "Jupiter"): print(c)
print("\nVenus 2026:")
for c in find_moudya_cycles_for_year(2026, "Venus"): print(c)
print("\nMars 2026:")
for c in find_moudya_cycles_for_year(2026, "Mars"): print(c)
print("\nMercury 2026:")
for c in find_moudya_cycles_for_year(2026, "Mercury"): print(c)
