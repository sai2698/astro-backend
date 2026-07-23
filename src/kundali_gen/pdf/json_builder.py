"""JSON builder for Kundali API."""
from kundali_gen.data.constants import (
    SIGNS, SIGN_SHORT, NAKSHATRAS, PLANETS, PLANET_SHORT, BHAVA_NAMES, SIGN_LORD,
    get_lucky_things, STHIRA_KARAKAS, DASHA_ORDER
)
from kundali_gen.core.divisional import VARGA_NAMES, VARGA_MEANING
from kundali_gen.data.translations import t
from kundali_gen.core.dasha import format_dasha_date

def build_json(data, panchanga, planets, ascendant, all_vargas,
               dasha_rows_3, sookshma_1yr, av_data, kaal_sarp, mangal, jaimini_karakas, charttype="full", language="en"):
    
    # Birth Details
    birth_details = {
        "name": data.get("name", ""),
        "gender": t(data.get("gender", ""), language),
        "dob": data.get("dob_display", data.get("dob_str", "")),
        "time": data.get("time_str", ""),
        "place": data.get("full_address", data.get("place_name", "")),
        "lat": data.get('lat', 0),
        "lon": data.get('lon', 0),
        "timezone": f"{data.get('tz_str', '')} ({data.get('tz_offset', '')})"
    }

    # Panchanga
    panchanga_translated = {
        "sunrise": panchanga.get("sunrise", ""),
        "sunset": panchanga.get("sunset", ""),
        "day_length": panchanga.get("day_length", ""),
        "night_length": panchanga.get("night_length", ""),
        "kali_year": panchanga.get("kali_year", ""),
        "saka_year": panchanga.get("saka_year", ""),
        "hindu_year": t(panchanga.get("hindu_year", ""), language),
        "ayana": t(panchanga.get("ayana", ""), language),
        "ritu": t(panchanga.get("ritu", ""), language),
        "hindu_month": t(panchanga.get("hindu_month", ""), language),
        "tithi": t(panchanga.get("tithi", ""), language),
        "weekday": t(panchanga.get("weekday", ""), language),
        "vedic_weekday": t(panchanga.get("vedic_weekday", ""), language),
        "nakshatra_pada": t(panchanga.get("nakshatra_pada", ""), language),
        "moon_sign": f"{t(panchanga.get('moon_sign', ''), language)} {t('Sign', language)}",
        "yoga": t(panchanga.get("yoga", ""), language),
        "karana": t(panchanga.get("karana", ""), language),
        "janmakshar": panchanga.get("janmakshar", "")
    }

    # Planets
    order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Ascendant"]
    planets_translated = []
    for p in order:
        pdata = ascendant if p == "Ascendant" else planets[p]
        if p == "Ascendant":
            rx = "-"
        else:
            r_str = t("(R)", language) if pdata.get("retrograde") else ""
            c_str = t("(C)", language) if pdata.get("combust") else ""
            if r_str and c_str:
                rx = f"{r_str}, {c_str}"
            else:
                rx = r_str or c_str or "-"
        nak_idx = pdata["nakshatra_idx"]
        pada = pdata["pada"]
        nak = NAKSHATRAS[nak_idx]
        nav = pdata.get("nav_sign_idx", (nak_idx * 4 + pada - 1) % 12)
        
        planets_translated.append({
            "planet": p,  # Keep english name for JS logic, we can translate it in JS
            "planet_translated": t(p, language),
            "status": rx,
            "sign": t(SIGNS[pdata["sign_idx"]], language),
            "sign_idx": pdata["sign_idx"],
            "degrees": pdata["dms"],
            "house": str(planets[p].get("house", "-")) if p != "Ascendant" else "-",
            "nakshatra_pada": f"{t(nak['name'], language)}-{pada}",
            "nakshatra_lord": t(nak["lord"], language),
            "navamsha_sign": t(SIGNS[nav], language),
            "navamsha_lord": t(SIGN_LORD[nav], language),
            "nav_sign_idx": nav
        })

    # Bhava
    bhava = []
    for i, cusp in enumerate(data.get("sripati_cusps", [0]*12)[:12]):
        sign_idx = int(cusp / 30) % 12
        deg = cusp % 30
        d = int(deg); m = int((deg - d) * 60); s = int(((deg - d) * 60 - m) * 60)
        bhava.append({
            "house": t(BHAVA_NAMES[i], language),
            "sign": t(SIGNS[sign_idx], language),
            "degrees": f"{d:02d}:{m:02d}:{s:02d}"
        })

    # Dasha
    dasha = []
    for r in dasha_rows_3:
        md_s = PLANET_SHORT[PLANETS.index(r["MD"])] if r["MD"] in PLANETS else r["MD"]
        bh_s = PLANET_SHORT[PLANETS.index(r["BH"])] if r["BH"] in PLANETS else r["BH"]
        pr_s = PLANET_SHORT[PLANETS.index(r["PR"])] if r["PR"] in PLANETS else r["PR"]
        dasha.append({
            "md": t(md_s, language),
            "bh": t(bh_s, language),
            "pr": t(pr_s, language),
            "start_date": format_dasha_date(r["start"]),
            "age": round(r["age"], 1)
        })

    sookshma = []
    if sookshma_1yr:
        for r in sookshma_1yr:
            sookshma.append({
                "md": t(r["MD"], language),
                "bh": t(r["BH"], language),
                "pr": t(r["PR"], language),
                "sd": t(r["SD"], language),
                "start_date": format_dasha_date(r["start"]),
                "age": round(r["age"], 1)
            })

    result = {
        "birth_details": birth_details,
        "panchanga": panchanga_translated,
        "planets": planets_translated,
        "bhava": bhava,
        "dasha": dasha,
        "sookshma": sookshma,
    }

    if charttype == "full":
        # Avakahada
        from kundali_gen.data.constants import SIGN_VARNA, SIGN_VASHYA
        result["avakahada"] = {
            "nakshatra": t(panchanga.get("nakshatra", ""), language),
            "nadi": t(panchanga.get("nadi", ""), language),
            "yoni": t(panchanga.get("yoni", ""), language),
            "gana": t(panchanga.get("gana", ""), language),
            "moon_sign": t(panchanga.get("moon_sign", ""), language),
            "rashi_lord": t(panchanga.get("rashi_lord", ""), language),
            "varna_kuta": t(SIGN_VARNA.get(panchanga.get("moon_sign_idx", 0), ""), language),
            "vashya_kuta": t(SIGN_VASHYA.get(panchanga.get("moon_sign_idx", 0), ""), language)
        }

        # Lucky Things
        lt = get_lucky_things(ascendant["sign_idx"])
        result["lucky_things"] = {
            "days": [t(d, language) for d in lt.get("days", [])],
            "planets": [t(p, language) for p in lt.get("planets", [])],
            "friendly_signs": [t(s, language) for s in lt.get("friendly_signs", [])],
            "friendly_ascendant": [t(a, language) for a in lt.get("friendly_asc", [])],
            "life_stone": t(lt.get("life_stone", ""), language),
            "lucky_stone": t(lt.get("lucky_stone", ""), language),
            "punya_stone": t(lt.get("punya_stone", ""), language),
            "deity": [t(d, language) for d in lt.get("deity", [])],
            "metal": t(lt.get("metal", ""), language),
            "color": [t(c, language) for c in lt.get("color", [])],
            "direction": [t(d, language) for d in lt.get("direction", [])],
            "time": t(lt.get("time", ""), language),
            "numbers": lt.get("numbers", [])
        }

        # Jaimini
        jaimini = []
        for karaka, planet in jaimini_karakas.items():
            p_short = PLANET_SHORT[PLANETS.index(planet)] if planet in PLANETS else planet[:2]
            sthira = STHIRA_KARAKAS.get(planet, "")
            jaimini.append({
                "planet": t(p_short, language),
                "chara_karaka": t(karaka, language),
                "sthira_karaka": t(sthira, language)
            })
        result["jaimini_karakas"] = jaimini

        # Ashtakavarga
        av_translated = {}
        for planet_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            bindus = av_data.get(planet_name, {}).get("bindus", [0] * 12)
            av_translated[t(planet_name, language)] = bindus
        result["ashtakavarga"] = av_translated

        # Doshas
        ks_found, ks_msg = kaal_sarp
        mg_lagna = mangal.get("lagna", {})
        mg_moon = mangal.get("moon", {})
        mg_venus = mangal.get("venus", {})
        result["doshas"] = {
            "kaal_sarp": t(ks_msg, language),
            "mangal_lagna": t(mg_lagna.get("message", ""), language),
            "mangal_moon": t(mg_moon.get("message", ""), language),
            "mangal_venus": t(mg_venus.get("message", ""), language)
        }

    return result
