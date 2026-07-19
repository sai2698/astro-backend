"""
HTML-based Kundali PDF renderer using xhtml2pdf (pure Python, no external DLLs).
Generates a beautiful HTML document and converts it to PDF.
"""
import os
from io import BytesIO
from xhtml2pdf import pisa
from kundali_gen.pdf.html_template import build_html


def render_html_pdf(data, panchanga, planets, ascendant, all_vargas,
                    dasha_rows_3, sookshma_1yr, av_data, kaal_sarp, mangal,
                    jaimini_karakas, output_path, charttype="full", language="en"):
    """Build the HTML string and write PDF to output_path."""
    html_str = build_html(
        data=data,
        panchanga=panchanga,
        planets=planets,
        ascendant=ascendant,
        all_vargas=all_vargas,
        dasha_rows_3=dasha_rows_3,
        sookshma_1yr=sookshma_1yr,
        av_data=av_data,
        kaal_sarp=kaal_sarp,
        mangal=mangal,
        jaimini_karakas=jaimini_karakas,
        charttype=charttype,
        language=language
    )

    # Save HTML for debugging / preview in browser
    html_debug = output_path.replace(".pdf", ".html")
    with open(html_debug, "w", encoding="utf-8") as f:
        f.write(html_str)
    print(f"[DEBUG] HTML saved: {html_debug}")

    # Convert to PDF
    with open(output_path, "wb") as pdf_file:
        result = pisa.CreatePDF(
            html_str.encode("utf-8"),
            dest=pdf_file,
            encoding="utf-8",
        )

    if result.err:
        print(f"[WARN] PDF generation had {result.err} error(s).")
    else:
        print(f"[OK] PDF saved: {output_path}")
