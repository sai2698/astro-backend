"""
Reusable table rendering helpers using reportlab.
"""
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from kundali_gen.pdf.styles import (
    COLOR_TABLE_HEADER, COLOR_TABLE_ROW_ALT, COLOR_TABLE_ROW,
    COLOR_TABLE_BORDER, COLOR_HEADER_BG, COLOR_HEADER_TEXT, FONT_BOLD, FONT_BODY
)

def make_table(data, col_widths, row_heights=None, header_rows=1, alt_rows=True):
    """
    Create a styled reportlab Table.
    data: list of lists (first row = headers)
    col_widths: list of column widths in points
    """
    t = Table(data, colWidths=col_widths, rowHeights=row_heights)

    style_cmds = [
        # Header style
        ('BACKGROUND', (0, 0), (-1, header_rows - 1), COLOR_TABLE_HEADER),
        ('TEXTCOLOR', (0, 0), (-1, header_rows - 1), colors.white),
        ('FONTNAME', (0, 0), (-1, header_rows - 1), FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, header_rows - 1), 8),
        ('ALIGN', (0, 0), (-1, header_rows - 1), 'CENTER'),
        # Body style
        ('FONTNAME', (0, header_rows), (-1, -1), FONT_BODY),
        ('FONTSIZE', (0, header_rows), (-1, -1), 8),
        ('ALIGN', (0, header_rows), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # Borders
        ('GRID', (0, 0), (-1, -1), 0.4, COLOR_TABLE_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]

    # Alternating row colors
    if alt_rows:
        for row_idx in range(header_rows, len(data)):
            if row_idx % 2 == 0:
                style_cmds.append(('BACKGROUND', (0, row_idx), (-1, row_idx), COLOR_TABLE_ROW_ALT))
            else:
                style_cmds.append(('BACKGROUND', (0, row_idx), (-1, row_idx), COLOR_TABLE_ROW))

    t.setStyle(TableStyle(style_cmds))
    return t

def make_kv_table(pairs, col_widths=(120, 200), header_bg=None):
    """
    Create a two-column key-value table.
    pairs: list of (key, value) tuples
    """
    data = [[k, str(v)] for k, v in pairs]
    t = Table(data, colWidths=list(col_widths))
    style = [
        ('FONTNAME', (0, 0), (0, -1), FONT_BOLD),
        ('FONTNAME', (1, 0), (1, -1), FONT_BODY),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.3, COLOR_TABLE_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
    ]
    for i in range(len(data)):
        bg = COLOR_TABLE_ROW_ALT if i % 2 == 0 else COLOR_TABLE_ROW
        style.append(('BACKGROUND', (0, i), (-1, i), bg))
    t.setStyle(TableStyle(style))
    return t
