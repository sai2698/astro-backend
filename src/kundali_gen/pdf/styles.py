"""
Shared PDF styles, colors, and fonts for the Kundali PDF generator.
"""
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 20 * mm

# Color palette
COLOR_HEADER_BG = colors.HexColor("#8B1A1A")      # Deep saffron/red for header
COLOR_HEADER_TEXT = colors.white
COLOR_SECTION_BG = colors.HexColor("#F5E6D3")     # Cream background for section titles
COLOR_SECTION_TEXT = colors.HexColor("#5C1A1A")   # Dark maroon for section text
COLOR_ACCENT = colors.HexColor("#CC6600")         # Orange accent
COLOR_TABLE_HEADER = colors.HexColor("#D4A054")   # Golden table header
COLOR_TABLE_ROW_ALT = colors.HexColor("#FFF8F0")  # Light cream alt row
COLOR_TABLE_ROW = colors.white
COLOR_TABLE_BORDER = colors.HexColor("#C8A870")   # Soft gold border
COLOR_BODY_TEXT = colors.HexColor("#1A1A1A")
COLOR_PLANET_RED = colors.HexColor("#AA0000")
COLOR_PLANET_BLUE = colors.HexColor("#003399")
COLOR_RETRO = colors.HexColor("#8B0000")
COLOR_FOOTER = colors.HexColor("#888888")

# Font names (using built-in Helvetica family for compatibility)
FONT_BODY = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
FONT_ITALIC = "Helvetica-Oblique"

def get_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='KundaliTitle',
        fontName=FONT_BOLD,
        fontSize=18,
        textColor=COLOR_HEADER_TEXT,
        spaceAfter=6,
        alignment=1,  # center
    ))
    styles.add(ParagraphStyle(
        name='SectionHeading',
        fontName=FONT_BOLD,
        fontSize=13,
        textColor=COLOR_SECTION_TEXT,
        spaceBefore=8,
        spaceAfter=4,
        alignment=1,
    ))
    styles.add(ParagraphStyle(
        name='SubHeading',
        fontName=FONT_BOLD,
        fontSize=10,
        textColor=COLOR_SECTION_TEXT,
        spaceBefore=6,
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name='BodyText2',
        fontName=FONT_BODY,
        fontSize=8.5,
        textColor=COLOR_BODY_TEXT,
        leading=13,
        spaceAfter=3,
    ))
    styles.add(ParagraphStyle(
        name='SmallText',
        fontName=FONT_BODY,
        fontSize=7.5,
        textColor=COLOR_BODY_TEXT,
        leading=11,
    ))
    styles.add(ParagraphStyle(
        name='FooterText',
        fontName=FONT_ITALIC,
        fontSize=7,
        textColor=COLOR_FOOTER,
        alignment=1,
    ))
    styles.add(ParagraphStyle(
        name='ChartLabel',
        fontName=FONT_BOLD,
        fontSize=9,
        textColor=COLOR_SECTION_TEXT,
        alignment=1,
    ))
    return styles


def draw_page_header(canvas_obj, name, page_num):
    """Draw the consistent red header bar with name and page number."""
    canvas_obj.saveState()
    w = PAGE_WIDTH
    # Header bar
    canvas_obj.setFillColor(COLOR_HEADER_BG)
    canvas_obj.rect(0, PAGE_HEIGHT - 30*mm, w, 30*mm, fill=1, stroke=0)
    # Name in header
    canvas_obj.setFillColor(COLOR_HEADER_TEXT)
    canvas_obj.setFont(FONT_BOLD, 14)
    canvas_obj.drawCentredString(w/2, PAGE_HEIGHT - 20*mm, name)
    # Page number
    canvas_obj.setFont(FONT_BODY, 8)
    canvas_obj.drawRightString(w - MARGIN, PAGE_HEIGHT - 10*mm, f"Page {page_num}")
    canvas_obj.restoreState()

def draw_section_title(canvas_obj, title, y, width=None):
    """Draw a section title with colored background."""
    w = width or PAGE_WIDTH - 2 * MARGIN
    canvas_obj.saveState()
    canvas_obj.setFillColor(COLOR_SECTION_BG)
    canvas_obj.rect(MARGIN, y - 5*mm, w, 8*mm, fill=1, stroke=0)
    canvas_obj.setFillColor(COLOR_SECTION_TEXT)
    canvas_obj.setFont(FONT_BOLD, 12)
    canvas_obj.drawCentredString(MARGIN + w/2, y - 1*mm, title)
    canvas_obj.restoreState()
    return y - 10*mm

def draw_footer(canvas_obj, page_num):
    """Draw footer with website attribution."""
    canvas_obj.saveState()
    canvas_obj.setFillColor(COLOR_FOOTER)
    canvas_obj.setFont(FONT_ITALIC, 7)
    canvas_obj.drawCentredString(PAGE_WIDTH/2, 10*mm,
        "Authentic Astrology  |  Vedic Horoscope Report")
    canvas_obj.restoreState()

def draw_kv_row(canvas_obj, x, y, key, value, key_width=80, row_height=5*mm):
    """Draw a key-value row."""
    canvas_obj.setFont(FONT_BOLD, 9)
    canvas_obj.setFillColor(COLOR_SECTION_TEXT)
    canvas_obj.drawString(x, y, key)
    canvas_obj.setFont(FONT_BODY, 9)
    canvas_obj.setFillColor(COLOR_BODY_TEXT)
    canvas_obj.drawString(x + key_width, y, str(value))
    return y - row_height
