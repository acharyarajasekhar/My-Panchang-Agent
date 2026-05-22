"""
panchang/timings.py
────────────────────
Computes all inauspicious / auspicious time windows for a given date:
  • Rahu Kalam
  • Yamagandam
  • Gulika Kalam  (Mandi)
  • Durmuhurtam   (two windows)

All windows are derived from the precise local sunrise and sunset times,
following the classic South Indian / Telugu almanac rules.

──────────────────────────────────────────────────────────────────────
Traditional rules (day = sunrise → sunset, split into 8 equal parts)
──────────────────────────────────────────────────────────────────────
Rahu Kalam slot (1-based, out of 8):
  Mon=2, Tue=7, Wed=5, Thu=6, Fri=4, Sat=3, Sun=8

Yamagandam slot (1-based, out of 8):
  Mon=4, Tue=3, Wed=2, Thu=1, Fri=7, Sat=6, Sun=5

Gulika Kalam slot (1-based, out of 8):
  Mon=6, Tue=5, Wed=4, Thu=3, Fri=2, Sat=1, Sun=7

Durmuhurtam: two fixed windows per weekday, offset in ghatikas
  (1 ghatika = 24 clock-minutes; measured from sunrise).
──────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from panchang.ephemeris import (
    datetime_to_jd,
    find_boundary_jd,
    get_sunrise,
    get_sunset,
    get_lunar_rise,
    get_lunar_set,
    jd_to_datetime,
    moon_longitude,
)
from panchang.data.nakshatra import NAKSHATRA_SPAN_DEG


# ─────────────────────────────────────────────────────────────────────
# Result type
# ─────────────────────────────────────────────────────────────────────

@dataclass
class TimeWindow:
    start: str   # "HH:MM AM/PM"
    end: str     # "HH:MM AM/PM"

    def __str__(self) -> str:
        return f"{self.start} – {self.end}"


@dataclass
class DailyTimings:
    sunrise: str
    sunset: str
    lunar_rise: str
    lunar_set: str
    varjyam: list[str]
    rahu_kalam: TimeWindow
    yamagandam: TimeWindow
    gulika_kalam: TimeWindow
    durmuhurtam_1: TimeWindow
    durmuhurtam_2: TimeWindow


# ─────────────────────────────────────────────────────────────────────
# Weekday lookup tables
# Python weekday():  Mon=0 Tue=1 Wed=2 Thu=3 Fri=4 Sat=5 Sun=6
# Slot index is 0-based (slot 0 = first 1/8 of the day)
# ─────────────────────────────────────────────────────────────────────

# Rahu Kalam — which 1/8 slot (0-indexed)?
_RAHU_SLOT = [1, 6, 4, 5, 3, 2, 7]   # Mon … Sun

# Yamagandam — which 1/8 slot (0-indexed)?
_YAMA_SLOT = [3, 2, 1, 0, 6, 5, 4]   # Mon … Sun

# Gulika Kalam — which 1/8 slot (0-indexed)?
_GULIKA_SLOT = [5, 4, 3, 2, 1, 0, 6] # Mon … Sun

# Durmuhurtam — (start_ghatika, duration_ghatikas) × 2 windows per weekday
# 1 ghatika = 24 clock-minutes measured from sunrise
_DURMUHURTAM_GHATIKAS: dict[int, list[tuple[int, int]]] = {
    0: [(6,  2), (20, 2)],  # Monday
    1: [(18, 2), (29, 2)],  # Tuesday
    2: [(8,  2), (28, 2)],  # Wednesday
    3: [(14, 2), (30, 2)],  # Thursday
    4: [(10, 2), (24, 2)],  # Friday
    5: [(8,  2), (22, 2)],  # Saturday
    6: [(26, 2), (34, 2)],  # Sunday
}

_GHATIKA_MINUTES = 24   # 1 ghatika = 24 clock minutes (fixed)

# Tyajya start offsets (in ghatikas from Nakshatra start), Ashwini..Revati.
# Varjyam duration is 4 ghatikas, scaled by actual Nakshatra duration.
_VARJYAM_START_GHATI = [
  50, 24, 30, 40, 14, 21, 30, 20, 32,
  30, 20, 18, 21, 20, 14, 14, 10, 14,
  56, 24, 20, 10, 10, 18, 16, 24, 30,
]
_VARJYAM_DURATION_GHATI = 4


# ─────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────

def _fmt(dt: datetime) -> str:
    """Format a datetime as '07:42 AM' (without rounding)."""
    return dt.strftime("%I:%M %p")


def _fmt_rounded(dt: datetime) -> str:
    """Format a datetime as '07:42 AM', rounding up if seconds present."""
    # Round up to next minute if seconds > 0
    if dt.second > 0:
        from datetime import timedelta
        dt = dt + timedelta(minutes=1)
    return dt.strftime("%I:%M %p")


def _fmt_for_target_day(dt: datetime, target: date) -> str:
    """Format a datetime for target day, without rounding."""
    base = _fmt(dt)
    if dt.date() < target:
        return f"Prev day {base}"
    if dt.date() > target:
        return f"Next day {base}"
    return base


def _fmt_for_target_day_rounded(dt: datetime, target: date) -> str:
    """Format a datetime for target day, rounding up end times if seconds present."""
    base = _fmt_rounded(dt)
    if dt.date() < target:
        return f"Prev day {base}"
    if dt.date() > target:
        return f"Next day {base}"
    return base


def _slot_window(
    sunrise: datetime,
    sunset: datetime,
    slot_index: int,
    total_slots: int = 8,
) -> TimeWindow:
    """
    Return the TimeWindow for a given 0-based slot index when the day
    (sunrise→sunset) is divided into *total_slots* equal parts.
    """
    day_seconds = (sunset - sunrise).total_seconds()
    slot_duration = timedelta(seconds=day_seconds / total_slots)
    start = sunrise + slot_duration * slot_index
    end   = start + slot_duration
    return TimeWindow(start=_fmt(start), end=_fmt_rounded(end))


def _durmuhurtam_window(
    sunrise: datetime,
    start_ghatika: int,
    duration_ghatikas: int,
) -> TimeWindow:
    """
    Build a Durmuhurtam window from a ghatika offset from sunrise.
    1 ghatika = 24 minutes (clock time, not proportional to day length).
    """
    start = sunrise + timedelta(minutes=start_ghatika * _GHATIKA_MINUTES)
    end   = start   + timedelta(minutes=duration_ghatikas * _GHATIKA_MINUTES)
    return TimeWindow(start=_fmt(start), end=_fmt_rounded(end))


def _nakshatra_index(jd: float) -> int:
    return int(moon_longitude(jd) / NAKSHATRA_SPAN_DEG) % 27


def _find_current_nakshatra_start(jd_probe: float) -> tuple[float, int]:
    idx = _nakshatra_index(jd_probe)
    boundary = idx * NAKSHATRA_SPAN_DEG
    start_jd = find_boundary_jd(moon_longitude, boundary, jd_probe - 3.0, jd_probe)
    return start_jd, idx


def _find_nakshatra_end(start_jd: float, idx: int) -> float:
    next_boundary = ((idx + 1) % 27) * NAKSHATRA_SPAN_DEG
    # Nakshatra duration is ~1 day; 2 days gives safe search margin.
    return find_boundary_jd(moon_longitude, next_boundary, start_jd + 1e-6, start_jd + 2.0)


def _compute_varjyam_windows(target: date, tzinfo) -> list[str]:
    day_start = datetime.combine(target, datetime.min.time(), tzinfo=tzinfo)
    day_end = day_start + timedelta(days=1)
    jd_day_start = datetime_to_jd(day_start)
    jd_day_end = datetime_to_jd(day_end)

    segment_start_jd, idx = _find_current_nakshatra_start(jd_day_start)
    windows: list[str] = []

    while segment_start_jd < jd_day_end + 2.0:
        segment_end_jd = _find_nakshatra_end(segment_start_jd, idx)
        segment_span = segment_end_jd - segment_start_jd

        start_frac = _VARJYAM_START_GHATI[idx] / 60.0
        duration_frac = _VARJYAM_DURATION_GHATI / 60.0

        varjyam_start_jd = segment_start_jd + segment_span * start_frac
        varjyam_end_jd = varjyam_start_jd + segment_span * duration_frac

        overlaps = not (varjyam_end_jd <= jd_day_start or varjyam_start_jd >= jd_day_end)
        if overlaps:
            vs = jd_to_datetime(varjyam_start_jd)
            ve = jd_to_datetime(varjyam_end_jd)
            windows.append(
                f"{_fmt_for_target_day(vs, target)} – {_fmt_for_target_day_rounded(ve, target)}"
            )

        if segment_start_jd > jd_day_end and not overlaps:
            break

        segment_start_jd = segment_end_jd
        idx = (idx + 1) % 27

    return windows


# ─────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────

def get_timings(target: date) -> DailyTimings:
    """
    Compute all daily inauspicious time windows for *target*.

    Returns a DailyTimings dataclass with all windows formatted as IST strings.
    """
    sunrise = get_sunrise(target)
    sunset  = get_sunset(target)
    lunar_rise = get_lunar_rise(target)
    lunar_set = get_lunar_set(target)

    wd = target.weekday()   # Mon=0 … Sun=6

    rahu   = _slot_window(sunrise, sunset, _RAHU_SLOT[wd])
    yama   = _slot_window(sunrise, sunset, _YAMA_SLOT[wd])
    gulika = _slot_window(sunrise, sunset, _GULIKA_SLOT[wd])
    varjyam = _compute_varjyam_windows(target, sunrise.tzinfo)

    (dg1_start, dg1_dur), (dg2_start, dg2_dur) = _DURMUHURTAM_GHATIKAS[wd]
    durm1 = _durmuhurtam_window(sunrise, dg1_start, dg1_dur)
    durm2 = _durmuhurtam_window(sunrise, dg2_start, dg2_dur)

    return DailyTimings(
        sunrise=_fmt(sunrise),
        sunset=_fmt(sunset),
        lunar_rise=_fmt(lunar_rise),
        lunar_set=_fmt(lunar_set),
        varjyam=varjyam,
        rahu_kalam=rahu,
        yamagandam=yama,
        gulika_kalam=gulika,
        durmuhurtam_1=durm1,
        durmuhurtam_2=durm2,
    )
