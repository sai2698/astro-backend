"""
North Indian square-grid Kundali chart drawer using reportlab canvas.
Layout: 4x4 grid, center 2x2 merged with X-diagonals.
"""
from reportlab.lib import colors
from kundali_gen.pdf.styles import (
    COLOR_PLANET_RED, COLOR_PLANET_BLUE, FONT_BOLD, FONT_BODY, COLOR_SECTION_TEXT
)
from kundali_gen.data.constants import SIGNS, PLANET_SHORT, PLANETS

# House positions as normalized (0-1) center coords within chart box.
# Grid: 4 cols x 4 rows, each cell = 1/4 of chart size.
# Center (houses not here) = inner 2x2 merged square.
# x increases right, y increases UP (reportlab convention).
HOUSE_CENTERS = {
    12: (1/8, 7/8),   # top-left corner
     1: (3/8, 7/8),   # top row, 2nd cell
     2: (5/8, 7/8),   # top row, 3rd cell
     3: (7/8, 7/8),   # top-right corner
     4: (7/8, 5/8),   # right col, upper
     5: (7/8, 3/8),   # right col, lower
     6: (7/8, 1/8),   # bottom-right corner
     7: (5/8, 1/8),   # bottom row, 3rd cell
     8: (3/8, 1/8),   # bottom row, 2nd cell
     9: (1/8, 1/8),   # bottom-left corner
    10: (1/8, 3/8),   # left col, lower
    11: (1/8, 5/8),   # left col, upper
}


def draw_north_indian_chart(c, x, y, size, lagna_sign_idx, planet_houses,
                             asc_deg_str="", chart_label=""):
    """
    Draw a proper North Indian square-grid Kundali chart.

    Args:
        c            : reportlab canvas
        x, y         : bottom-left corner of chart square
        size         : side length (square)
        lagna_sign_idx: 0-based sign index for house 1 (Lagna)
        planet_houses: dict {house_num(1-12): [list of abbr strings]}
        chart_label  : label shown in centre (e.g. "Lagna: 11")
    """
    s = size

    c.saveState()

    # ── 1. Outer border ──────────────────────────────────────────────────
    c.setStrokeColor(colors.HexColor("#8B1A1A"))
    c.setLineWidth(1.2)
    c.rect(x, y, s, s)

    # ── 2. All internal border segments (drawn explicitly to avoid gaps) ──
    c.setLineWidth(0.8)

    # Two full vertical lines
    c.line(x + s/4,   y,       x + s/4,   y + s)
    c.line(x + 3*s/4, y,       x + 3*s/4, y + s)

    # Two full horizontal lines
    c.line(x,         y + s/4, x + s,     y + s/4)
    c.line(x,         y + 3*s/4, x + s,   y + 3*s/4)

    # ── 3. X-diagonals inside the centre 2×2 square ─────────────────────
    c.line(x + s/4, y + s/4,   x + 3*s/4, y + 3*s/4)
    c.line(x + s/4, y + 3*s/4, x + 3*s/4, y + s/4)

    # ── 3b. Re-draw the four corner-to-edge segments explicitly ──────────
    # (ensures 12↔11 and 5↔6 borders are never missing)
    c.line(x,         y + 3*s/4, x + s/4,   y + 3*s/4)   # 12-11 left segment
    c.line(x + 3*s/4, y + s/4,   x + s,     y + s/4)     # 5-6  right segment
    c.line(x,         y + s/4,   x + s/4,   y + s/4)     # 10-9  left segment
    c.line(x + 3*s/4, y + 3*s/4, x + s,     y + 3*s/4)   # 3-4  right segment

    # Re-draw outer border on top so it is always clean
    c.setStrokeColor(colors.HexColor("#8B1A1A"))
    c.setLineWidth(1.2)
    c.rect(x, y, s, s, fill=0, stroke=1)

    # ── 4. Sign numbers in each house (small, top-left of cell) ──────────
    c.setFillColor(COLOR_PLANET_RED)
    c.setFont(FONT_BOLD, 7)
    for house_num, (nx, ny) in HOUSE_CENTERS.items():
        sign_num = ((lagna_sign_idx + house_num - 1) % 12) + 1
        cx = x + nx * s
        cy = y + ny * s
        # Small sign number at top-left of the cell
        c.drawString(cx - s/8 + 2, cy + s/8 - 9, str(sign_num))

    # ── 5. Planet abbreviations in each house ────────────────────────────
    for house_num, planet_abbrs in planet_houses.items():
        if not planet_abbrs:
            continue
        nx, ny = HOUSE_CENTERS[house_num]
        cx = x + nx * s
        cy = y + ny * s

        # Stack planets below the cell midpoint, 2 per row
        for i, abbr in enumerate(planet_abbrs):
            row = i // 2
            col = i % 2
            px = cx - 14 + col * 20
            py = cy - row * 9

            # Colour: retrograde = red, combust = orange, else blue
            if "®" in abbr or "(R)" in abbr:
                c.setFillColor(COLOR_PLANET_RED)
            else:
                c.setFillColor(COLOR_PLANET_BLUE)
            c.setFont(FONT_BODY, 7)
            c.drawString(px, py, abbr)

    # ── 6. Centre label (Lagna info / Om) ────────────────────────────────
    if chart_label:
        c.setFillColor(COLOR_SECTION_TEXT)
        c.setFont(FONT_BOLD, 7.5)
        c.drawCentredString(x + s/2, y + s/2 + 4, chart_label)

    c.restoreState()


def planets_to_houses(planets_data, ascendant_data, varga_signs=None):
    """
    Return dict {house_num(1-12): [abbr_strings]} for chart drawing.
    If varga_signs provided, use those sign positions (divisional charts).
    """
    short_map = dict(zip(PLANETS, PLANET_SHORT))
    planet_names = ["Sun", "Moon", "Mars", "Mercury", "Jupiter",
                    "Venus", "Saturn", "Rahu", "Ketu"]

    houses = {i: [] for i in range(1, 13)}

    if varga_signs is not None:
        asc_sign = varga_signs.get("Ascendant", 0)
        for p in planet_names:
            p_sign = varga_signs.get(p)
            if p_sign is None:
                continue
            house = ((p_sign - asc_sign) % 12) + 1
            abbr = short_map.get(p, p[:2])
            retro = planets_data.get(p, {}).get("retrograde", False)
            combust = planets_data.get(p, {}).get("combust", False)
            suffix = " ®" if retro else (" ©" if combust else "")
            houses[house].append(abbr + suffix)
    else:
        for p in planet_names:
            house = planets_data[p].get("house", 1)
            abbr = short_map.get(p, p[:2])
            retro = planets_data[p].get("retrograde", False)
            combust = planets_data[p].get("combust", False)
            suffix = " ®" if retro else (" ©" if combust else "")
            houses[house].append(abbr + suffix)

    return houses
