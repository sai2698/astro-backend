"""
Vimshottari Dasha calculations: Mahadasha, Bhukti (Antardasha), Pratyantar, Sookshma.
"""
from datetime import datetime, timedelta
from kundali_gen.data.constants import DASHA_YEARS, DASHA_ORDER, DASHA_TOTAL, NAKSHATRA_DASHA_LORD, NAKSHATRAS

def get_dasha_balance(moon_long, birth_dt):
    """
    Calculate Dasha balance at birth.
    Returns: (dasha_lord, balance_years_float, balance_str, dasha_start_dt)
    """
    nak_span = 360.0 / 27
    nak_idx = int(moon_long / nak_span)
    pos_in_nak = moon_long % nak_span
    fraction_elapsed = pos_in_nak / nak_span

    dasha_lord = NAKSHATRAS[nak_idx]["lord"]
    total_years = DASHA_YEARS[dasha_lord]
    years_elapsed = fraction_elapsed * total_years
    balance_years = total_years - years_elapsed

    # Dasha start = birth_dt - years_elapsed
    days_elapsed = years_elapsed * 365.25
    dasha_start = birth_dt - timedelta(days=days_elapsed)

    return dasha_lord, balance_years, _years_to_str(balance_years), dasha_start

def _years_to_str(years_float):
    total_days = int(round(years_float * 365.25))
    y = total_days // 365
    m = (total_days % 365) // 30
    d = (total_days % 365) % 30
    return f"{y}Y, {m}M, {d}D"

def _add_years(dt, years_float):
    """Add fractional years to a datetime."""
    days = years_float * 365.25
    return dt + timedelta(days=days)

def generate_vimshottari_dasha(birth_dt, moon_long, levels=3):
    """
    Generate complete Vimshottari Dasha table up to specified levels (2=Bhukti, 3=Pratyantar, 4=Sookshma).
    Returns: list of dicts with MD, BH, PR, SD keys and start_date.
    """
    dasha_lord, balance_years, balance_str, first_dasha_start = get_dasha_balance(moon_long, birth_dt)

    # Build the dasha sequence starting from dasha_lord
    start_idx = DASHA_ORDER.index(dasha_lord)
    sequence = DASHA_ORDER[start_idx:] + DASHA_ORDER[:start_idx]

    rows = []
    current_dt = first_dasha_start

    for md_idx, md_lord in enumerate(sequence):
        md_years = DASHA_YEARS[md_lord]
        md_end = _add_years(current_dt, md_years)

        if levels >= 2:
            # Bhukti starts from same planet as MD, then rotates
            bh_start_idx = DASHA_ORDER.index(md_lord)
            bh_sequence = DASHA_ORDER[bh_start_idx:] + DASHA_ORDER[:bh_start_idx]
            bh_current = current_dt

            for bh_lord in bh_sequence:
                bh_years = (DASHA_YEARS[md_lord] * DASHA_YEARS[bh_lord]) / DASHA_TOTAL
                bh_end = _add_years(bh_current, bh_years)

                if levels >= 3:
                    pr_start_idx = DASHA_ORDER.index(bh_lord)
                    pr_sequence = DASHA_ORDER[pr_start_idx:] + DASHA_ORDER[:pr_start_idx]
                    pr_current = bh_current

                    for pr_lord in pr_sequence:
                        pr_years = (DASHA_YEARS[md_lord] * DASHA_YEARS[bh_lord] * DASHA_YEARS[pr_lord]) / (DASHA_TOTAL * DASHA_TOTAL)
                        pr_end = _add_years(pr_current, pr_years)

                        if levels >= 4:
                            sd_start_idx = DASHA_ORDER.index(pr_lord)
                            sd_sequence = DASHA_ORDER[sd_start_idx:] + DASHA_ORDER[:sd_start_idx]
                            sd_current = pr_current

                            for sd_lord in sd_sequence:
                                sd_years = (DASHA_YEARS[md_lord] * DASHA_YEARS[bh_lord] * DASHA_YEARS[pr_lord] * DASHA_YEARS[sd_lord]) / (DASHA_TOTAL ** 3)
                                rows.append({
                                    "MD": md_lord, "BH": bh_lord, "PR": pr_lord, "SD": sd_lord,
                                    "start": sd_current,
                                    "age": (sd_current - birth_dt).days / 365.25
                                })
                                sd_current = _add_years(sd_current, sd_years)
                        else:
                            rows.append({
                                "MD": md_lord, "BH": bh_lord, "PR": pr_lord,
                                "start": pr_current,
                                "age": (pr_current - birth_dt).days / 365.25
                            })
                        pr_current = pr_end
                else:
                    rows.append({
                        "MD": md_lord, "BH": bh_lord,
                        "start": bh_current,
                        "age": (bh_current - birth_dt).days / 365.25
                    })
                bh_current = bh_end
        else:
            rows.append({
                "MD": md_lord,
                "start": current_dt,
                "age": (current_dt - birth_dt).days / 365.25
            })

        current_dt = md_end

    return rows, dasha_lord, balance_str

def format_dasha_date(dt):
    return dt.strftime("%d.%m.%Y")

def format_dasha_date_long(dt):
    return dt.strftime("%d/%m/%Y %I:%M:%S %p")
