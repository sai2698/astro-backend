"""
Master PDF renderer - orchestrates all sections into the final Kundali PDF.
"""
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.platypus import (SimpleDocTemplate, Spacer, Paragraph, PageBreak, Table, TableStyle, KeepTogether)
from reportlab.lib.units import mm
from reportlab.lib import colors
import io

from kundali_gen.pdf.styles import *
from kundali_gen.pdf.chart_drawer import draw_north_indian_chart, planets_to_houses
from kundali_gen.pdf.table_helpers import make_table, make_kv_table
from kundali_gen.data.constants import *
from kundali_gen.core.divisional import VARGA_NAMES, VARGA_MEANING

PAGE_W, PAGE_H = A4
MARGIN = 18 * mm
CONTENT_W = PAGE_W - 2 * MARGIN
CONTENT_TOP = PAGE_H - 35 * mm
FOOTER_Y = 8 * mm


class KundaliRenderer:
    def __init__(self, output_filename):
        self.output = output_filename
        self.c = pdf_canvas.Canvas(output_filename, pagesize=A4)
        self.page_num = 0
        self.data = None

    def set_data(self, data):
        self.data = data

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _new_page(self, show_header=True):
        if self.page_num > 0:
            self.c.showPage()
        self.page_num += 1
        if show_header:
            self._draw_header()
        self._draw_footer()

    def _draw_header(self):
        d = self.data
        self.c.setFillColor(COLOR_HEADER_BG)
        self.c.rect(0, PAGE_H - 28 * mm, PAGE_W, 28 * mm, fill=1, stroke=0)
        self.c.setFillColor(COLOR_HEADER_TEXT)
        self.c.setFont(FONT_BOLD, 13)
        name = d.get("name", "")
        self.c.drawCentredString(PAGE_W / 2, PAGE_H - 13 * mm, name)
        self.c.setFont(FONT_BODY, 7)
        self.c.drawRightString(PAGE_W - MARGIN, PAGE_H - 6 * mm, f"Page {self.page_num}")

    def _draw_footer(self):
        self.c.setFillColor(COLOR_FOOTER)
        self.c.setFont(FONT_ITALIC, 6.5)
        self.c.drawCentredString(PAGE_W / 2, FOOTER_Y,
            "Authentic Astrology  |  Vedic Horoscope Report")

    def _section_title(self, title, y):
        self.c.setFillColor(COLOR_SECTION_BG)
        self.c.rect(MARGIN, y - 5 * mm, CONTENT_W, 7 * mm, fill=1, stroke=0)
        self.c.setFillColor(COLOR_SECTION_TEXT)
        self.c.setFont(FONT_BOLD, 11)
        self.c.drawCentredString(PAGE_W / 2, y - 1.5 * mm, title)
        return y - 9 * mm

    def _draw_table(self, table_data, col_widths, y, header_rows=1):
        t = make_table(table_data, col_widths, header_rows=header_rows)
        tw, th = t.wrapOn(self.c, CONTENT_W, PAGE_H)
        t.drawOn(self.c, MARGIN, y - th)
        return y - th - 3 * mm

    def _kv_block(self, pairs, y, col1=90, col2=140, col3=None, col4=None):
        """Draw a two or four column key-value grid."""
        row_h = 6 * mm
        x = MARGIN
        for k, v in pairs:
            self.c.setFont(FONT_BOLD, 8.5)
            self.c.setFillColor(COLOR_SECTION_TEXT)
            self.c.drawString(x, y, k)
            self.c.setFont(FONT_BODY, 8.5)
            self.c.setFillColor(COLOR_BODY_TEXT)
            self.c.drawString(x + col1, y, str(v))
            y -= row_h
        return y

    def _wrap_text(self, text, y, font_size=8, leading=12, max_width=None):
        mw = max_width or CONTENT_W
        from reportlab.pdfbase.pdfmetrics import stringWidth
        words = text.split()
        line = ""
        self.c.setFont(FONT_BODY, font_size)
        self.c.setFillColor(COLOR_BODY_TEXT)
        lines = []
        for w in words:
            test = (line + " " + w).strip()
            if stringWidth(test, FONT_BODY, font_size) <= mw:
                line = test
            else:
                if line:
                    lines.append(line)
                line = w
        if line:
            lines.append(line)
        for ln in lines:
            self.c.drawString(MARGIN, y, ln)
            y -= leading
        return y

    # ── Pages ─────────────────────────────────────────────────────────────────

    def render_cover(self):
        d = self.data
        self._new_page(show_header=False)
        # Full header for cover
        self.c.setFillColor(COLOR_HEADER_BG)
        self.c.rect(0, PAGE_H - 55 * mm, PAGE_W, 55 * mm, fill=1, stroke=0)
        self.c.setFillColor(COLOR_HEADER_TEXT)
        self.c.setFont(FONT_BOLD, 22)
        self.c.drawCentredString(PAGE_W / 2, PAGE_H - 22 * mm, "Authentic Astrology")
        self.c.setFont(FONT_BOLD, 16)
        self.c.drawCentredString(PAGE_W / 2, PAGE_H - 35 * mm, "Vedic Horoscope Report")
        self.c.setFont(FONT_ITALIC, 10)
        self.c.setFillColor(colors.HexColor("#FFD700"))
        self.c.drawCentredString(PAGE_W / 2, PAGE_H - 47 * mm, "Authentic Vedic Astrology")

        y = PAGE_H - 65 * mm
        self.c.setFillColor(COLOR_BODY_TEXT)
        self.c.setFont(FONT_ITALIC, 9)
        self.c.drawCentredString(PAGE_W / 2, y, "Janani janma saukhyanam, vardhani kula sampadam |")
        y -= 6 * mm
        self.c.drawCentredString(PAGE_W / 2, y, "Padavi poorva punyanam, likhyate janma patrika ||")

        y -= 12 * mm
        y = self._section_title("Birth Details", y)
        y -= 3 * mm

        birth_pairs = [
            ("Name", d.get("name", "")),
            ("Gender", d.get("gender", "")),
            ("Date of Birth", d.get("dob_display", d.get("dob_str", ""))),
            ("Time of Birth", d.get("time_str", "")),
            ("Place of Birth", d.get("full_address", d.get("place_name", ""))),
            ("Latitude", f"{d['lat']:.5f} N"),
            ("Longitude", f"{d['lon']:.5f} E"),
            ("Timezone", f"{d['tz_str']} ({d['tz_offset']}) E"),
        ]
        for k, v in birth_pairs:
            self.c.setFont(FONT_BOLD, 10)
            self.c.setFillColor(COLOR_SECTION_TEXT)
            self.c.drawString(MARGIN + 10, y, k)
            self.c.setFont(FONT_BODY, 10)
            self.c.setFillColor(COLOR_BODY_TEXT)
            self.c.drawString(MARGIN + 120, y, str(v))
            y -= 7 * mm

    def render_panchanga(self, panchanga):
        self._new_page()
        y = CONTENT_TOP
        y = self._section_title("Panchanga Details", y)
        y -= 3 * mm

        pairs = [
            ("Sunrise", panchanga["sunrise"]),
            ("Sunset", panchanga["sunset"]),
            ("Day Length", panchanga["day_length"]),
            ("Night Length", panchanga["night_length"]),
            ("Kali Year", panchanga["kali_year"]),
            ("Saka Year", panchanga["saka_year"]),
            ("Hindu Year", panchanga["hindu_year"]),
            ("Ayana", panchanga["ayana"]),
            ("Rithu (Season)", panchanga["ritu"]),
            ("Hindu Month", panchanga["hindu_month"]),
            ("Tithi", panchanga["tithi"]),
            ("Weekday", panchanga["weekday"]),
            ("Vedic Weekday", panchanga["vedic_weekday"]),
            ("Nakshatra, Pada", panchanga["nakshatra_pada"]),
            ("Sign", f"{panchanga['moon_sign']} Sign"),
            ("Yoga", panchanga["yoga"]),
            ("Karana", panchanga["karana"]),
            ("Janmakshar", panchanga["janmakshar"]),
            ("Vimshottari Dasa", self.data.get("dasha_lord", "Mars")),
        ]
        for k, v in pairs:
            self.c.setFont(FONT_BOLD, 9)
            self.c.setFillColor(COLOR_SECTION_TEXT)
            self.c.drawString(MARGIN + 5, y, k)
            self.c.setFont(FONT_BODY, 9)
            self.c.setFillColor(COLOR_BODY_TEXT)
            self.c.drawString(MARGIN + 130, y, str(v))
            y -= 6 * mm

    def render_avakahada(self, panchanga):
        self._new_page()
        y = CONTENT_TOP
        y = self._section_title("Avakahada Chakra", y)
        y -= 3 * mm
        pairs = [
            ("Nakshatra", panchanga["nakshatra"]),
            ("Nadi", panchanga["nadi"]),
            ("Yoni", panchanga["yoni"]),
            ("Gana", panchanga["gana"]),
            ("Sign", panchanga["moon_sign"]),
            ("Rashi lord", panchanga["rashi_lord"]),
            ("Varna Kuta", SIGN_VARNA.get(panchanga["moon_sign_idx"], "")),
            ("Vashya Kuta", SIGN_VASHYA.get(panchanga["moon_sign_idx"], "")),
        ]
        for k, v in pairs:
            self.c.setFont(FONT_BOLD, 9)
            self.c.setFillColor(COLOR_SECTION_TEXT)
            self.c.drawString(MARGIN + 5, y, k)
            self.c.setFont(FONT_BODY, 9)
            self.c.setFillColor(COLOR_BODY_TEXT)
            self.c.drawString(MARGIN + 130, y, str(v))
            y -= 6 * mm

    def render_lucky_things(self, lagna_idx, jaimini_karakas):
        self._new_page()
        y = CONTENT_TOP
        y = self._section_title("Lucky Things", y)
        y -= 3 * mm

        lt = get_lucky_things(lagna_idx)
        lucky_pairs = [
            ("Lucky Days", ", ".join(lt.get("days", []))),
            ("Lucky Planets", ", ".join(lt.get("planets", []))),
            ("Friendly Signs", ", ".join(lt.get("friendly_signs", []))),
            ("Friendly Ascendant", ", ".join(lt.get("friendly_asc", []))),
            ("Life Stone", lt.get("life_stone", "")),
            ("Lucky Stone", lt.get("lucky_stone", "")),
            ("Punya Stone", lt.get("punya_stone", "")),
            ("Favorable Deity", ", ".join(lt.get("deity", []))),
            ("Favorable Metal", lt.get("metal", "")),
            ("Favorable Color", ", ".join(lt.get("color", []))),
            ("Favorable Direction", ", ".join(lt.get("direction", []))),
            ("Favorable Time", lt.get("time", "")),
            ("Favorable Numbers", ", ".join(lt.get("numbers", []))),
        ]
        for k, v in lucky_pairs:
            self.c.setFont(FONT_BOLD, 9)
            self.c.setFillColor(COLOR_SECTION_TEXT)
            self.c.drawString(MARGIN + 5, y, k)
            self.c.setFont(FONT_BODY, 9)
            self.c.setFillColor(COLOR_BODY_TEXT)
            self.c.drawString(MARGIN + 140, y, str(v))
            y -= 6 * mm

        y -= 5 * mm
        y = self._section_title("Jaimini Karakas", y)
        y -= 3 * mm

        headers = ["Planet", "Chara Karaka", "Sthira Karaka"]
        rows = [headers]
        chara_order = ["Atmakaraka", "Amatyakaraka", "Bhratrukaraka", "Matrukaraka",
                       "Putrakaraka", "Gnatikaraka", "Darakaraka"]
        from kundali_gen.data.constants import STHIRA_KARAKAS
        for i, (karaka, planet) in enumerate(jaimini_karakas.items()):
            p_short = PLANET_SHORT[PLANETS.index(planet)] if planet in PLANETS else planet[:2]
            sthira = STHIRA_KARAKAS.get(planet, "")
            rows.append([p_short, karaka, sthira])
        cw = [CONTENT_W * 0.2, CONTENT_W * 0.4, CONTENT_W * 0.4]
        y = self._draw_table(rows, cw, y)

    def render_planetary_positions(self, planets, ascendant):
        self._new_page()
        y = CONTENT_TOP
        y = self._section_title("Planetary Positions", y)
        y -= 3 * mm

        headers = ["Planet", "Rx/Comb", "Sign", "Deg/Min/Sec", "House"]
        rows = [headers]
        planet_order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Ascendant"]
        for p in planet_order:
            if p == "Ascendant":
                data = ascendant
                rx_comb = "-"
            else:
                data = planets[p]
                rx_comb = "(R)" if data.get("retrograde") else ("(C)" if data.get("combust") else "-")
            rows.append([
                p if p != "Ascendant" else "Ascendant",
                rx_comb,
                SIGNS[data["sign_idx"]],
                data["dms"],
                str(planets[p].get("house", "-")) if p != "Ascendant" else "-"
            ])

        cw = [CONTENT_W * 0.22, CONTENT_W * 0.12, CONTENT_W * 0.22, CONTENT_W * 0.22, CONTENT_W * 0.22]
        y = self._draw_table(rows, cw, y)

        y -= 5 * mm
        y = self._section_title("Planetary Table (Nakshatra)", y)
        y -= 3 * mm

        headers2 = ["Planet", "Nakshatra/Pada", "Nak. Lord", "Navamsha Sign", "Navamsha Lord"]
        rows2 = [headers2]
        for p in planet_order:
            if p == "Ascendant":
                data = ascendant
            else:
                data = planets[p]
            nak_idx = data["nakshatra_idx"]
            pada = data["pada"]
            nak = NAKSHATRAS[nak_idx]
            nav_sign_idx = data.get("nav_sign_idx", (nak_idx * 4 + pada - 1) % 12)
            rows2.append([
                p,
                f"{nak['name']}-{pada}",
                nak["lord"],
                SIGNS[nav_sign_idx],
                SIGN_LORD[nav_sign_idx]
            ])

        cw2 = [CONTENT_W*0.2, CONTENT_W*0.25, CONTENT_W*0.18, CONTENT_W*0.2, CONTENT_W*0.17]
        y = self._draw_table(rows2, cw2, y)

    def render_bhava_table(self, planets, ascendant, sripati_cusps):
        self._new_page()
        y = CONTENT_TOP
        y = self._section_title("Bhava Table", y)
        y -= 3 * mm

        headers = ["House", "Sign", "Deg/Min/Sec"]
        rows = [headers]
        for i, cusp in enumerate(sripati_cusps[:12]):
            sign_idx = int(cusp / 30) % 12
            deg = cusp % 30
            d = int(deg); m = int((deg - d) * 60); s = int(((deg - d) * 60 - m) * 60)
            rows.append([BHAVA_NAMES[i], SIGNS[sign_idx], f"{d:02d}:{m:02d}:{s:02d}"])

        cw = [CONTENT_W * 0.45, CONTENT_W * 0.3, CONTENT_W * 0.25]
        y = self._draw_table(rows, cw, y)

    def render_divisional_charts_page(self, charts_on_page, all_vargas, planets, ascendant):
        """Render up to 4 divisional charts on one page."""
        self._new_page()
        y = CONTENT_TOP
        chart_size = 68 * mm
        charts_per_row = 2

        for i, varga_key in enumerate(charts_on_page):
            row = i // charts_per_row
            col = i % charts_per_row

            cx = MARGIN + col * (chart_size + 10 * mm)
            cy = y - row * (chart_size + 20 * mm)

            varga_signs = all_vargas[varga_key]
            asc_sign = varga_signs.get("Ascendant", ascendant["sign_idx"])
            planet_houses = planets_to_houses(planets, ascendant, varga_signs)

            # Label
            self.c.setFont(FONT_BOLD, 9)
            self.c.setFillColor(COLOR_SECTION_TEXT)
            label = VARGA_NAMES.get(varga_key, varga_key)
            self.c.drawCentredString(cx + chart_size / 2, cy + 3, label)

            draw_north_indian_chart(
                self.c, cx, cy - chart_size, chart_size,
                asc_sign, planet_houses,
                chart_label=f"Lagna: {asc_sign + 1}"
            )

            # Meaning below chart
            meaning = VARGA_MEANING.get(varga_key, "")
            if meaning:
                self.c.setFont(FONT_ITALIC, 7)
                self.c.setFillColor(COLOR_FOOTER)
                self.c.drawCentredString(cx + chart_size / 2, cy - chart_size - 8, meaning[:70])

    def render_ashtakavarga_table(self, planet_name, av_data):
        """Render one Ashtakavarga table for a planet."""
        self._new_page()
        y = CONTENT_TOP
        y = self._section_title(f"{planet_name} Ashtakavarga Table", y)
        y -= 3 * mm

        sources = ["Su", "Mo", "Me", "Ve", "Ma", "Ju", "Sa", "As", "Total Score"]
        headers = ["Sign"] + sources
        rows = [headers]
        bindus = av_data.get(planet_name, {}).get("bindus", [0] * 12)
        contribs = av_data.get(planet_name, {}).get("contributions", {})
        src_map = {"Sun": "Su", "Moon": "Mo", "Mercury": "Me", "Venus": "Ve",
                   "Mars": "Ma", "Jupiter": "Ju", "Saturn": "Sa", "Lagna": "As"}

        for s_idx, sname in enumerate(SIGN_SHORT):
            row = [sname]
            for full_name, abbr in src_map.items():
                c_val = contribs.get(full_name, [0]*12)
                row.append(str(c_val[s_idx]) if len(c_val) > s_idx else "0")
            row.append(str(bindus[s_idx]))
            rows.append(row)

        cw = [CONTENT_W * 0.1] + [CONTENT_W * 0.08] * 8 + [CONTENT_W * 0.12]
        y = self._draw_table(rows, cw, y)

    def render_dasha_table(self, dasha_rows, group_md, group_bh=None):
        """Render Mahadasha/Bhukti/Pratyantar table for one MD-BH group."""
        self._new_page()
        y = CONTENT_TOP
        title = f"MD: {group_md}"
        if group_bh:
            title += f" - BH.: {group_bh}"
        y = self._section_title(title, y)
        y -= 3 * mm

        headers = ["MD", "BH.", "PR.", "Start Date", "Age"]
        table_data = [headers]
        from kundali_gen.core.dasha import format_dasha_date
        for row in dasha_rows:
            table_data.append([
                PLANET_SHORT[PLANETS.index(row["MD"])] if row["MD"] in PLANETS else row["MD"],
                PLANET_SHORT[PLANETS.index(row["BH"])] if row["BH"] in PLANETS else row["BH"],
                PLANET_SHORT[PLANETS.index(row["PR"])] if row["PR"] in PLANETS else row["PR"],
                format_dasha_date(row["start"]),
                f"{row['age']:.1f}"
            ])

        cw = [CONTENT_W * 0.1] * 3 + [CONTENT_W * 0.4, CONTENT_W * 0.3]
        y = self._draw_table(table_data, cw, y)

    def render_predictions_page(self, title, text_blocks):
        """Render a page with a title and multiple text paragraphs."""
        self._new_page()
        y = CONTENT_TOP
        y = self._section_title(title, y)
        y -= 4 * mm

        for heading, text in text_blocks:
            if heading:
                self.c.setFont(FONT_BOLD, 9)
                self.c.setFillColor(COLOR_SECTION_TEXT)
                self.c.drawString(MARGIN, y, heading)
                y -= 6 * mm

            if text:
                y = self._wrap_text(text, y, font_size=8, leading=12)
                y -= 3 * mm

            if y < 25 * mm:
                break

    def render_doshas(self, kaal_sarp, mangal):
        """Render Doshas & Remedies page."""
        self._new_page()
        y = CONTENT_TOP
        y = self._section_title("Doshas and Remedies", y)
        y -= 5 * mm

        self.c.setFont(FONT_BOLD, 10)
        self.c.setFillColor(COLOR_SECTION_TEXT)
        self.c.drawString(MARGIN, y, "Kaal Sarp Dosha")
        y -= 6 * mm

        found_ks, msg_ks = kaal_sarp
        y = self._wrap_text(msg_ks, y, font_size=8.5, leading=13)
        y -= 8 * mm

        self.c.setFont(FONT_BOLD, 10)
        self.c.setFillColor(COLOR_SECTION_TEXT)
        self.c.drawString(MARGIN, y, "Mangal Dosha")
        y -= 6 * mm

        lagna_res = mangal.get("lagna", {})
        if lagna_res.get("found"):
            y = self._wrap_text(f"Dosha Found: {lagna_res['message']}", y)
            for r in lagna_res.get("cancel_reasons", []):
                y = self._wrap_text(f"- {r}", y)
        else:
            y = self._wrap_text(lagna_res.get("message", ""), y)
        y -= 3 * mm

        moon_res = mangal.get("moon", {})
        y = self._wrap_text(moon_res.get("message", ""), y)
        venus_res = mangal.get("venus", {})
        y = self._wrap_text(venus_res.get("message", ""), y)

    def save(self):
        self.c.save()
        print(f"[OK] PDF saved: {self.output}")
