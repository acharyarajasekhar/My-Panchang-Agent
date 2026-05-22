"""
panchang/calculations.py
────────────────────────
Orchestrates all Panchangam elements for a given date.

Returns a PanchangamResult dataclass containing every field needed by the
formatter, with all end-times expressed as IST strings.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime

from panchang.ephemeris import (
    count_sankrantis_between,
    date_to_jd_noon,
    datetime_to_jd,
    find_boundary_jd,
    find_last_new_moon_jd,
    find_next_new_moon_jd,
    get_sunrise,
    get_sunset,
    jd_to_datetime,
    moon_longitude,
    sun_longitude,
)
from panchang.data.tithi import get_tithi, get_tithi_by_index, TITHI_SPAN_DEG
from panchang.data.nakshatra import get_nakshatra, get_nakshatra_by_index, NAKSHATRA_SPAN_DEG
from panchang.data.yoga import get_yoga, get_yoga_by_index, YOGA_SPAN_DEG
from panchang.data.karana import get_karana, get_karana_by_position
from panchang.data.masa import get_masa
from panchang.data.samvatsara import get_samvatsara

# ── Telugu weekday names ───────────────────────────────────────────────
_WEEKDAY_TE = [
    "సోమవారం",     # Monday    (0)
    "మంగళవారం",   # Tuesday   (1)
    "బుధవారం",     # Wednesday (2)
    "గురువారం",    # Thursday  (3)
    "శుక్రవారం",  # Friday    (4)
    "శనివారం",     # Saturday  (5)
    "ఆదివారం",    # Sunday    (6)
]
# Python weekday(): Monday=0 … Sunday=6 — matches above list order.

# ── Sanskrit weekday names ─────────────────────────────────────────────
_WEEKDAY_SA = [
    "Indhu Vasarah",       # Monday    (0) — Moon
    "Bhauma Vasarah",      # Tuesday   (1) — Mars
    "Saumya Vasarah",      # Wednesday (2) — Mercury
    "Bruhaspathi Vasarah", # Thursday  (3) — Jupiter
    "Brughu Vasarah",      # Friday    (4) — Venus
    "Sthira Vasarah",      # Saturday  (5) — Saturn
    "Bhanu Vasarah",       # Sunday    (6) — Sun
]
# Python weekday(): Monday=0 … Sunday=6 — matches above list order.

# ── Sanskrit weekday names in Telugu script ────────────────────────────
_WEEKDAY_SA_TE = [
    "ఇందు వాసర",        # Monday    (0) — Moon
    "భౌమ వాసర",          # Tuesday   (1) — Mars
    "సౌమ్య వాసర",        # Wednesday (2) — Mercury
    "బృహస్పతి వాసర",    # Thursday  (3) — Jupiter
    "బృగు వాసర",         # Friday    (4) — Venus
    "స్థిర వాసర",       # Saturday  (5) — Saturn
    "భాను వాసర",        # Sunday    (6) — Sun
]
# Python weekday(): Monday=0 … Sunday=6 — matches above list order.


# ─────────────────────────────────────────────────────────────────────
# Result types
# ─────────────────────────────────────────────────────────────────────

@dataclass
class TimedElement:
    """An element (Tithi/Nakshatra/Yoga/Karana) with its end time and optional next element."""
    name_en: str
    name_te: str
    ends_at: str          # e.g. "08:14 AM" or "Next day"
    is_inauspicious: bool = False
    next_name_en: str | None = None  # Next element name (if same day)
    next_name_te: str | None = None  # Next element name in Telugu
    next_ends_at: str | None = None  # Next element end time
    next_next_name_en: str | None = None  # Element after next (if next also same day)
    next_next_name_te: str | None = None  # Element after next in Telugu


@dataclass
class PanchangamResult:
    # ── Date ──────────────────────────────────────────────────────────
    gregorian_date: date
    weekday_en: str
    weekday_sa: str
    weekday_sa_te: str
    weekday_te: str

    # ── Cycle / calendar ──────────────────────────────────────────────
    samvatsara_en: str
    samvatsara_te: str
    ayana_en: str
    ayana_te: str
    ritu_en: str
    ritu_te: str
    masa_en: str
    masa_te: str
    masa_status_en: str
    masa_status_te: str
    paksha_en: str
    paksha_te: str

    # ── Five elements (Pancha Anga) ────────────────────────────────────
    tithi: TimedElement
    nakshatra: TimedElement
    yoga: TimedElement
    karana: TimedElement

    # ── Key timings (strings, formatted as "HH:MM AM/PM IST") ─────────
    sunrise: str
    sunset: str
    # Rahu Kalam / Yamagandam / Gulika / Durmuhurtam supplied by timings.py


# ─────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────

def _fmt_time(dt: datetime, target_date: date | None = None) -> str:
    """Format a datetime as '07:42 AM' (IST), rounding up if seconds present.
    If target_date is provided and time is on next day, prefix with 'Next day'.
    """
    # Round up to next minute if seconds > 0
    if dt.second > 0:
        from datetime import timedelta
        dt = dt + timedelta(minutes=1)
    
    time_str = dt.strftime("%I:%M %p")
    
    # Add day indicator if needed
    if target_date and dt.date() > target_date:
        return f"Next day {time_str}"
    return time_str


def _elongation(jd: float) -> float:
    """Moon–Sun elongation in degrees [0, 360), monotonically increasing."""
    return (moon_longitude(jd) - sun_longitude(jd)) % 360.0


def _yoga_value(jd: float) -> float:
    """Sun + Moon combined longitude [0, 360), monotonically increasing."""
    return (sun_longitude(jd) + moon_longitude(jd)) % 360.0


def _end_time_with_datetime(
    value_fn,
    current_val: float,
    span: float,
    jd_start: float,
    search_days: float = 3.0,
    target_date: date | None = None,
) -> tuple[str, datetime | None]:
    """
    Find when value_fn next crosses the next span-multiple boundary.
    Returns (formatted_time_string, datetime_object).
    datetime_object is None if calculation fails.
    """
    idx = math.floor(current_val / span)
    boundary = (idx + 1) * span
    if boundary >= 360.0:
        boundary -= 360.0

    jd_hi = jd_start + search_days
    try:
        jd_end = find_boundary_jd(value_fn, boundary, jd_start, jd_hi)
        dt = jd_to_datetime(jd_end)
        formatted = _fmt_time(dt, target_date=target_date)
        return formatted, dt
    except Exception:
        return "Next day", None


def _end_time(
    value_fn,
    current_val: float,
    span: float,
    jd_start: float,
    search_days: float = 3.0,
    target_date: date | None = None,
) -> str:
    """
    Find when value_fn next crosses the next span-multiple boundary after
    current_val, searching up to *search_days* ahead of *jd_start*.

    Returns formatted IST time string, or "Next day" on failure.
    If target_date is provided, shows "Next day" prefix for times after midnight.
    """
    formatted, _ = _end_time_with_datetime(value_fn, current_val, span, jd_start, search_days, target_date)
    return formatted


def _karana_end_time(jd_start: float, elongation_at_start: float, target_date: date | None = None) -> str:
    """
    Karana spans 6° of elongation (half a Tithi).
    Find when elongation next crosses the next multiple of 6°.
    """
    return _end_time(_elongation, elongation_at_start, 6.0, jd_start, target_date=target_date)


def _shaka_year(target: date, s_lon: float) -> int:
    """
    Compute Samvatsara cycle year (60-year repeating pattern).
    
    Formula: (CE year - 7) % 60 gives the index in the 60-year Samvatsara cycle.
    But we account for Ugadi (Chaitra Shukla Pratipada, March/April) — the new
    Samvatsara doesn't begin until Ugadi. Before Ugadi, use the prior year's index.
    """
    ce = target.year
    if target.month < 4:
        return ce - 68
    if target.month > 4:
        return ce - 67
    # In April, use sidereal solar ingress proximity as a practical Ugadi anchor.
    if s_lon < 10.0:
        return ce - 68
    return ce - 67


# ─────────────────────────────────────────────────────────────────────
# Main calculation entry point
# ─────────────────────────────────────────────────────────────────────

def calculate(target: date) -> PanchangamResult:
    """
    Compute the full Panchangam for *target* (a datetime.date object).

    All times are in IST (Asia/Kolkata).
    """
    # ── Sunrise & sunset ──────────────────────────────────────────────
    sunrise_dt = get_sunrise(target)
    sunset_dt  = get_sunset(target)
    jd_sunrise = datetime_to_jd(sunrise_dt)

    # ── Planetary positions at sunrise ────────────────────────────────
    s_lon = sun_longitude(jd_sunrise)
    m_lon = moon_longitude(jd_sunrise)
    elong = (m_lon - s_lon) % 360.0

    # ── Weekday ───────────────────────────────────────────────────────
    wd_py = target.weekday()        # Mon=0 … Sun=6
    weekday_en = target.strftime("%A")
    weekday_sa = _WEEKDAY_SA[wd_py]
    weekday_sa_te = _WEEKDAY_SA_TE[wd_py]
    weekday_te = _WEEKDAY_TE[wd_py]

    # ── Samvatsara ────────────────────────────────────────────────────
    shaka = _shaka_year(target, s_lon)
    sam_en, sam_te = get_samvatsara(shaka)

    # ── Masa, Ritu, Ayana ─────────────────────────────────────────────
    # Lunar month is named after the rashi where the Sun was at the new moon
    # that started the month. Adhik (extra) months occur when no Sankranti
    # (rashi entry) occurs between two successive new moons.
    jd_noon = date_to_jd_noon(target)
    jd_new_moon_curr = find_last_new_moon_jd(jd_noon)
    jd_new_moon_prev = find_last_new_moon_jd(jd_new_moon_curr - 25)
    jd_new_moon_next = find_next_new_moon_jd(jd_new_moon_curr)
    
    s_lon_curr = sun_longitude(jd_new_moon_curr)

    # The current month is named after the rashi at current new moon
    masa_info = get_masa(s_lon_curr)

    prev_sankrantis = count_sankrantis_between(jd_new_moon_prev, jd_new_moon_curr)
    curr_sankrantis = count_sankrantis_between(jd_new_moon_curr, jd_new_moon_next)

    masa_status_en = ""
    masa_status_te = ""
    if curr_sankrantis == 0:
        masa_status_en = "Adhika"
        masa_status_te = "అధిక"
    elif prev_sankrantis == 0 and curr_sankrantis >= 1:
        masa_status_en = "Nija"
        masa_status_te = "నిజ"

    # ── Paksha ────────────────────────────────────────────────────────
    tithi_info = get_tithi(m_lon, s_lon)
    paksha_en = tithi_info.paksha_en
    paksha_te = tithi_info.paksha_te

    # ── Tithi (with end time) ─────────────────────────────────────────
    tithi_name_en = f"{tithi_info.paksha_en} {tithi_info.english}"
    tithi_name_te = f"{tithi_info.paksha_te} {tithi_info.telugu}"
    tithi_end     = _end_time(_elongation, elong, TITHI_SPAN_DEG, jd_sunrise, target_date=target)
    
    # Show next Tithi if current one ends on the same day
    next_tithi_name_en = None
    next_tithi_name_te = None
    next_tithi_end = None
    next_next_tithi_name_en = None
    next_next_tithi_name_te = None
    
    if "Next day" not in tithi_end:
        next_tithi_info = get_tithi_by_index(tithi_info.index + 1)
        next_tithi_name_en = f"{next_tithi_info.paksha_en} {next_tithi_info.english}"
        next_tithi_name_te = f"{next_tithi_info.paksha_te} {next_tithi_info.telugu}"
        
        # Compute when next tithi ends
        next_elong = ((math.floor(elong / TITHI_SPAN_DEG) + 1) * TITHI_SPAN_DEG) % 360.0
        next_tithi_end = _end_time(_elongation, next_elong, TITHI_SPAN_DEG, jd_sunrise, target_date=target)
        
        # If next tithi also ends same day, get the one after that
        if "Next day" not in next_tithi_end:
            next_next_tithi_info = get_tithi_by_index(tithi_info.index + 2)
            next_next_tithi_name_en = f"{next_next_tithi_info.paksha_en} {next_next_tithi_info.english}"
            next_next_tithi_name_te = f"{next_next_tithi_info.paksha_te} {next_next_tithi_info.telugu}"
    
    tithi_elem    = TimedElement(
        name_en=tithi_name_en,
        name_te=tithi_name_te,
        ends_at=tithi_end,
        next_name_en=next_tithi_name_en,
        next_name_te=next_tithi_name_te,
        next_ends_at=next_tithi_end,
        next_next_name_en=next_next_tithi_name_en,
        next_next_name_te=next_next_tithi_name_te,
    )

    # ── Nakshatra (with end time) ──────────────────────────────────────
    nak_idx, nak_tuple = get_nakshatra(m_lon)
    nak_end  = _end_time(moon_longitude, m_lon, NAKSHATRA_SPAN_DEG, jd_sunrise, target_date=target)
    
    # Show next Nakshatra if current one ends on the same day
    next_nak_name_en = None
    next_nak_name_te = None
    next_nak_end = None
    next_next_nak_name_en = None
    next_next_nak_name_te = None
    
    if "Next day" not in nak_end:
        next_nak_en, next_nak_te, _ = get_nakshatra_by_index(nak_idx + 1)
        next_nak_name_en = next_nak_en
        next_nak_name_te = next_nak_te
        
        # Compute when next nakshatra ends
        next_m_lon = ((math.floor(m_lon / NAKSHATRA_SPAN_DEG) + 1) * NAKSHATRA_SPAN_DEG) % 360.0
        next_nak_end = _end_time(moon_longitude, next_m_lon, NAKSHATRA_SPAN_DEG, jd_sunrise, target_date=target)
        
        # If next nakshatra also ends same day, get the one after that
        if "Next day" not in next_nak_end:
            next_next_nak_en, next_next_nak_te, _ = get_nakshatra_by_index(nak_idx + 2)
            next_next_nak_name_en = next_next_nak_en
            next_next_nak_name_te = next_next_nak_te
    
    nak_elem = TimedElement(
        name_en=nak_tuple[0],
        name_te=nak_tuple[1],
        ends_at=nak_end,
        next_name_en=next_nak_name_en,
        next_name_te=next_nak_name_te,
        next_ends_at=next_nak_end,
        next_next_name_en=next_next_nak_name_en,
        next_next_name_te=next_next_nak_name_te,
    )

    # ── Yoga (with end time) ───────────────────────────────────────────
    yoga_val = (s_lon + m_lon) % 360.0
    yoga_idx, yoga_tuple = get_yoga(s_lon, m_lon)
    yoga_end  = _end_time(_yoga_value, yoga_val, YOGA_SPAN_DEG, jd_sunrise, target_date=target)
    
    # Show next Yoga if current one ends on the same day
    next_yoga_name_en = None
    next_yoga_name_te = None
    next_yoga_end = None
    next_next_yoga_name_en = None
    next_next_yoga_name_te = None
    
    if "Next day" not in yoga_end:
        next_yoga_en, next_yoga_te, next_yoga_inauspicious = get_yoga_by_index(yoga_idx + 1)
        next_yoga_name_en = next_yoga_en
        next_yoga_name_te = next_yoga_te
        
        # Compute when next yoga ends
        next_yoga_val = ((math.floor(yoga_val / YOGA_SPAN_DEG) + 1) * YOGA_SPAN_DEG) % 360.0
        next_yoga_end = _end_time(_yoga_value, next_yoga_val, YOGA_SPAN_DEG, jd_sunrise, target_date=target)
        
        # If next yoga also ends same day, get the one after that
        if "Next day" not in next_yoga_end:
            next_next_yoga_en, next_next_yoga_te, _ = get_yoga_by_index(yoga_idx + 2)
            next_next_yoga_name_en = next_next_yoga_en
            next_next_yoga_name_te = next_next_yoga_te
    
    yoga_elem = TimedElement(
        name_en=yoga_tuple[0],
        name_te=yoga_tuple[1],
        ends_at=yoga_end,
        is_inauspicious=yoga_tuple[2],
        next_name_en=next_yoga_name_en,
        next_name_te=next_yoga_name_te,
        next_ends_at=next_yoga_end,
        next_next_name_en=next_next_yoga_name_en,
        next_next_name_te=next_next_yoga_name_te,
    )

    # ── Karana (with end time) ────────────────────────────────────────
    kar_en, kar_te = get_karana(tithi_info.index, elong)
    kar_end  = _karana_end_time(jd_sunrise, elong, target_date=target)
    
    # Show next Karana if current one ends on the same day
    next_kar_name_en = None
    next_kar_name_te = None
    next_kar_end = None
    next_next_kar_name_en = None
    next_next_kar_name_te = None
    
    if "Next day" not in kar_end:
        # Calculate current Karana position and get next one
        half = 0 if (elong % 12.0) < 6.0 else 1
        karana_pos = tithi_info.index * 2 + half
        next_kar_en, next_kar_te = get_karana_by_position(karana_pos + 1)
        next_kar_name_en = next_kar_en
        next_kar_name_te = next_kar_te
        
        # Compute when next karana ends (next 6° elongation boundary)
        next_elong = ((math.floor(elong / 6.0) + 1) * 6.0) % 360.0
        next_kar_end = _karana_end_time(jd_sunrise, next_elong, target_date=target)
        
        # If next karana also ends same day, get the one after that
        if "Next day" not in next_kar_end:
            next_next_kar_en, next_next_kar_te = get_karana_by_position(karana_pos + 2)
            next_next_kar_name_en = next_next_kar_en
            next_next_kar_name_te = next_next_kar_te
    
    kar_elem = TimedElement(
        name_en=kar_en,
        name_te=kar_te,
        ends_at=kar_end,
        is_inauspicious=(kar_en == "Vishti"),
        next_name_en=next_kar_name_en,
        next_name_te=next_kar_name_te,
        next_ends_at=next_kar_end,
        next_next_name_en=next_next_kar_name_en,
        next_next_name_te=next_next_kar_name_te,
    )

    return PanchangamResult(
        gregorian_date=target,
        weekday_en=weekday_en,
        weekday_sa=weekday_sa,
        weekday_sa_te=weekday_sa_te,
        weekday_te=weekday_te,

        samvatsara_en=sam_en,
        samvatsara_te=sam_te,
        ayana_en=masa_info.ayana_en,
        ayana_te=masa_info.ayana_te,
        ritu_en=masa_info.ritu_en,
        ritu_te=masa_info.ritu_te,
        masa_en=masa_info.english,
        masa_te=masa_info.telugu,
        masa_status_en=masa_status_en,
        masa_status_te=masa_status_te,
        paksha_en=paksha_en,
        paksha_te=paksha_te,

        tithi=tithi_elem,
        nakshatra=nak_elem,
        yoga=yoga_elem,
        karana=kar_elem,

        sunrise=_fmt_time(sunrise_dt),
        sunset=_fmt_time(sunset_dt),
    )
