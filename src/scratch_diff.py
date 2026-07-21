import sys
sys.path.append('.')
from datetime import datetime
from kundali_gen.core.astro_calc import get_julian_day, calc_planets

def print_distance(dt_str):
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    jd = get_julian_day(dt)
    planets = calc_planets(jd)
    sun = planets["Sun"]["longitude"]
    ven = planets["Venus"]["longitude"]
    diff = abs(sun - ven)
    if diff > 180: diff = 360 - diff
    print(f"Date: {dt_str}, Sun: {sun:.2f}, Venus: {ven:.2f}, Diff: {diff:.3f}, Venus Retro: {planets['Venus']['retrograde']}")

print_distance("2025-11-26 06:21:39") # 11:51:39 IST
print_distance("2026-02-17 09:38:20") # 15:08:20 IST
print_distance("2026-10-19 02:45:39") # 08:15:39 IST
print_distance("2026-10-29 04:09:58") # 09:39:58 IST
