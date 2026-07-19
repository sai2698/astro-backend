"""
Yoga detection: Kaal Sarp, Mangal Dosha, Nipuna (Budha-Aditya), and multi-planet yogas.
"""
from kundali_gen.data.constants import PLANETS

def check_kaal_sarp(planets):
    """Returns True if all planets are between Rahu and Ketu (Kaal Sarp Dosha)."""
    rahu_long = planets["Rahu"]["longitude"]
    ketu_long = planets["Ketu"]["longitude"]

    # Determine the arc from Rahu to Ketu going clockwise
    def in_arc(p_long, start, end):
        if start < end:
            return start < p_long < end
        else:  # crosses 0
            return p_long > start or p_long < end

    check_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    half_occupied = all(in_arc(planets[p]["longitude"], rahu_long, ketu_long) for p in check_planets)
    other_half = all(in_arc(planets[p]["longitude"], ketu_long, rahu_long) for p in check_planets)

    if half_occupied or other_half:
        return True, "All planets are positioned between Rahu and Ketu."
    return False, "You don't have Kalasarpa dosha in your chart."

def check_mangal_dosha(planets, ascendant_sign_idx):
    """
    Check Mangal Dosha from Lagna, Moon, and Venus.
    Returns dict with results.
    """
    mars_house = planets["Mars"]["house"]
    moon_sign = planets["Moon"]["sign_idx"]
    venus_sign = planets["Venus"]["sign_idx"]

    dosha_houses = [1, 4, 7, 8, 12]
    results = {}

    # From Lagna
    if mars_house in dosha_houses:
        cancelled = False
        cancel_reason = []
        # Cancellation rules
        if ascendant_sign_idx in [0, 7]:  # Aries or Scorpio lagna
            cancelled = True
            cancel_reason.append("Mars is lord of Lagna in Aries/Scorpio, Dosha cancelled.")
        if planets["Jupiter"]["house"] == 1 or planets["Venus"]["house"] == 1:
            cancelled = True
            cancel_reason.append("The presence of Jupiter or Venus in the 1st House cancels the dosha.")
        if planets["Mars"]["combust"]:
            cancelled = True
            cancel_reason.append("Dosha is cancelled because Mars is combust")

        results["lagna"] = {
            "found": True,
            "house": mars_house,
            "cancelled": cancelled,
            "cancel_reasons": cancel_reason,
            "message": f"Mars is in the {mars_house}{'st' if mars_house==1 else 'th'} house from the Ascendant."
        }
    else:
        results["lagna"] = {"found": False, "message": "No Kuja Dosha from the Ascendant."}

    # From Moon (calculate Mars house from Moon sign)
    mars_sign = planets["Mars"]["sign_idx"]
    mars_from_moon = ((mars_sign - moon_sign) % 12) + 1
    if mars_from_moon in dosha_houses:
        results["moon"] = {"found": True, "message": f"Kuja Dosha from Moon exists (Mars in house {mars_from_moon} from Moon)."}
    else:
        results["moon"] = {"found": False, "message": "No Kuja Dosha from the Moon."}

    # From Venus
    mars_from_venus = ((mars_sign - venus_sign) % 12) + 1
    if mars_from_venus in dosha_houses:
        results["venus"] = {"found": True, "message": f"Kuja Dosha from Venus exists."}
    else:
        results["venus"] = {"found": False, "message": "No Kuja Dosha from Venus."}

    return results

def check_nipuna_yoga(planets):
    """Budha-Aditya Yoga: Sun and Mercury in same/adjacent sign."""
    sun_sign = planets["Sun"]["sign_idx"]
    mer_sign = planets["Mercury"]["sign_idx"]
    if sun_sign == mer_sign:
        return True, "You have the Nipuna (Budha-Aditya) yoga — Sun and Mercury together."
    return False, ""

def check_vesi_yoga(planets):
    """Vesi Yoga: Planet in 2nd house from Sun."""
    sun_sign = planets["Sun"]["sign_idx"]
    second_from_sun = (sun_sign + 1) % 12
    vesi_planets = []
    for p in ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        if planets[p]["sign_idx"] == second_from_sun:
            vesi_planets.append(p)
    if vesi_planets:
        return True, vesi_planets
    return False, []

def detect_multi_planet_yogas(planets):
    """Detect Dwi/Tri/Chatur graha yogas."""
    # Group planets by sign
    sign_groups = {}
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        s = planets[p]["sign_idx"]
        if s not in sign_groups:
            sign_groups[s] = []
        sign_groups[s].append(p)

    yogas = []
    for sign, ps in sign_groups.items():
        if len(ps) >= 2:
            yogas.append({"count": len(ps), "planets": ps, "sign": sign})
    return yogas

def get_jaimini_karakas(planets):
    """
    Calculate Jaimini Chara Karakas based on degrees in sign (descending order).
    Returns ordered list: [Atmakaraka, Amatyakaraka, ..., Darakaraka]
    """
    karaka_names = ["Atmakaraka", "Amatyakaraka", "Bhratrukaraka", "Matrukaraka",
                    "Putrakaraka", "Gnatikaraka", "Darakaraka"]
    planet_degs = {}
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        planet_degs[p] = planets[p]["deg_in_sign"]

    sorted_planets = sorted(planet_degs.items(), key=lambda x: x[1], reverse=True)

    result = {}
    for i, (planet, deg) in enumerate(sorted_planets):
        if i < len(karaka_names):
            result[karaka_names[i]] = planet
    return result

def get_jaimini_arudhas(planets, ascendant):
    """
    Calculate Jaimini Arudha Padas for all 12 houses.
    """
    lagna_sign = ascendant["sign_idx"]
    sign_lords = [5, 3, 1, 3, 1, 1, 5, 0, 5, 5, 5, 5]  # Mars=0,Venus=1,Mer=2,Moon=3,Sun=4,Mars/Jupiter=5
    # Simplified: map each house lord to their planet sign and compute Arudha
    from kundali_gen.data.constants import SIGN_LORD, PLANETS

    arudhas = {}
    for house_num in range(1, 13):
        house_sign = (lagna_sign + house_num - 1) % 12
        house_lord_name = SIGN_LORD[house_sign]
        # Find where the lord is placed
        if house_lord_name in planets:
            lord_sign = planets[house_lord_name]["sign_idx"]
        else:
            lord_sign = house_sign  # fallback

        # Arudha = house_sign + (lord_sign - house_sign) + (lord_sign - house_sign) from lord
        diff = (lord_sign - house_sign) % 12
        arudha_sign = (lord_sign + diff) % 12

        # Special rule: if Arudha falls on same sign or 7th from it
        if arudha_sign == house_sign:
            arudha_sign = (house_sign + 9) % 12
        elif arudha_sign == (house_sign + 6) % 12:
            arudha_sign = (house_sign + 3) % 12

        arudha_house = ((arudha_sign - lagna_sign) % 12) + 1
        arudhas[house_num] = arudha_house

    return arudhas

ARUDHA_NAMES = {
    1: "Lagnapada", 2: "Dhanapada", 3: "Vikramapada", 4: "Matrpada / Sukhapada",
    5: "Mantrapada / Putrapada", 6: "Rogapada / Shatrupada", 7: "Darapada / Kalatrapada",
    8: "Maranapada / Mrtyupada", 9: "Pitrpada / Bhagyapada", 10: "Karmapada / Rajyapada",
    11: "Labhapada", 12: "Vyayapada / Upapada"
}
