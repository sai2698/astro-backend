"""HTML template builder for Kundali PDF."""
from kundali_gen.data.constants import (
    SIGNS, SIGN_SHORT, NAKSHATRAS, PLANETS, PLANET_SHORT, BHAVA_NAMES, SIGN_LORD,
    get_lucky_things, STHIRA_KARAKAS, DASHA_ORDER
)
from kundali_gen.core.divisional import VARGA_NAMES, VARGA_MEANING
from kundali_gen.data.translations import t


CSS_STYLES = """
@page { size: A4; margin: 15mm 18mm 18mm 18mm; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Helvetica, Arial, sans-serif; font-size: 10pt; color: #1a1a1a; background: #fff; }

/* ── COVER ── */
.cover { page-break-after: always; min-height: 297mm; }
.cover-header {
  background-color: #1A365D;
  color: #fff; text-align: center; padding: 28mm 20mm 22mm;
}
.cover-brand { font-family: 'Cinzel', serif; font-size: 26pt; font-weight: 700; letter-spacing: 2px; }
.cover-subtitle { font-family: 'Cinzel', serif; font-size: 15pt; font-weight: 400; margin-top: 6mm; color: #63B3ED; letter-spacing: 3px; }
.cover-tagline { font-size: 10pt; font-style: italic; margin-top: 5mm; color: #EBF8FF; }
.cover-divider { width: 60mm; height: 2px; background-color: #63B3ED; margin: 6mm auto; }
.cover-body { padding: 12mm 20mm; }
.birth-card { background-color: #F7FAFC; border: 1px solid #90CDF4; border-radius: 3mm; padding: 8mm 10mm; margin-top: 10mm; }
.birth-card-title { font-family: 'Cinzel', serif; font-size: 12pt; color: #1A365D; border-bottom: 2px solid #3182CE; padding-bottom: 3mm; margin-bottom: 6mm; text-align: center; letter-spacing: 1px; }

/* ── SECTIONS ── */
.section { page-break-before: always; padding-top: 5mm; }
.section-title {
  background-color: #2C5282;
  color: #fff; font-family: 'Cinzel', serif; font-size: 12pt;
  text-align: center; padding: 3mm 5mm; letter-spacing: 1px;
  margin-bottom: 5mm; border-radius: 1mm;
}
.subtitle { font-family: 'Cinzel', serif; font-size: 10pt; color: #1A365D;
  background-color: #EBF8FF; padding: 2mm 4mm; margin: 5mm 0 3mm;
  border-left: 3px solid #3182CE;
}

/* ── TABLES ── */
table { width: 100%; border-collapse: collapse; font-size: 9pt; margin-bottom: 4mm; }
th { background: #3182CE; color: #fff; font-family: 'Cinzel', serif; font-size: 8pt; padding: 2.5mm 3mm; text-align: center; letter-spacing: 0.5px; }
td { padding: 2mm 3mm; border: 0.5pt solid #90CDF4; text-align: center; vertical-align: middle; }
tr:nth-child(even) td { background: #F7FAFC; }
tr:nth-child(odd) td { background: #fff; }
td:first-child { text-align: left; font-weight: 600; color: #2A4365; }
.kv-table td:first-child { width: 45%; }
.kv-table td:last-child { text-align: left; }

/* ── CHART ── */
.chart-wrap { text-align: center; margin: 4mm auto; }
.chart-title { font-size: 11pt; font-weight: bold; color: #1A365D; margin-bottom: 3mm; text-align: center; }
.chart-layout { display: table; width: 100%; }
.chart-left { display: table-cell; width: 55%; vertical-align: top; text-align: center; padding-right: 5mm; }
.chart-right { display: table-cell; width: 45%; vertical-align: top; }

/* ── GRID LAYOUT ── */
.varga-meaning { font-size: 8pt; font-style: italic; color: #2A4365; margin-top: 2mm; padding: 0 4mm; text-align: center; }

/* ── FOOTER ── */
.page-footer { position: fixed; bottom: 5mm; left: 0; right: 0; text-align: center; font-size: 7pt; color: #888; font-style: italic; }
.page-num::after { content: counter(page); }
"""

MOBILE_CSS = """
@media screen and (max-width: 768px) {
  @page { margin: 0; }
  body { 
    padding: 10px; font-size: 14px; background: #fff; 
    max-width: 100vw; overflow-x: hidden; 
    margin: 0 auto; text-align: center;
  }
  .cover { min-height: auto; padding-bottom: 20px; }
  .cover-header { padding: 40px 10px; }
  .cover-brand { font-size: 24px; text-align: center; }
  .cover-body { padding: 10px 0; margin: 0 auto; }
  .birth-card { margin: 15px auto 0; padding: 10px; text-align: center; }
  .section { padding-top: 15px; margin: 0 auto; }
  .section-title { 
    font-size: 16px; margin: 0 auto 15px; padding: 10px; 
    white-space: normal; height: auto; text-align: center;
  }
  .subtitle { text-align: center; margin: 5px auto; }
  
  /* Make tables scroll horizontally and center them */
  .data-table, .kv-table, .birth-card table { 
    display: block; width: 100%; max-width: 100%; 
    overflow-x: auto; -webkit-overflow-scrolling: touch; 
    white-space: nowrap; font-size: 13px; margin: 0 auto 20px; 
  }
  
  .chart-wrap table {
    display: table; margin: 0 auto; width: 100%;
  }
  
  /* Chart Layouts */
  .chart-layout, .chart-left, .chart-right { 
    display: block; width: 100%; padding: 0; margin: 0 auto 15px; text-align: center; 
  }
  .chart-wrap { margin: 0 auto; text-align: center; }
  
  /* Divisional Chart Grids (which are inline tables with 50% tds) */
  td[style*="width: 50%"] { 
    display: block; width: 100% !important; margin: 0 auto 15px; padding: 0 !important; text-align: center;
  }
  
  /* SVG Logo */
  svg { max-width: 100%; height: auto; margin: 0 auto; display: block; }
  
  /* Fix kv-table wrap */
  .kv-table td { white-space: normal; word-break: break-word; text-align: left; }
  .kv-table td:first-child { width: 45%; font-weight: bold; text-align: left; }
  
  /* Hide the fixed page-footer on mobile screens since it overlays content */
  .page-footer { display: none; }
}
"""


def _esc(v):
    return str(v).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _kv_table(pairs):
    rows = "".join(
        f"<tr><td>{_esc(k)}</td><td>{_esc(v)}</td></tr>" for k, v in pairs
    )
    return f'<table class="kv-table"><tbody>{rows}</tbody></table>'


def _data_table(headers, rows):
    ths = "".join(f"<th>{_esc(h)}</th>" for h in headers)
    trs = ""
    for row in rows:
        tds = "".join(f"<td>{_esc(c)}</td>" for c in row)
        trs += f"<tr>{tds}</tr>"
    return f'<table class="data-table"><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table>'


def _section(title, content, lang="en"):
    return f'<div class="section"><div class="section-title">{_esc(t(title, lang))}</div>{content}</div>'


def _subtitle(txt, lang="en"):
    return f'<div class="subtitle">{_esc(t(txt, lang))}</div>'


# ── Table-Based South Indian Chart ──────────────────────────────────────────

def _planets_to_signs(planets, ascendant, varga_signs=None):
    """Convert planet data to {sign_idx: [("Abbr Deg", color)]} for South Indian chart."""
    short_map = dict(zip(PLANETS, PLANET_SHORT))
    planet_names = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Ascendant"]
    
    PLANET_COLORS = {
        "Sun": "#D32F2F", "Moon": "#000000", "Mars": "#D32F2F",
        "Mercury": "#388E3C", "Jupiter": "#F57C00", "Venus": "#C2185B",
        "Saturn": "#1976D2", "Rahu": "#616161", "Ketu": "#795548",
        "Ascendant": "#795548"
    }
    
    signs = {i: [] for i in range(12)}
    
    if varga_signs is not None:
        for p in planet_names:
            p_sign = varga_signs.get(p)
            if p_sign is None:
                continue
            abbr = short_map.get(p, p[:2]) if p != "Ascendant" else "Asc"
            retro = planets.get(p, {}).get("retrograde", False) if p != "Ascendant" else False
            combust = planets.get(p, {}).get("combust", False) if p != "Ascendant" else False
            suffix = " &reg;" if retro else (" &copy;" if combust else "")
            color = PLANET_COLORS.get(p, "#000")
            signs[p_sign].append((abbr + suffix, color))
    else:
        for p in planet_names:
            if p == "Ascendant":
                sign_idx = ascendant["sign_idx"]
                deg_str = ascendant.get("dms", "00:00").split(":")[0]
                abbr = f"Asc {deg_str}"
                color = PLANET_COLORS["Ascendant"]
                signs[sign_idx].append((abbr, color))
            else:
                pdata = planets[p]
                sign_idx = pdata["sign_idx"]
                deg_str = pdata.get("dms", "00:00").split(":")[0]
                abbr = short_map.get(p, p[:2])
                retro = pdata.get("retrograde", False)
                combust = pdata.get("combust", False)
                suffix = " &reg;" if retro else (" &copy;" if combust else "")
                color = PLANET_COLORS.get(p, "#000")
                signs[sign_idx].append((f"{abbr} {deg_str}{suffix}", color))
                
    return signs


def build_south_indian_chart(asc_sign_idx, planets_by_sign, title="", lang="en"):
    """Build a South Indian style chart using HTML table."""
    cells = {}
    for i in range(12):
        sign_num = i + 1
        planet_html = ""
        for p_str, color in planets_by_sign.get(i, []):
            # Translate planet string (e.g., "Su", "Mo", etc.)
            p_str_translated = t(p_str, lang)
            planet_html += f'<div style="color: {color};">{p_str_translated}</div>'
            
        cells[i] = f'''
        <td style="border: 1pt solid #2C5282; width: 25%; vertical-align: top; padding: 2px; height: 60px;">
            <div style="font-size: 8pt; color: #888; text-align: left; line-height: 1;">{sign_num}</div>
            <div style="font-size: 8.5pt; font-weight: bold; text-align: center; line-height: 1.2; margin-top: 1px;">
                {planet_html}
            </div>
        </td>
        '''
        
    om_html = f'''
    <td colspan="2" rowspan="2" style="border: 1pt solid #2C5282; text-align: center; vertical-align: middle; background: #EBF8FF;">
        <div style="color: #1A365D; font-size: 16pt; font-weight: bold;">&#2384;</div>
        <div style="color: #1A365D; font-size: 9pt; margin-top: 4px;">{t("Lagna", lang)}: {asc_sign_idx + 1}</div>
    </td>
    '''
    
    return f'''
    <div class="chart-wrap">
      <div class="chart-title">{_esc(t(title, lang))}</div>
      <table style="width: 100%; border-collapse: collapse; border: 1.5pt solid #2C5282; table-layout: fixed; background: #fff;">
        <tr>{cells[11]} {cells[0]} {cells[1]} {cells[2]}</tr>
        <tr>{cells[10]} {om_html} {cells[3]}</tr>
        <tr>{cells[9]} {cells[4]}</tr>
        <tr>{cells[8]} {cells[7]} {cells[6]} {cells[5]}</tr>
      </table>
    </div>
    '''


def build_lagna_chart(planets, ascendant, all_vargas, lang="en"):
    """Build the D1 Lagna chart section with HTML chart + side table."""
    lagna_idx = ascendant["sign_idx"]
    planets_by_sign = _planets_to_signs(planets, ascendant)
    chart_html = build_south_indian_chart(lagna_idx, planets_by_sign, title="Lagna Chart (D1)", lang=lang)

    # Build a compact planet-house summary table beside the chart
    rows = []
    for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        pdata = planets[p_name]
        rows.append([t(p_name, lang), str(pdata.get("house", "-")), t(SIGNS[pdata["sign_idx"]], lang), pdata["dms"]])

    table_html = _data_table([t("Planet", lang), t("House", lang), t("Sign", lang), t("Degrees", lang)], rows)

    content = f'''
<div class="chart-layout">
  <div class="chart-left">{chart_html}</div>
  <div class="chart-right">{table_html}</div>
</div>'''
    return _section("Birth Chart — Lagna (D1)", content, lang)



def build_cover(data, lang="en"):
    d = data
    birth_rows = [
        (t("Name", lang), d.get("name", "")),
        (t("Gender", lang), t(d.get("gender", ""), lang)),
        (t("Date of Birth", lang), d.get("dob_display", d.get("dob_str", ""))),
        (t("Time of Birth", lang), d.get("time_str", "")),
        (t("Place of Birth", lang), d.get("full_address", d.get("place_name", ""))),
        (t("Latitude", lang), f"{d.get('lat', 0):.5f} N"),
        (t("Longitude", lang), f"{d.get('lon', 0):.5f} E"),
        (t("Timezone", lang), f"{d.get('tz_str', '')} ({d.get('tz_offset', '')})"),
    ]
    birth_html = '<table style="width: 100%; border: none;">'
    for k, v in birth_rows:
        birth_html += f'<tr><td style="border: none; text-align: left; padding: 2mm; font-weight: bold; color: #2A4365; width: 35%;">{_esc(k)}</td>'
        birth_html += f'<td style="border: none; text-align: left; padding: 2mm; color: #2D3748;">{_esc(v)}</td></tr>'
    birth_html += '</table>'
    
    logo_svg = """<svg version="1.1" xmlns="http://www.w3.org/2000/svg" style="display: block; margin: 0 auto 5mm auto;" viewBox="400 70 1250 1250" width="80" height="80" preserveAspectRatio="xMidYMid meet">
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 1006.96 89.3421 C 1340.84 78.8502 1619.98 341.067 1630.37 674.955 C 1640.76 1008.84 1378.46 1287.9 1044.57 1298.19 C 710.822 1308.47 431.909 1046.3 421.526 712.564 C 411.142 378.824 673.219 99.8294 1006.96 89.3421 z"></path>
<path transform="translate(0,0)" fill="rgb(0,0,0)" d="M 1027.95 113.142 C 1348.81 114.135 1608.04 375.173 1606.81 696.031 C 1605.58 1016.89 1344.35 1275.93 1023.49 1274.46 C 702.973 1273 444.261 1012.1 445.49 691.578 C 446.719 371.056 707.424 112.151 1027.95 113.142 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 738.793 334.456 C 743.418 332.855 765.748 314.73 771.646 310.845 C 787.692 300.274 802.751 291.195 819.861 282.289 C 929.613 226.046 1057.57 217.067 1174.1 257.432 C 1289.61 297.29 1384.5 381.476 1437.84 491.409 C 1488.68 597.798 1495.77 719.884 1457.58 831.442 C 1419.42 941.025 1337.75 1027.86 1233.74 1080.68 C 1008.22 1195.18 723.232 1099.7 611.787 872.871 C 561.8 771.132 558.963 641.002 597.422 534.828 C 627.852 451.591 669.685 395.92 735.194 338.353 C 737.563 336.863 737.004 336.958 738.793 334.456 z"></path>
<path transform="translate(0,0)" fill="rgb(0,0,0)" d="M 1017.4 241.441 C 1020.51 241.236 1023.54 241.259 1026.66 241.274 C 1146.58 241.637 1261.39 289.874 1345.59 375.269 C 1428.06 458.319 1474.06 570.799 1473.42 687.842 C 1473.55 784.775 1440.4 878.815 1379.52 954.244 C 1365.09 972.03 1350.54 986.315 1334.28 1002.33 C 1313.68 996.415 1292.02 990.818 1278.77 972.601 C 1260.57 947.581 1250.28 916.135 1238.81 887.51 L 1199.58 789.958 C 1191.86 770.568 1182.82 746.054 1174.12 727.519 C 1137.4 752.499 1109.33 768.682 1070.1 789.311 C 1089.22 847.467 1115.08 904.306 1132.61 963.038 C 1142.33 995.591 1093.41 998.591 1072.04 1001.56 C 1072.06 1005.09 1071.48 1010.01 1073.22 1012.7 C 1081.2 1013.61 1093.87 1013.22 1102.21 1013.23 L 1153.39 1013.23 L 1322.64 1013.39 C 1255.7 1069.06 1174.44 1104.77 1088.17 1116.45 C 988.486 1129.69 887.211 1109.96 799.787 1060.27 C 772.726 1044.78 756.268 1032.25 731.737 1013.4 C 770.588 1012.61 809.756 1013.6 848.629 1013.32 C 858.137 1013.26 868.825 1013.96 878.137 1012.82 C 880.069 1009.95 880.159 1006.74 879.267 1003.43 C 863.644 996.248 826.463 996.853 819.427 974.367 C 810.336 945.317 836.423 889.364 846.173 862.306 C 871.223 858.382 896.162 851.353 920.315 843.759 C 1055.29 801.32 1261.75 689.518 1329.02 559.331 C 1342.29 533.65 1353.23 502.427 1343.78 473.659 C 1338.22 456.729 1326.69 444.596 1310.79 436.767 C 1256.27 409.914 1180.99 436.14 1127.27 454.581 C 1118.36 457.911 1103.18 461.966 1095.86 466.626 L 1096.35 467.733 C 1105.25 471.258 1147.83 459.043 1158.98 455.756 C 1261.89 425.42 1360.25 463.793 1288.55 581.576 C 1269.93 612.169 1249.3 633.39 1221.84 659.192 C 1122.5 752.561 986.168 813.791 854.65 845.462 C 863.417 818.855 874.6 790.222 884.425 763.952 L 927.412 648.817 C 942.75 608.066 960.797 567.53 967.657 524.65 C 956.227 530.085 946.868 535.343 935.847 541.587 C 933.5 547.61 931.488 553.785 929.404 559.905 C 916.865 596.725 903.858 633.421 890.54 669.97 C 868.073 730.192 844.79 790.107 820.698 849.698 C 771.707 862.262 698.69 841.972 707.185 780.452 C 717.126 708.458 799.562 643.908 856.583 605.429 C 878.875 590.386 903.399 579.563 924.826 563.366 C 925.134 563.099 925.441 562.833 925.749 562.567 C 848.403 596.9 770.157 647.519 714.562 712.129 C 692.847 737.796 668.408 776.275 671.633 811.378 C 677.606 876.392 765.755 875.772 812.938 871.168 C 801.905 900.892 789.704 932.799 776.926 961.786 C 765.588 987.508 744.38 993.735 719.64 1002.02 C 631.686 923.221 583.887 820.056 579.338 702.133 C 575.648 585.109 618.09 471.321 697.516 385.299 C 782.746 293.177 892.975 246.241 1017.4 241.441 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 1016.34 323.688 C 1020.86 329.182 1041.21 383.362 1045.68 394.195 C 1064.7 383.567 1086.12 369.598 1105.25 358.209 C 1097.2 380.172 1088.78 401.994 1079.98 423.667 C 1094.24 424.685 1116.21 425.932 1129.68 428.438 C 1121.53 436.664 1094.86 458.818 1085.24 465.809 C 1097.61 472.045 1107.33 478.339 1118.59 486.097 L 1083.09 493.617 C 1088.86 508.145 1098.34 526.91 1102.68 541.252 C 1087.18 534.175 1071.55 527.393 1055.79 520.909 C 1055.9 529.348 1056.19 537.785 1056.68 546.211 C 1050.34 541.523 1043.97 536.886 1037.56 532.302 C 1031.53 544.834 1025.17 561.797 1019.55 575.064 C 1012.96 560.58 1006.04 546.248 998.793 532.079 C 994.662 536.828 990.616 541.65 986.659 546.544 C 974.525 561.347 967.409 571.387 957 587.154 C 965.546 560.682 969.076 544.124 971.932 516.554 C 953.457 526.776 930.765 536.743 911.288 545.025 C 919.616 526.315 932.834 505.134 944.054 487.842 C 937.403 488.039 922.271 489.902 919.12 483.255 C 922.032 476.9 936.765 475.55 942.911 474.615 C 922.136 461.255 901.525 447.642 881.083 433.779 C 903.976 429.919 926.937 426.477 949.956 423.455 C 942.564 402.05 933.646 379.713 925.721 358.343 C 943.069 366.357 972.203 385.395 990.298 395.628 C 999.639 372.92 1006.2 347.661 1016.34 323.688 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 1060.56 528.546 C 1073.3 534.305 1088.32 540.873 1101.33 545.639 C 1107.42 557.321 1118.5 586.86 1123.88 600.093 C 1137.71 634.078 1151.73 667.981 1165.96 701.799 C 1138.59 724.055 1091.98 749.988 1060.57 765.49 C 1057.86 759.358 1055.01 751.587 1052.48 745.247 C 1043.82 723.842 1035.27 698.947 1026.99 677.072 L 982.871 562.871 C 988.078 556.541 993.501 549.133 998.532 542.57 C 1006.26 556.045 1012.3 570.785 1020.04 584.586 C 1026.92 572.187 1034.68 553.987 1040.58 540.895 L 1060.55 554.358 C 1060.36 545.944 1060.54 537.005 1060.56 528.546 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 479.582 567.802 C 487.986 569.306 487.434 573.079 493.118 573.189 C 502.792 567.157 503.752 566.02 512.782 572.841 C 517.478 573.206 518.924 569.674 522.709 568.641 C 535.037 565.279 535.892 583.076 537.632 590.029 C 541.339 591.527 546.682 587.735 548.672 588.721 C 576.737 602.639 552.347 628.769 540.392 639.474 C 542.71 644.199 547.863 650.211 548.609 654.437 C 542.762 661.823 536.671 653.456 532.972 648.642 C 528.859 652.754 526.696 656.436 520.6 656.063 C 517.788 654.23 517.941 654.41 516.192 651.551 C 516.94 648.184 525.354 639.018 528.056 635.781 C 526.241 627.727 525.272 619.505 525.164 611.25 C 525.15 604.558 526.639 585.111 522.458 581.261 L 519.955 581.889 C 508.746 593.189 525.869 646.75 506.463 638.444 C 499.018 628.746 509.048 587.089 499.971 581.934 C 486.179 585.894 500.076 626.656 491.182 639.164 C 487.676 641.015 489.506 640.589 485.459 640.374 C 476.758 633.784 484.192 596.381 480.914 584.577 C 479.685 580.151 476.536 579.756 472.154 576.748 L 471.82 574.456 C 473.752 570.826 475.915 570.056 479.582 567.802 z"></path>
<path transform="translate(0,0)" fill="rgb(0,0,0)" d="M 543.139 600.614 C 556.238 603.606 546.231 618.672 540.782 624.094 C 539.868 624.658 540.508 624.368 538.699 624.409 C 537.36 620.158 537.502 612.122 537.355 607.371 C 539.168 605.039 541.186 602.839 543.139 600.614 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 992.132 133.427 C 1015.23 133.922 1038.21 133.911 1061.29 133.204 C 1063.58 133.134 1063.48 133.169 1064.8 134.683 C 1065.09 137.868 1065.29 137.783 1064.13 140.693 C 1060.8 143.608 1054.01 144.365 1049.17 145.527 C 1049.02 162.515 1049.03 179.505 1049.2 196.494 C 1055.47 199.385 1058.1 198.502 1063.46 201.544 C 1065.82 205.077 1065.05 204.821 1065.37 209.769 C 1050.93 213.348 1015.71 205.599 999.207 210.845 C 997.043 211.533 995.771 210.67 994.361 209.368 C 993.981 205.986 993.776 205.808 994.649 202.412 C 997.508 199.64 1001.48 199.314 1005.48 198.43 C 1005.8 189.165 1007.29 154.471 1004.54 147.84 C 999.561 142.792 994.503 145.332 990.431 140.285 C 990.37 136.577 990.565 136.631 992.132 133.427 z"></path>
<path transform="translate(0,0)" fill="rgb(0,0,0)" d="M 1018.24 145.206 C 1025.34 145.052 1029.94 144.929 1037.02 145.647 C 1037.03 155.526 1037.7 189.16 1036.12 197.626 C 1030.78 198.539 1024.51 199.496 1019.69 196.904 C 1016.79 190.924 1017.99 154.265 1018.24 145.206 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 1405.98 351.076 C 1423.44 350.978 1425.77 362.077 1424.93 376.785 C 1430.64 374.704 1433.67 373.393 1439.8 372.622 L 1440.68 371.318 C 1446.32 363.019 1451.48 355.704 1462.53 353.627 C 1470.48 352.132 1480.93 357.814 1480.98 366.961 C 1481 370.246 1477.84 379.051 1475.53 381.504 C 1472.37 382.524 1473.96 382.488 1470.62 381.334 C 1466.39 375.714 1469.46 369.763 1464.56 365.216 C 1458.6 365.747 1455.18 371.943 1451.75 376.448 C 1461.53 383.94 1464.05 387.58 1466.97 399.174 C 1465.81 422.709 1449.44 437.51 1425.85 427.345 C 1391.28 412.454 1427.92 371.461 1407.51 362.224 C 1403.74 365.757 1407.64 376.327 1402.46 382.398 L 1400.12 382.212 C 1385.74 372.439 1392.34 357.409 1405.98 351.076 z"></path>
<path transform="translate(0,0)" fill="rgb(0,0,0)" d="M 1434.25 384.913 C 1455.93 383.637 1462.3 407.586 1441.52 418.782 C 1421.31 419.147 1413.78 396.919 1434.25 384.913 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 616.146 334.136 C 648.856 329.402 661.975 362.844 642.833 386.881 C 637.125 394.049 625.272 399.064 623.631 409.247 C 624.581 413.019 623.671 411.433 626.513 414.151 C 638.386 415.97 631.356 403.422 640.449 401.149 L 642.478 402.431 C 654.535 424.454 610.279 443.41 612.044 403.172 C 616.714 394.62 628.244 384.388 635.299 375.677 C 638.44 369.715 639.896 366.932 639.029 360.167 C 638.065 352.639 629.164 341.966 620.793 345 C 596.074 353.957 616.628 394.079 605.441 411.609 C 602.154 416.762 596.319 417.366 590.979 418.501 C 557.121 409.58 565.993 369.33 596.871 375.029 C 596.37 354.987 595.471 342.799 616.146 334.136 z"></path>
<path transform="translate(0,0)" fill="rgb(0,0,0)" d="M 587.035 385.536 C 599.025 384.943 599.819 398.17 591.823 405.414 C 579.286 404.481 579.193 393.128 587.035 385.536 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 531.2 806.151 C 540.248 804.986 546.953 805.44 554.97 810.518 C 561.738 814.805 566.524 821.608 568.271 829.427 C 570.593 839.883 567.885 848.244 562.582 857 C 569.754 857.016 580.908 855.483 585.786 861.003 C 586.727 864.262 586.383 864.377 585.265 867.528 C 579.582 869.823 550.588 868.453 545.043 867.018 C 543.19 861.804 552.381 850.818 554.47 844.678 C 558.336 833.317 555.265 822.042 542.215 818.833 C 537.588 817.74 532.718 818.522 528.667 821.009 C 506.416 834.374 531.213 856.895 529.187 865.734 C 525.417 867.678 520.154 867.763 515.764 868.207 C 511.235 868.437 503.893 868.893 502.17 873.48 L 503.213 875.307 C 507.863 876.985 516.583 875.745 521.519 876.584 C 538.944 879.544 566.859 877.065 583.293 880.78 L 584.424 882.745 C 584.713 886.898 584.941 887.343 583.331 891.016 C 579.642 893.19 507.28 888.858 497.05 887.949 C 493.396 884.604 493.281 867.097 492.785 861.02 C 499.026 858.553 505.004 857.341 511.526 855.814 C 502.724 832.65 507.303 815.392 531.2 806.151 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 1139.37 1133.76 C 1144.89 1134.56 1147.12 1136.46 1151.59 1138.47 C 1153.57 1139.37 1163.21 1133.74 1165.09 1133.61 C 1169.47 1133.31 1173.09 1136.16 1176.11 1138.78 C 1219.76 1113.28 1196.74 1193.6 1204.12 1208.23 C 1210.95 1212.85 1214.85 1204.21 1221.85 1206.41 C 1227.79 1219.37 1209.97 1226.29 1200.59 1220.15 C 1179.77 1206.51 1195.86 1166.87 1188.55 1146.39 C 1168.44 1146.27 1186.82 1196.4 1175.14 1205.85 C 1171.82 1206.8 1171.62 1206.44 1168.35 1205.49 C 1161.61 1195.68 1173.6 1152.18 1161.59 1146.86 C 1147.69 1150.82 1161.06 1196.47 1152.92 1204.22 C 1136.96 1219.39 1143.19 1172.38 1142.35 1165.64 C 1140.81 1153.2 1146.56 1150.9 1132.31 1142.43 C 1131.35 1141.86 1131.85 1140.35 1131.94 1139.45 C 1134.1 1136.23 1135.98 1135.61 1139.37 1133.76 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 659.844 1015.94 C 663.924 1016.77 664.801 1017.86 668.297 1020.49 L 669.488 1021.4 C 673.825 1021.88 678.721 1016.21 681.503 1016.34 C 712.103 1017.78 684.225 1074.49 699.714 1083.74 C 704.424 1083.62 706.411 1081.34 710.617 1078.39 C 720.791 1077.97 717.5 1090.53 710.209 1093.48 C 668.526 1110.34 689.317 1045.15 681.174 1029.05 L 679.356 1028.52 C 669.83 1035.35 672.668 1052.31 672.834 1062.98 C 672.946 1071.13 674.166 1082.05 670.37 1088.75 C 666.994 1090.75 668.809 1090.28 664.664 1089.91 C 653.407 1083.14 666.621 1041.42 657.881 1030.55 C 654.842 1029.82 656.329 1029.75 653.283 1030.99 C 645.485 1040.58 652.122 1074.14 649.392 1086.79 C 648.435 1091.23 642.012 1090.52 638.833 1089.34 C 634.434 1081.17 638.64 1046.03 636.951 1035.16 C 635.484 1025.72 630.958 1028.82 626.566 1025.81 C 626.153 1022.07 626.082 1022.33 627.338 1018.8 C 635.198 1012.85 642.265 1020.93 648.285 1021.2 C 653.102 1018.46 654.612 1017.73 659.844 1015.94 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 1354.69 1013.9 C 1362.23 1015.46 1363.41 1018.02 1368.72 1023.68 C 1374.47 1022.37 1381.72 1007.11 1394.05 1015.94 C 1409.48 1027.52 1397.23 1059.36 1402.84 1075.14 C 1408.01 1089.69 1432.95 1078.53 1420.68 1063.12 C 1412.87 1059.34 1411.18 1065.71 1404.12 1065.5 L 1402.83 1063.68 C 1402.35 1058.15 1403.31 1055.01 1408.66 1052.37 C 1436.59 1038.6 1447.25 1079.03 1421.39 1092.45 C 1410.12 1096.03 1404.21 1095.68 1395.36 1087.73 C 1390.52 1095.96 1380.28 1108.38 1369.4 1103.73 L 1368.94 1101.35 C 1372.29 1091.93 1378.19 1092.32 1384.34 1084.95 C 1391.48 1076.39 1389.35 1039.91 1387.3 1029.05 C 1386.48 1028.08 1385.92 1026.79 1384.65 1026.95 C 1365.37 1029.42 1378.77 1059.26 1369.63 1067.71 C 1365.9 1068.96 1365.84 1068.7 1362.1 1067.97 C 1357.03 1060.81 1366.63 1033.51 1356.09 1027.14 C 1353.72 1025.71 1351.2 1023.61 1349.99 1021.14 C 1350.36 1016.8 1350.62 1017.91 1354.69 1013.9 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 1507.63 567.304 C 1531.03 578.058 1533.56 603.272 1537.26 606.212 C 1544.87 603.227 1558.37 560.333 1575.78 572.538 C 1575.99 574.496 1576.47 576.194 1574.8 577.857 C 1564.13 588.455 1560.34 592.175 1554.48 606.216 C 1561.13 606.02 1573.16 604.214 1575.95 611.809 C 1571.42 618.789 1560.93 618.205 1553.73 618.417 C 1555.5 623.124 1556.36 625.655 1559.2 629.948 C 1563.89 637.06 1575.76 643.877 1575.58 651.895 C 1573.31 655.321 1574.84 654.114 1570.59 655.329 C 1568.88 654.56 1567.2 653.725 1565.56 652.824 C 1554.33 646.551 1547.21 636.943 1543.32 624.863 C 1541.89 620.414 1542.48 618.553 1538.02 616.397 L 1539.96 617.016 L 1536.8 617.159 C 1532.91 622.46 1532.53 631.469 1528.52 637.505 C 1520.54 649.531 1512.47 652.699 1499.48 655.557 C 1499.16 653.709 1498.08 648.075 1499 647.114 C 1512.18 633.283 1516.62 639.051 1522.43 619.122 C 1515.85 617.632 1510.88 618.065 1504.11 616.287 C 1502.58 613.576 1503.13 611.692 1503.4 608.551 C 1507.73 604.854 1517.33 606.177 1523.53 606.301 C 1518.72 589.003 1507.67 584.095 1504.83 574.512 C 1505.06 570.363 1505.03 570.589 1507.63 567.304 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 932.313 1140.58 C 935.94 1140.15 939.67 1139.27 942.916 1140.64 C 943.558 1148.17 943.526 1157.15 943.537 1164.76 C 943.548 1172.02 945.55 1185.49 938.433 1189.18 C 935.018 1188.64 934.315 1187.52 931.782 1185.16 C 930.281 1180.85 930.724 1164.74 930.7 1159.06 C 920.916 1169.73 910.948 1180.23 900.802 1190.55 C 906.833 1196.64 912.454 1202.34 918.183 1208.75 L 910.97 1217.06 C 904.135 1211.39 898.698 1206.05 892.379 1199.87 L 872.12 1220.03 C 870.045 1221.94 870.244 1221.98 867.518 1222.53 C 864.036 1221.68 861.967 1218.64 859.477 1215.88 C 866.57 1207.78 875.511 1198.81 883.063 1190.91 C 877.439 1185.9 871.839 1180.42 866.369 1175.2 C 868.966 1172.34 872.252 1169.37 875.08 1166.69 L 892.132 1181.51 C 901.411 1171.9 910.799 1162.39 920.295 1152.99 C 912.076 1152.76 910.377 1152.86 902.165 1155.17 C 899.725 1155.85 897.825 1154.65 896.071 1153.33 C 890.632 1135.4 921.043 1141.48 931.189 1140.67 L 932.313 1140.58 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 1232.04 190.102 C 1250.54 188.979 1256.83 195.778 1261.04 213.28 C 1261.8 211.667 1262.6 210.078 1263.46 208.515 C 1275.22 187.208 1297.91 186.884 1304.31 213.071 C 1303.37 217.611 1302.2 222.485 1299.64 226.395 C 1295.15 233.229 1284.45 235.653 1277.7 230.733 C 1276.98 223.85 1288.3 222.547 1293.18 212.816 C 1293.1 210.646 1293.4 209.681 1291.26 208.257 C 1278.54 199.809 1272.48 214.578 1268.7 223.674 C 1266 232.614 1260.39 266.372 1250.75 265.97 C 1245.98 259.864 1253.63 224.249 1248.59 212.005 C 1244.86 202.926 1235.87 195.422 1228.05 208.586 C 1224.24 215.012 1237.79 217.51 1239.95 223.071 C 1239.38 226.409 1239.33 226.16 1236.93 228.628 C 1223.02 234.498 1202.15 203.302 1232.04 190.102 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 805.164 183.114 C 814.329 183.555 841.389 192.564 844.884 200.434 C 844.479 204.818 845.251 202.976 842.876 206.31 C 835.516 208.906 822.335 198.311 813.31 196.664 C 806.881 195.491 805.744 195.689 799.238 195.89 C 804.084 204.286 805.408 209.116 805.526 218.827 C 802.885 225.764 798.742 231.721 791.639 234.699 C 786.456 236.864 780.612 236.807 775.473 234.541 C 769.958 232.114 765.749 227.438 763.912 221.699 C 755.81 196.314 787.58 187.609 805.164 183.114 z"></path>
<path transform="translate(0,0)" fill="rgb(0,0,0)" d="M 782.201 201.629 C 795.839 203.381 796.459 217.401 785.182 224.71 C 769.255 222.816 772.492 209.483 782.201 201.629 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 828.671 214.162 C 835.876 214.415 845.739 217.789 848.447 225.201 C 854.734 242.406 838.929 257.193 823.683 261.939 C 807.768 266.892 796.57 265.963 781.756 258.428 C 777.06 254.927 768.588 250.314 771.458 243.52 C 779.669 240.29 800.78 259.108 813.544 252.228 C 812.05 248.08 809.453 244.45 808.453 241.174 C 806.964 236.212 807.59 230.855 810.182 226.37 C 814.424 219.069 820.892 216.116 828.671 214.162 z"></path>
<path transform="translate(0,0)" fill="rgb(0,0,0)" d="M 829.118 225.799 C 843.128 229.946 839.845 239.489 830.111 246.499 C 815.394 243.767 818.002 232.163 829.118 225.799 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 1490.47 854.745 C 1498.35 855.392 1501.48 863.502 1505.18 869.739 C 1520.38 852.543 1521.33 853.074 1533.63 871.884 C 1539.2 865.495 1542.45 861.988 1548.72 856.356 C 1553.79 861.361 1570.5 885.018 1558.86 888.454 C 1551.94 886.039 1550.35 881.076 1546.6 874.546 L 1541.08 880.516 C 1537.68 884.995 1535.51 887.197 1531.63 891.104 C 1527.34 886.269 1521.97 878.119 1518.1 872.595 C 1513.17 877.978 1507.99 884.607 1503.42 890.334 C 1498.13 884.794 1494.99 879.359 1491.21 872.812 L 1474.06 888.444 C 1471.27 886.06 1469.17 883.325 1466.82 880.516 C 1472.82 871.723 1482.77 862.425 1490.47 854.745 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 1520.33 814.461 C 1524.02 818.82 1529.76 827.902 1533.15 832.957 C 1538.77 826.747 1543.51 821.347 1550.36 816.487 C 1554.68 820.786 1558.79 826.462 1562.14 831.54 C 1564.98 835.846 1574.81 847.01 1564.07 848.352 C 1556.11 845.705 1553.73 842.054 1548.55 835.732 L 1547.3 835.938 C 1541.8 841.678 1537.41 846.133 1531.49 851.399 C 1527.41 846.977 1522.29 839.087 1518.7 833.897 C 1512.56 839.985 1509.37 843.083 1502.49 848.18 C 1498.19 843.961 1495.28 839.258 1491.9 834.284 C 1485.2 840.784 1479.96 846.969 1471.16 850.2 L 1468.94 848.846 C 1470.7 837.088 1484.17 824.579 1492.25 815.538 C 1498.53 818.645 1501.29 824.269 1505.03 830.161 C 1510.51 823.96 1514.07 819.78 1520.33 814.461 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 803.163 1082.42 C 806.588 1084.6 805.94 1083.25 806.898 1086.11 C 802.119 1097.95 793.871 1112.89 787.987 1124.75 C 775.661 1149.91 762.977 1174.89 749.94 1199.69 C 748.997 1199.23 747.27 1198.1 746.317 1197.51 C 745.693 1191.5 784.167 1122.27 788.672 1110.63 C 790.449 1106.03 800.112 1088.04 803.163 1082.42 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 652.206 950.044 C 655.182 953.016 654.652 951.384 654.973 954.682 C 650.628 958.846 629.917 972.656 624.053 976.744 L 555.103 1024.8 C 552.343 1021.72 552.922 1023.39 552.375 1019.98 C 556.178 1015.99 573.802 1004.45 579.381 1000.43 C 603.127 983.305 628.639 967.324 652.206 950.044 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 1269.77 1071.27 C 1272.03 1072.22 1272.49 1072.01 1273.86 1074.56 C 1282.35 1090.32 1292.77 1107.87 1300.65 1123.78 C 1309.56 1141.8 1323.62 1164.23 1331.44 1181.94 L 1329.13 1185.58 C 1324.78 1183.36 1307.09 1148.04 1303.79 1141.87 L 1267.56 1074.7 L 1269.77 1071.27 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 1399.88 950.294 C 1406.47 952.986 1499.06 1018.43 1500.48 1021.18 L 1498.72 1025.24 C 1494.28 1023.3 1400.16 957.373 1398.38 954.609 L 1399.88 950.294 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 550.738 724.574 C 558.714 723.82 562.437 722.682 569.236 726.968 L 568.719 728.842 L 569.695 727.539 C 568.987 728.095 568.278 728.652 567.57 729.209 C 537.173 731.77 495.224 734.102 465.755 736.215 C 458.166 737.02 453.944 738.358 447.562 734.329 L 447.946 732.755 C 454.305 730.737 474.233 729.795 481.697 729.246 C 504.702 727.567 527.716 726.01 550.738 724.574 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 1484.76 723.943 C 1506.8 723.345 1577.82 730.493 1602.75 732.365 C 1603.72 732.438 1604.23 735.717 1604.62 737.195 C 1579.24 737.499 1551.38 733.288 1525.85 732.361 C 1513.17 731.9 1499.27 731.016 1486.67 729.848 C 1484.47 727.721 1485.18 727.836 1484.76 723.943 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 502.491 460.407 C 508.488 461.952 533.938 474.339 540.686 477.598 C 561.344 487.577 583.57 497.159 603.936 507.474 C 605.773 510.357 605.23 509.321 604.709 513.589 C 591.96 510.319 518.701 473.517 502.495 465.71 C 501.727 465.341 502.361 461.854 502.491 460.407 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 1036.95 1136.34 C 1040.22 1136.89 1039.14 1136.32 1041.68 1138.13 C 1042.79 1146.55 1042.14 1172.01 1042.12 1181.66 L 1042.13 1268.95 C 1039.39 1268.41 1039.16 1268.66 1037.16 1266.84 C 1036.11 1255.47 1036.79 1233.42 1036.8 1221.44 L 1036.95 1136.34 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 881.694 131.243 C 883.535 131.699 885.465 131.839 886.061 134.07 C 890.142 149.352 915.993 236.242 913.004 244.9 C 911.236 244.635 910.961 244.468 909.253 243.908 C 906.681 238.885 898.191 202.831 896.736 195.813 C 894.31 184.111 880.212 139.613 881.694 131.243 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 1547.46 461.915 C 1550.26 463.399 1549.42 462.308 1550.29 465.107 C 1547.32 469.908 1464.9 506.587 1452.53 512.372 L 1452.07 512.446 C 1449.32 511.128 1450.55 512.048 1448.9 508.927 C 1451.45 504.603 1536.69 466.77 1547.46 461.915 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 735.194 338.353 C 731.485 335.339 726.813 329.693 723.666 325.972 C 704.072 302.801 684.242 279.875 664.034 257.249 C 662.569 255.609 662.996 255.095 662.755 252.933 L 664.097 251.526 C 669.398 252.734 732.178 325.584 738.793 334.456 C 737.004 336.958 737.563 336.863 735.194 338.353 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 1165.74 131.353 C 1168.29 132.217 1168.41 131.982 1169.91 134.122 C 1169.57 139.608 1161.41 171.35 1159.43 179.246 C 1154.06 200.65 1149.83 223.782 1144.29 244.849 C 1142.88 244.151 1141.73 243.36 1140.41 242.523 C 1138.84 237.633 1162.34 140.653 1165.74 131.353 z"></path>
<path transform="translate(0,0)" fill="rgb(253,196,57)" d="M 1389.16 251.754 C 1390.27 252.36 1390.8 253.13 1391.75 254.107 C 1391.63 254.927 1391.51 255.748 1391.39 256.568 C 1370.99 281.037 1342.93 314.178 1323.05 337.912 C 1320.77 336.545 1321.56 337.146 1319.88 334.94 C 1321.4 327.692 1380.48 261.215 1389.16 251.754 z"></path>
</svg>"""
    
    return f"""
<div class="cover">
  <div class="cover-header">
    {logo_svg}
    <div class="cover-brand">Authentic Astrology</div>
  </div>
  <div class="cover-body">
    
    <div class="birth-card">
      <div class="birth-card-title">{_esc(t("Birth Details", lang))}</div>
      {birth_html}
    </div>
  </div>
</div>"""


# ── Panchanga ─────────────────────────────────────────────────────────────────

def build_panchanga(p, lang="en"):
    pairs = [
        (t("Sunrise", lang), p.get("sunrise", "")), (t("Sunset", lang), p.get("sunset", "")),
        (t("Day Length", lang), p.get("day_length", "")), (t("Night Length", lang), p.get("night_length", "")),
        (t("Kali Year", lang), p.get("kali_year", "")), (t("Saka Year", lang), p.get("saka_year", "")),
        (t("Hindu Year", lang), t(p.get("hindu_year", ""), lang)), (t("Ayana", lang), t(p.get("ayana", ""), lang)),
        (t("Rithu (Season)", lang), t(p.get("ritu", ""), lang)), (t("Hindu Month", lang), t(p.get("hindu_month", ""), lang)),
        (t("Tithi", lang), t(p.get("tithi", ""), lang)), (t("Weekday", lang), t(p.get("weekday", ""), lang)),
        (t("Vedic Weekday", lang), t(p.get("vedic_weekday", ""), lang)),
        (t("Nakshatra, Pada", lang), t(p.get("nakshatra_pada", ""), lang)),
        (t("Moon Sign", lang), f"{t(p.get('moon_sign', ''), lang)} {t('Sign', lang)}"),
        (t("Yoga", lang), t(p.get("yoga", ""), lang)), (t("Karana", lang), t(p.get("karana", ""), lang)),
        (t("Janmakshar", lang), p.get("janmakshar", "")),
    ]
    return _section("Panchanga Details", _kv_table(pairs), lang)


# ── Avakahada ─────────────────────────────────────────────────────────────────

def build_avakahada(p, lang="en"):
    from kundali_gen.data.constants import SIGN_VARNA, SIGN_VASHYA
    pairs = [
        (t("Nakshatra", lang), t(p.get("nakshatra", ""), lang)), (t("Nadi", lang), p.get("nadi", "")),
        (t("Yoni", lang), p.get("yoni", "")), (t("Gana", lang), p.get("gana", "")),
        (t("Moon Sign", lang), t(p.get("moon_sign", ""), lang)), (t("Rashi Lord", lang), t(p.get("rashi_lord", ""), lang)),
        (t("Varna Kuta", lang), SIGN_VARNA.get(p.get("moon_sign_idx", 0), "")),
        (t("Vashya Kuta", lang), SIGN_VASHYA.get(p.get("moon_sign_idx", 0), "")),
    ]
    return _section("Avakahada Chakra", _kv_table(pairs), lang)


# ── Lucky Things & Jaimini Karakas ──────────────────────────────────────────

def build_lucky_things(ascendant, jaimini_karakas, lang="en"):
    lt = get_lucky_things(ascendant["sign_idx"])
    pairs = [
        (t("Lucky Days", lang), ", ".join([t(d, lang) for d in lt.get("days", [])])),
        (t("Lucky Planets", lang), ", ".join([t(p, lang) for p in lt.get("planets", [])])),
        (t("Friendly Signs", lang), ", ".join([t(s, lang) for s in lt.get("friendly_signs", [])])),
        (t("Friendly Ascendant", lang), ", ".join([t(a, lang) for a in lt.get("friendly_asc", [])])),
        (t("Life Stone", lang), lt.get("life_stone", "")),
        (t("Lucky Stone", lang), lt.get("lucky_stone", "")),
        (t("Punya Stone", lang), lt.get("punya_stone", "")),
        (t("Favorable Deity", lang), ", ".join(lt.get("deity", []))),
        (t("Favorable Metal", lang), lt.get("metal", "")),
        (t("Favorable Color", lang), ", ".join(lt.get("color", []))),
        (t("Favorable Direction", lang), ", ".join(lt.get("direction", []))),
        (t("Favorable Time", lang), lt.get("time", "")),
        (t("Favorable Numbers", lang), ", ".join(lt.get("numbers", []))),
    ]
    lucky_html = _kv_table(pairs)

    rows = []
    for karaka, planet in jaimini_karakas.items():
        p_short = PLANET_SHORT[PLANETS.index(planet)] if planet in PLANETS else planet[:2]
        sthira = STHIRA_KARAKAS.get(planet, "")
        rows.append([t(p_short, lang), karaka, sthira])
    jaimini_html = _data_table([t("Planet", lang), t("Chara Karaka", lang), t("Sthira Karaka", lang)], rows)

    return _section("Lucky Things", lucky_html + _subtitle("Jaimini Karakas", lang) + jaimini_html, lang)


# ── Planetary Positions ────────────────────────────────────────────────────────

def build_planets(planets, ascendant, lang="en"):
    order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Ascendant"]
    rows = []
    for p in order:
        data = ascendant if p == "Ascendant" else planets[p]
        rx = "-" if p == "Ascendant" else (t("(R)", lang) if data.get("retrograde") else (t("(C)", lang) if data.get("combust") else "-"))
        rows.append([t(p, lang), rx, t(SIGNS[data["sign_idx"]], lang), data["dms"],
                     str(planets[p].get("house", "-")) if p != "Ascendant" else "-"])
    t1 = _data_table([t("Planet", lang), t("Rx/Comb", lang), t("Sign", lang), t("Deg/Min/Sec", lang), t("House", lang)], rows)

    rows2 = []
    for p in order:
        data = ascendant if p == "Ascendant" else planets[p]
        nak_idx = data["nakshatra_idx"]
        pada = data["pada"]
        nak = NAKSHATRAS[nak_idx]
        nav = data.get("nav_sign_idx", (nak_idx * 4 + pada - 1) % 12)
        rows2.append([t(p, lang), f"{t(nak['name'], lang)}-{pada}", t(nak["lord"], lang), t(SIGNS[nav], lang), t(SIGN_LORD[nav], lang)])
    t2 = _data_table([t("Planet", lang), t("Nakshatra/Pada", lang), t("Nak. Lord", lang), t("Navamsha Sign", lang), t("Navamsha Lord", lang)], rows2)

    return _section("Planetary Positions", t1 + _subtitle("Planetary Table (Nakshatra)", lang) + t2, lang)


# ── Bhava Table ───────────────────────────────────────────────────────────────

def build_bhava(sripati_cusps, lang="en"):
    rows = []
    for i, cusp in enumerate(sripati_cusps[:12]):
        sign_idx = int(cusp / 30) % 12
        deg = cusp % 30
        d = int(deg); m = int((deg - d) * 60); s = int(((deg - d) * 60 - m) * 60)
        rows.append([t(BHAVA_NAMES[i], lang), t(SIGNS[sign_idx], lang), f"{d:02d}:{m:02d}:{s:02d}"])
    return _section("Bhava Table", _data_table([t("House", lang), t("Sign", lang), t("Deg/Min/Sec", lang)], rows), lang)


# ── Divisional Charts ─────────────────────────────────────────────────────────

def build_divisional_charts(planets, ascendant, all_vargas, lang="en"):
    varga_keys = ["D1", "D2", "D9", "D3", "D4", "D7", "D10", "D12", "D16", "D20",
                  "D24", "D27", "D30", "D40", "D45", "D60"]
    blocks = ""
    for i in range(0, len(varga_keys), 4):
        chunk = varga_keys[i:i+4]
        
        # Build 2x2 grid using a table (xhtml2pdf compat)
        grid_html = '<table style="width: 100%; border: none;">'
        
        # Row 1 (first two charts)
        grid_html += '<tr>'
        for j in range(2):
            if j < len(chunk):
                vk = chunk[j]
                v_signs = all_vargas[vk]
                asc_idx = v_signs.get("Ascendant", ascendant["sign_idx"])
                p_signs = _planets_to_signs(planets, ascendant, v_signs)
                title = VARGA_NAMES.get(vk, vk)
                chart_html = build_south_indian_chart(asc_idx, p_signs, title=title, lang=lang)
                meaning = VARGA_MEANING.get(vk, "")
                meaning_html = f'<div class="varga-meaning">{_esc(meaning[:80])}</div>' if meaning else ""
                grid_html += f'<td style="width: 50%; padding: 3mm; vertical-align: top; border: none;">{chart_html}{meaning_html}</td>'
            else:
                grid_html += '<td style="width: 50%; border: none;"></td>'
        grid_html += '</tr>'
        
        # Row 2 (next two charts)
        grid_html += '<tr>'
        for j in range(2, 4):
            if j < len(chunk):
                vk = chunk[j]
                v_signs = all_vargas[vk]
                asc_idx = v_signs.get("Ascendant", ascendant["sign_idx"])
                p_signs = _planets_to_signs(planets, ascendant, v_signs)
                title = VARGA_NAMES.get(vk, vk)
                chart_html = build_south_indian_chart(asc_idx, p_signs, title=title, lang=lang)
                meaning = VARGA_MEANING.get(vk, "")
                meaning_html = f'<div class="varga-meaning">{_esc(meaning[:80])}</div>' if meaning else ""
                grid_html += f'<td style="width: 50%; padding: 3mm; vertical-align: top; border: none;">{chart_html}{meaning_html}</td>'
            else:
                grid_html += '<td style="width: 50%; border: none;"></td>'
        grid_html += '</tr>'
        
        grid_html += '</table>'
        blocks += _section(f"Divisional Charts ({chunk[0]}-{chunk[-1]})", grid_html, lang)
    return blocks


# ── Ashtakavarga ──────────────────────────────────────────────────────────────

def build_ashtakavarga(av_data, lang="en"):
    src_map = {"Sun": "Su", "Moon": "Mo", "Mercury": "Me", "Venus": "Ve",
               "Mars": "Ma", "Jupiter": "Ju", "Saturn": "Sa", "Lagna": "As"}
    headers = [t("Sign", lang)] + [t(v, lang) for v in src_map.values()] + ["Total"]
    blocks = ""
    for planet_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        bindus = av_data.get(planet_name, {}).get("bindus", [0] * 12)
        contribs = av_data.get(planet_name, {}).get("contributions", {})
        rows = []
        for s_idx, sname in enumerate(SIGN_SHORT):
            row = [t(sname, lang)]
            for full_name in src_map:
                c_val = contribs.get(full_name, [0] * 12)
                row.append(str(c_val[s_idx]) if len(c_val) > s_idx else "0")
            row.append(str(bindus[s_idx]))
            rows.append(row)
        blocks += _section(f"{t(planet_name, lang)} Ashtakavarga", _data_table(headers, rows), lang)
    return blocks


# ── Dasha ─────────────────────────────────────────────────────────────────────

def build_dasha(dasha_rows_3, lang="en"):
    from kundali_gen.core.dasha import format_dasha_date
    rows_by = {}
    for row in dasha_rows_3:
        key = (row["MD"], row["BH"])
        rows_by.setdefault(key, []).append(row)

    blocks = ""
    for (md, bh), rows in rows_by.items():
        table_rows = []
        for r in rows:
            md_s = PLANET_SHORT[PLANETS.index(r["MD"])] if r["MD"] in PLANETS else r["MD"]
            bh_s = PLANET_SHORT[PLANETS.index(r["BH"])] if r["BH"] in PLANETS else r["BH"]
            pr_s = PLANET_SHORT[PLANETS.index(r["PR"])] if r["PR"] in PLANETS else r["PR"]
            table_rows.append([t(md_s, lang), t(bh_s, lang), t(pr_s, lang), format_dasha_date(r["start"]), f"{r['age']:.1f}"])
        blocks += _section(f"{t('MD', lang)}: {t(md, lang)} — {t('BH', lang)}: {t(bh, lang)}", _data_table([t("MD", lang), t("BH", lang), t("PR", lang), t("Start Date", lang), t("Age", lang)], table_rows), lang)
    return blocks


# ── Doshas ────────────────────────────────────────────────────────────────────

def build_doshas(kaal_sarp, mangal, lang="en"):
    ks_found, ks_msg = kaal_sarp
    mg_lagna = mangal.get("lagna", {})
    mg_moon = mangal.get("moon", {})
    mg_venus = mangal.get("venus", {})
    content = f"""
    <div style="margin-bottom:5mm">
      <div class="subtitle">{_esc(t('Kaal Sarp Dosha', lang))}</div>
      <p style="margin:2mm 0">{_esc(ks_msg)}</p>
    </div>
    <div>
      <div class="subtitle">{_esc(t('Mangal Dosha', lang))}</div>
      <p style="margin:2mm 0">{_esc(mg_lagna.get('message',''))}</p>
      <p style="margin:2mm 0">{_esc(mg_moon.get('message',''))}</p>
      <p style="margin:2mm 0">{_esc(mg_venus.get('message',''))}</p>
    </div>"""
    return _section("Doshas and Remedies", content, lang)


# ── Predictions ───────────────────────────────────────────────────────────────

def build_predictions(data, panchanga, ascendant, av_data, lang="en"):
    dasha_lord = t(data.get("dasha_lord", ""), lang)
    balance_str = data.get("balance_str", "")
    lagna_sign = t(SIGNS[ascendant["sign_idx"]], lang)
    
    lagna_html = f"""
    <div style="margin-bottom: 5mm;">
      <div class="subtitle">{_esc(t('Lagna Analysis', lang))}</div>
      <p style="line-height:1.5;">You are born in {lagna_sign} Ascendant. 
      The lord of this house is {t(SIGN_LORD[ascendant['sign_idx']], lang)}. 
      Your Moon Sign is {t(panchanga.get('moon_sign',''), lang)}. 
      You are born in 3rd quarter of {t(panchanga.get('nakshatra',''), lang)} Nakshatra. 
      You are born in maha dasha of {dasha_lord}.</p>
    </div>
    <div style="margin-bottom: 5mm;">
      <div class="subtitle">{_esc(t('Dasha Balance at Birth', lang))}</div>
      <p style="line-height:1.5;">{dasha_lord} Dasha {balance_str}</p>
    </div>
    <div style="margin-bottom: 5mm;">
      <div class="subtitle">{_esc(t('Birth Nakshatra', lang))}</div>
      <p style="line-height:1.5;">You are born under the {t(panchanga.get('nakshatra',''), lang)} Nakshatra. 
      This nakshatra bestows intelligence, curiosity and strong communication skills.</p>
    </div>
    """
    blocks = _section("Horoscope Predictions", lagna_html, lang)

    for md_lord in DASHA_ORDER:
        md_lord_t = t(md_lord, lang)
        md_text = f"This {md_lord_t} Mahadasha will bring significant changes. "
        md_text += f"During this period, the significations of {md_lord_t} will be prominent in your life. "
        md_text += "Consult a qualified Vedic astrologer for personalized guidance."
        blocks += _section(f"{md_lord} Mahadasha Predictions", f'<div class="subtitle">{md_lord_t} Mahadasha Overview</div><p style="line-height:1.5;">{_esc(md_text)}</p>', lang)

    samudaya = av_data.get("Samudaya", {}).get("bindus", [0]*12)
    av_rows = []
    for h_idx, pts in enumerate(samudaya):
        house_name = t(BHAVA_NAMES[h_idx], lang)
        quality = "Excellent" if pts >= 30 else ("Good" if pts >= 25 else "Demands Attention")
        av_rows.append([f"{h_idx+1}. {house_name}", str(pts), quality])
    
    blocks += _section("Natal Samudaya Ashtakavarga Predictions", _data_table([t("House", lang), t("Points", lang), t("Quality", lang)], av_rows), lang)
    return blocks


# ── Master builder ────────────────────────────────────────────────────────────

def build_html(data, panchanga, planets, ascendant, all_vargas,
               dasha_rows_3, sookshma_1yr, av_data, kaal_sarp, mangal, jaimini_karakas, charttype="full", language="en"):
    
    sookshma_html = ""
    if sookshma_1yr:
        from kundali_gen.core.dasha import format_dasha_date
        s_rows = []
        for r in sookshma_1yr:
            s_rows.append([t(r["MD"], language), t(r["BH"], language), t(r["PR"], language), t(r["SD"], language), format_dasha_date(r["start"]), f"{r['age']:.1f}"])
        sookshma_html = _section("Vimshottari Dashas: Sookshma Dasha (Next 1 Year)", _data_table([t("MD", language), t("BH", language), t("PR", language), t("SD", language), t("Start Date", language), t("Age", language)], s_rows), language)

    if charttype == "custom":
        body = (
            build_cover(data, language)
            + build_panchanga(panchanga, language)
            + build_lagna_chart(planets, ascendant, all_vargas, language)
            + build_planets(planets, ascendant, language)
            + build_bhava(data.get("sripati_cusps", [0] * 12), language)
            + build_dasha(dasha_rows_3, language)
            + sookshma_html
        )
    else:
        body = (
            build_cover(data, language)
            + build_lagna_chart(planets, ascendant, all_vargas, language)
            + build_panchanga(panchanga, language)
            + build_avakahada(panchanga, language)
            + build_lucky_things(ascendant, jaimini_karakas, language)
            + build_planets(planets, ascendant, language)
            + build_bhava(data.get("sripati_cusps", [0] * 12), language)
            + build_divisional_charts(planets, ascendant, all_vargas, language)
            + build_ashtakavarga(av_data, language)
            + build_dasha(dasha_rows_3, language)
            + sookshma_html
            + build_doshas(kaal_sarp, mangal, language)
            + build_predictions(data, panchanga, ascendant, av_data, language)
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Authentic Astrology — Kundali Report</title>
<meta name="description" content="Authentic Kundali Report generated by Authentic Astrology">
<style>{CSS_STYLES}</style>
<style media="screen">{MOBILE_CSS}</style>
</head>
<body>
<div class="page-footer">Authentic Astrology &nbsp;|&nbsp; Page <pdf:pagenumber></div>
{body}
</body>
</html>"""
