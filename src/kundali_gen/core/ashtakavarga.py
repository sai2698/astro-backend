"""
Ashtakavarga calculations for all 7 planets + Lagna.
Based on classical Parashari Ashtakavarga bindu positions.
"""

# Classical Ashtakavarga tables: for each planet (source), which houses (from THAT planet's sign) get a bindu
# Values are house numbers (1-indexed) from the SOURCE planet's position
AV_TABLES = {
    "Sun": {
        "Sun":    [1, 2, 4, 7, 8, 9, 10, 11],
        "Moon":   [3, 6, 10, 11],
        "Mars":   [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury":[3, 5, 6, 9, 10, 11, 12],
        "Jupiter":[5, 6, 9, 11],
        "Venus":  [6, 7, 12],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna":  [3, 4, 6, 10, 11, 12],
    },
    "Moon": {
        "Sun":    [3, 6, 7, 8, 10, 11],
        "Moon":   [1, 3, 6, 7, 10, 11],
        "Mars":   [2, 3, 5, 6, 9, 10, 11],
        "Mercury":[1, 3, 4, 5, 7, 8, 10, 11],
        "Jupiter":[1, 4, 7, 8, 10, 11, 12],
        "Venus":  [3, 4, 5, 7, 9, 10, 11],
        "Saturn": [3, 5, 6, 11],
        "Lagna":  [3, 6, 10, 11],
    },
    "Mars": {
        "Sun":    [3, 5, 6, 10, 11],
        "Moon":   [3, 6, 11],
        "Mars":   [1, 2, 4, 7, 8, 10, 11],
        "Mercury":[3, 5, 6, 11],
        "Jupiter":[6, 10, 11, 12],
        "Venus":  [6, 8, 11, 12],
        "Saturn": [1, 4, 7, 8, 9, 10, 11],
        "Lagna":  [1, 2, 4, 7, 8, 10, 11],
    },
    "Mercury": {
        "Sun":    [5, 6, 9, 11, 12],
        "Moon":   [2, 4, 6, 8, 10, 11],
        "Mars":   [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury":[1, 3, 5, 6, 9, 10, 11, 12],
        "Jupiter":[6, 8, 11, 12],
        "Venus":  [1, 2, 3, 4, 5, 8, 9, 11],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna":  [1, 2, 4, 6, 8, 10, 11],
    },
    "Jupiter": {
        "Sun":    [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "Moon":   [2, 5, 7, 9, 11],
        "Mars":   [1, 2, 4, 7, 8, 10, 11],
        "Mercury":[1, 2, 4, 5, 6, 9, 10, 11],
        "Jupiter":[1, 2, 3, 4, 7, 8, 10, 11],
        "Venus":  [2, 5, 6, 9, 10, 11],
        "Saturn": [3, 5, 6, 12],
        "Lagna":  [1, 2, 4, 5, 6, 7, 9, 10, 11],
    },
    "Venus": {
        "Sun":    [8, 11, 12],
        "Moon":   [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Mars":   [3, 4, 6, 9, 11, 12],
        "Mercury":[3, 5, 6, 9, 11],
        "Jupiter":[5, 8, 9, 10, 11],
        "Venus":  [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Saturn": [3, 4, 5, 8, 9, 10, 11],
        "Lagna":  [1, 2, 3, 4, 5, 8, 9, 11],
    },
    "Saturn": {
        "Sun":    [1, 2, 4, 7, 8, 10, 11],
        "Moon":   [3, 6, 11],
        "Mars":   [3, 5, 6, 10, 11, 12],
        "Mercury":[6, 8, 9, 10, 11, 12],
        "Jupiter":[5, 6, 11, 12],
        "Venus":  [6, 11, 12],
        "Saturn": [3, 5, 6, 11],
        "Lagna":  [1, 3, 4, 6, 10, 11],
    },
    "Lagna": {
        "Sun":    [3, 4, 6, 10, 11, 12],
        "Moon":   [3, 6, 10, 11],
        "Mars":   [1, 2, 4, 8, 10, 11],
        "Mercury":[1, 2, 4, 6, 8, 10, 11],
        "Jupiter":[1, 2, 4, 5, 6, 7, 9, 10, 11],
        "Venus":  [1, 2, 3, 4, 5, 8, 9, 11],
        "Saturn": [1, 3, 4, 6, 10, 11],
        "Lagna":  [],  # Lagna has no self-contribution
    },
}

PLANET_ORDER = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Lagna"]


def calc_single_av(target_planet, sign_positions):
    """
    Calculate Ashtakavarga table for a single target_planet.
    sign_positions: dict {planet: sign_idx (0-11), "Lagna": sign_idx}
    Returns: list of 12 values (bindus per sign) + contributions dict
    """
    table_rows = AV_TABLES.get(target_planet, {})
    totals = [0] * 12
    contributions = {}

    for source, houses in table_rows.items():
        src_sign = sign_positions.get(source)
        if src_sign is None:
            continue
        row = [0] * 12
        for h in houses:
            sign = (src_sign + h - 1) % 12
            row[sign] = 1
            totals[sign] += 1
        contributions[source] = row

    return totals, contributions


def calc_all_ashtakavarga(planets, ascendant):
    """
    Calculate Ashtakavarga for all 7 planets + Lagna.
    planets: dict of planet_name -> data dict with 'sign_idx'
    ascendant: dict with 'sign_idx'
    Returns: dict with planet names as keys, each containing 'bindus' (list of 12) and 'contributions'.
    Also returns 'Samudaya' (combined table).
    """
    sign_pos = {
        "Sun":     planets["Sun"]["sign_idx"],
        "Moon":    planets["Moon"]["sign_idx"],
        "Mars":    planets["Mars"]["sign_idx"],
        "Mercury": planets["Mercury"]["sign_idx"],
        "Jupiter": planets["Jupiter"]["sign_idx"],
        "Venus":   planets["Venus"]["sign_idx"],
        "Saturn":  planets["Saturn"]["sign_idx"],
        "Lagna":   ascendant["sign_idx"],
    }

    result = {}
    samudaya = [0] * 12

    for target in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Lagna"]:
        bindus, contribs = calc_single_av(target, sign_pos)
        result[target] = {"bindus": bindus, "contributions": contribs}
        for i in range(12):
            samudaya[i] += bindus[i]

    result["Samudaya"] = {"bindus": samudaya}
    return result
