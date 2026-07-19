"""
Divisional chart calculations (Varga charts) D1 through D60.
Returns the sign index (0-11) for each planet in each divisional chart.
"""

def get_sign_idx(longitude):
    return int(longitude / 30) % 12

def get_deg_in_sign(longitude):
    return longitude % 30

def d1(longitude):
    """D1 - Rasi (Birth chart)."""
    return get_sign_idx(longitude)

def d2(longitude):
    """D2 - Hora. Wealth chart."""
    sign = get_sign_idx(longitude)
    deg = get_deg_in_sign(longitude)
    is_odd = sign % 2 == 0  # 0-based: 0=Aries(odd), 1=Taurus(even)
    if is_odd:
        return 4 if deg < 15 else 3  # Leo (4) or Cancer (3)
    else:
        return 3 if deg < 15 else 4  # Cancer (3) or Leo (4)

def d3(longitude):
    """D3 - Drekkana. Siblings chart."""
    sign = get_sign_idx(longitude)
    deg = get_deg_in_sign(longitude)
    if deg < 10:
        return sign
    elif deg < 20:
        return (sign + 4) % 12
    else:
        return (sign + 8) % 12

def d4(longitude):
    """D4 - Chaturthamsha. Home/property chart."""
    sign = get_sign_idx(longitude)
    deg = get_deg_in_sign(longitude)
    quarter = int(deg / 7.5)  # 0-3
    return (sign + quarter * 3) % 12

def d7(longitude):
    """D7 - Saptamsha. Children chart."""
    sign = get_sign_idx(longitude)
    deg = get_deg_in_sign(longitude)
    part = int(deg / (30/7))  # 0-6
    if sign % 2 == 0:  # Odd sign (0-based: 0,2,4,6,8,10)
        return (sign + part) % 12
    else:
        return (sign + 6 + part) % 12

def d9(longitude):
    """D9 - Navamsha. Marriage/inner chart."""
    # Each sign has 9 parts of 3°20' each
    nav_num = int(longitude / (360/108))  # 0-107
    fire = [0, 4, 8]  # Aries, Leo, Sag
    earth = [1, 5, 9]
    air = [2, 6, 10]
    water = [3, 7, 11]
    sign = int(longitude / 30) % 12
    if sign in fire:
        start = 0  # Aries
    elif sign in earth:
        start = 9  # Capricorn
    elif sign in air:
        start = 6  # Libra
    else:
        start = 3  # Cancer
    part = int((longitude % 30) / (30/9))
    return (start + part) % 12

def d10(longitude):
    """D10 - Dashamsha. Career chart."""
    sign = get_sign_idx(longitude)
    deg = get_deg_in_sign(longitude)
    part = int(deg / 3)  # 0-9
    if sign % 2 == 0:
        return (sign + part) % 12
    else:
        return (sign + 9 - part) % 12

def d12(longitude):
    """D12 - Dwadashamsha. Parents chart."""
    sign = get_sign_idx(longitude)
    deg = get_deg_in_sign(longitude)
    part = int(deg / 2.5)  # 0-11
    return (sign + part) % 12

def d16(longitude):
    """D16 - Shodashamsha. Vehicles/comforts chart."""
    sign = get_sign_idx(longitude)
    deg = get_deg_in_sign(longitude)
    part = int(deg / (30/16))  # 0-15
    movable = [0, 3, 6, 9]
    fixed = [1, 4, 7, 10]
    # dual = [2, 5, 8, 11]
    if sign in movable:
        start = 0  # Aries
    elif sign in fixed:
        start = 4  # Leo
    else:
        start = 8  # Sagittarius
    return (start + part) % 12

def d20(longitude):
    """D20 - Vimshamsha. Devotion/spiritual chart."""
    sign = get_sign_idx(longitude)
    deg = get_deg_in_sign(longitude)
    part = int(deg / 1.5)  # 0-19
    movable = [0, 3, 6, 9]
    fixed = [1, 4, 7, 10]
    if sign in movable:
        start = 0  # Aries
    elif sign in fixed:
        start = 8  # Sagittarius
    else:
        start = 4  # Leo
    return (start + part) % 12

def d24(longitude):
    """D24 - Chaturvimshamsha. Education chart."""
    sign = get_sign_idx(longitude)
    deg = get_deg_in_sign(longitude)
    part = int(deg / (30/24))  # 0-23
    if sign % 2 == 0:
        start = 4  # Leo
    else:
        start = 3  # Cancer
    return (start + part) % 12

def d27(longitude):
    """D27 - Saptavimshamsha. Strength/stamina chart."""
    sign = get_sign_idx(longitude)
    deg = get_deg_in_sign(longitude)
    part = int(deg / (30/27))  # 0-26
    fire = [0, 4, 8]
    earth = [1, 5, 9]
    air = [2, 6, 10]
    if sign in fire:
        start = 0  # Aries
    elif sign in earth:
        start = 3  # Cancer
    elif sign in air:
        start = 6  # Libra
    else:
        start = 9  # Capricorn
    return (start + part) % 12

def d30(longitude):
    """D30 - Trimshamsha. Misfortune/disease chart."""
    sign = get_sign_idx(longitude)
    deg = get_deg_in_sign(longitude)
    # Odd signs: Mars 0-5, Saturn 5-10, Jupiter 10-18, Mercury 18-25, Venus 25-30
    # Even signs: Venus 0-5, Mercury 5-12, Jupiter 12-20, Saturn 20-25, Mars 25-30
    odd_lords = [(5,"Mars"),(10,"Saturn"),(18,"Jupiter"),(25,"Mercury"),(30,"Venus")]
    even_lords = [(5,"Venus"),(12,"Mercury"),(20,"Jupiter"),(25,"Saturn"),(30,"Mars")]
    lord_sign_map = {"Mars":0,"Venus":1,"Mercury":2,"Jupiter":3,"Saturn":4}  # simplified
    if sign % 2 == 0:  # odd sign
        lords = odd_lords
    else:
        lords = even_lords
    lord_name = lords[-1][1]
    for limit, lname in lords:
        if deg < limit:
            lord_name = lname
            break
    # Return a sign based on the lord
    return (sign + lord_sign_map.get(lord_name, 0) * 3) % 12

def d40(longitude):
    """D40 - Khavedamsha. Auspicious/inauspicious effects."""
    sign = get_sign_idx(longitude)
    deg = get_deg_in_sign(longitude)
    part = int(deg / 0.75)  # 0-39
    if sign % 2 == 0:
        start = 0  # Aries
    else:
        start = 6  # Libra
    return (start + part) % 12

def d45(longitude):
    """D45 - Akshavedamsha. Ethics/morals chart."""
    sign = get_sign_idx(longitude)
    deg = get_deg_in_sign(longitude)
    part = int(deg / (30/45))  # 0-44
    movable = [0, 3, 6, 9]
    fixed = [1, 4, 7, 10]
    if sign in movable:
        start = 0  # Aries
    elif sign in fixed:
        start = 4  # Leo
    else:
        start = 8  # Sagittarius
    return (start + part) % 12

def d60(longitude):
    """D60 - Shashtyamsha. Past karma chart."""
    sign = get_sign_idx(longitude)
    deg = get_deg_in_sign(longitude)
    part = int(deg / 0.5)  # 0-59
    return (sign * 5 + part) % 12  # Simplified

VARGA_FUNCS = {
    "D1": d1, "D2": d2, "D3": d3, "D4": d4, "D7": d7, "D9": d9,
    "D10": d10, "D12": d12, "D16": d16, "D20": d20, "D24": d24,
    "D27": d27, "D30": d30, "D40": d40, "D45": d45, "D60": d60,
}

VARGA_NAMES = {
    "D1": "Lagna Chart (D-1)", "D2": "Hora Chart (D-2)", "D3": "Drekkana Chart (D-3)",
    "D4": "Chaturthamsha Chart (D-4)", "D7": "Saptamsha Chart (D-7)",
    "D9": "Navamsha Chart (D-9)", "D10": "Dashamsha Chart (D-10)",
    "D12": "Dwadashamsha Chart (D-12)", "D16": "Shodashamsha Chart (D-16)",
    "D20": "Vimshamsha Chart (D-20)", "D24": "Chaturvimshamsha Chart (D-24)",
    "D27": "Saptavimshamsha Chart (D-27)", "D30": "Trimshamsha Chart (D-30)",
    "D40": "Khavedamsha Chart (D-40)", "D45": "Akshavedamsha Chart (D-45)",
    "D60": "Shashtyamsha Chart (D-60)",
}

VARGA_MEANING = {
    "D1": "The Lagna Kundali shows overall life, health, career, marriage and family.",
    "D2": "The Hora Kundali indicates wealth, resources and money flow.",
    "D3": "The Drekkana Chart shows siblings, courage, effort and vitality.",
    "D4": "The Chaturthamsha Chart shows home, peace, property and happiness.",
    "D7": "The Saptamsha Chart shows children, creativity and progeny prospects.",
    "D9": "The Navamsha Kundali shows marriage, fortune and inner chart strength.",
    "D10": "The Dashamsha Chart shows career, status, skills and profession.",
    "D12": "The Dwadashamsha Chart shows parents, lineage and past karma.",
    "D16": "The Shodashamsha Chart shows vehicles, comforts, property and happiness.",
    "D20": "The Vimshamsha Chart shows devotion, worship and spiritual growth.",
    "D24": "The Chaturvimshamsha Chart shows education, learning and wisdom.",
    "D27": "The Saptavimshamsha Chart shows strength, stamina and resilience.",
    "D30": "The Trimshamsha Chart shows misfortune, disease and hidden troubles.",
    "D40": "The Khavedamsha Chart shows subtle auspicious and inauspicious effects.",
    "D45": "The Akshavedamsha Chart shows ethics, morals and refined tendencies.",
    "D60": "The Shashtyamsha Chart shows past karma and very subtle life results.",
}

def calc_all_vargas(planets_data, ascendant_data):
    """
    Calculate sign positions in all 16 divisional charts for all planets + Ascendant.
    Returns: dict[varga_key][planet_name] = sign_idx (0-11)
    """
    planet_list = ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

    longitudes = {}
    for p in planet_list:
        if p == "Ascendant":
            longitudes[p] = ascendant_data["longitude"]
        else:
            longitudes[p] = planets_data[p]["longitude"]

    result = {}
    for varga_key, func in VARGA_FUNCS.items():
        result[varga_key] = {}
        for p in planet_list:
            result[varga_key][p] = func(longitudes[p])

    return result
