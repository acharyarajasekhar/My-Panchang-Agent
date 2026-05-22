"""
panchang/ephemeris.py
─────────────────────
Thin wrapper around Skyfield for all raw astronomical data.

All longitudes returned are SIDEREAL (Nirayana) using the Lahiri ayanamsa,
which is the standard for Vedic / Telugu Panchangam calculations.

Dependency: skyfield >= 1.46
"""

from __future__ import annotations

import math
from datetime import date, datetime, timedelta

import pytz
from skyfield.api import load, Topos
from skyfield import almanac
from skyfield.framelib import ecliptic_frame

# ── Lahiri ayanamsa (Chitrapaksha) ─────────────────────────────────────
# The official Indian government standard (as of 1956 Revision).
# Lahiri ayanamsa value in 2000.0 (J2000): ~23° 51' 03" = 23.85083...°
# Change per year: ~50.288 arcsec
_LAHIRI_2000_DEG = 23.85083333
_LAHIRI_CHANGE_PER_YEAR = 50.288 / 3600.0  # degrees/year


def _lahiri_ayanamsa(jd: float) -> float:
    """
    Compute Lahiri ayanamsa for a given Julian Day.
    
    The ayanamsa increases at ~50.288 arcseconds per year.
    Returns the value in degrees (to be subtracted from tropical longitudes).
    """
    # Years since J2000.0
    year_2000 = 2000.0 + (jd - 2451545.0) / 365.25
    years_since_2000 = year_2000 - 2000.0
    return _LAHIRI_2000_DEG + (_LAHIRI_CHANGE_PER_YEAR * years_since_2000)


def _datetime_to_time(dt: datetime):
    """Convert an aware datetime into a Skyfield Time object."""
    if dt.tzinfo is None:
        raise ValueError("Expected timezone-aware datetime")
    utc_dt = dt.astimezone(pytz.utc)
    sec_frac = utc_dt.second + utc_dt.microsecond / 1_000_000.0
    return ts.utc(
        year=utc_dt.year,
        month=utc_dt.month,
        day=utc_dt.day,
        hour=utc_dt.hour,
        minute=utc_dt.minute,
        second=sec_frac,
    )


# ── Load Skyfield ephemerides ──────────────────────────────────────────
ts = load.timescale()
eph = load("de421.bsp")  # Planetary ephemeris
earth = eph["earth"]
sun = eph["sun"]
moon = eph["moon"]

# ── Geo constants ──────────────────────────────────────────────────────
from config import LATITUDE, LONGITUDE, ALTITUDE, TIMEZONE

_TZ = pytz.timezone(TIMEZONE)
# Create the observer location using Topos
_OBSERVER = Topos(latitude_degrees=LATITUDE, longitude_degrees=LONGITUDE,
                  elevation_m=ALTITUDE)


# ─────────────────────────────────────────────────────────────────────
# Julian Day helpers
# ─────────────────────────────────────────────────────────────────────

def datetime_to_jd(dt: datetime) -> float:
    """Convert a timezone-aware (or naive IST) datetime → Julian Day (UT)."""
    if dt.tzinfo is None:
        dt = _TZ.localize(dt)
    t = _datetime_to_time(dt)
    return float(t.tt)


def jd_to_datetime(jd: float) -> datetime:
    """Convert a Julian Day (UT) → timezone-aware IST datetime."""
    # Create a Time object from Julian Day (TT scale)
    t = ts.tt_jd(jd)
    utc_dt = t.utc_datetime()
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(_TZ)


def date_to_jd_noon(target: date) -> float:
    """Julian Day for local noon on *target* (good seed for rise_trans searches)."""
    noon_local = _TZ.localize(datetime(target.year, target.month, target.day, 12, 0, 0))
    return datetime_to_jd(noon_local)


# ─────────────────────────────────────────────────────────────────────
# Planet longitude helpers  (sidereal / Nirayana via Lahiri ayanamsa)
# ─────────────────────────────────────────────────────────────────────

def sun_longitude(jd: float) -> float:
    """Sidereal Sun longitude in degrees [0, 360) at Julian Day *jd* (UT)."""
    t = ts.tt_jd(jd)
    apparent = earth.at(t).observe(sun).apparent()
    _, lon, _ = apparent.frame_latlon(ecliptic_frame)
    lon_tropical = lon.degrees % 360.0

    ayanamsa = _lahiri_ayanamsa(jd)
    lon_sidereal = (lon_tropical - ayanamsa) % 360.0
    return lon_sidereal


def moon_longitude(jd: float) -> float:
    """Sidereal Moon longitude in degrees [0, 360) at Julian Day *jd* (UT)."""
    t = ts.tt_jd(jd)
    apparent = earth.at(t).observe(moon).apparent()
    _, lon, _ = apparent.frame_latlon(ecliptic_frame)
    lon_tropical = lon.degrees % 360.0

    ayanamsa = _lahiri_ayanamsa(jd)
    lon_sidereal = (lon_tropical - ayanamsa) % 360.0
    return lon_sidereal


def moon_speed(jd: float) -> float:
    """Moon's daily motion in degrees/day (used for end-time estimates)."""
    lon_now = moon_longitude(jd)
    lon_tomorrow = moon_longitude(jd + 1.0)
    speed = (lon_tomorrow - lon_now) % 360.0
    if speed > 180:
        speed -= 360.0
    return speed


def sun_speed(jd: float) -> float:
    """Sun's daily motion in degrees/day."""
    lon_now = sun_longitude(jd)
    lon_tomorrow = sun_longitude(jd + 1.0)
    speed = (lon_tomorrow - lon_now) % 360.0
    if speed > 180:
        speed -= 360.0
    return speed


def jupiter_longitude(jd: float) -> float:
    """Sidereal Jupiter longitude (used for Samvatsara calculation)."""
    t = ts.tt_jd(jd)
    jupiter = eph["jupiter barycenter"]
    apparent = earth.at(t).observe(jupiter).apparent()
    _, lon, _ = apparent.frame_latlon(ecliptic_frame)
    lon_tropical = lon.degrees % 360.0

    ayanamsa = _lahiri_ayanamsa(jd)
    lon_sidereal = (lon_tropical - ayanamsa) % 360.0
    return lon_sidereal



# ─────────────────────────────────────────────────────────────────────
# Sunrise & Sunset  (topocentric, standard horizon refraction)
# ─────────────────────────────────────────────────────────────────────

def get_sunrise(target: date) -> datetime:
    """
    Return sunrise as an IST-aware datetime for *target* at the configured
    location, using Skyfield's rise/set calculations with standard refraction.
    """
    start_local = _TZ.localize(datetime(target.year, target.month, target.day, 0, 0, 0)) - timedelta(hours=6)
    end_local = start_local + timedelta(hours=48)
    t0 = _datetime_to_time(start_local)
    t1 = _datetime_to_time(end_local)

    t, y = almanac.find_discrete(t0, t1, almanac.sunrise_sunset(eph, _OBSERVER))

    # y[i] = 1 means sunrise, 0 means sunset on that date
    for ti, yi in zip(t, y):
        if yi == 1:  # sunrise
            ti_ist = ti.astimezone(_TZ)
            if ti_ist.date() == target:
                return ti_ist
    
    raise RuntimeError(f"No sunrise found for {target}")


def get_sunset(target: date) -> datetime:
    """
    Return sunset as an IST-aware datetime for *target* at the configured location.
    """
    start_local = _TZ.localize(datetime(target.year, target.month, target.day, 0, 0, 0)) - timedelta(hours=6)
    end_local = start_local + timedelta(hours=48)
    t0 = _datetime_to_time(start_local)
    t1 = _datetime_to_time(end_local)

    t, y = almanac.find_discrete(t0, t1, almanac.sunrise_sunset(eph, _OBSERVER))

    # y[i] = 0 means sunset
    for ti, yi in zip(t, y):
        if yi == 0:  # sunset
            ti_ist = ti.astimezone(_TZ)
            if ti_ist.date() == target:
                return ti_ist
    
    raise RuntimeError(f"No sunset found for {target}")


def get_lunar_rise(target: date) -> datetime:
    """
    Return lunar rise as an IST-aware datetime for *target* at the configured location.
    Uses Skyfield's almanac.risings_and_settings() which matches standard ephemeris sources.
    """
    start_local = _TZ.localize(datetime(target.year, target.month, target.day, 0, 0, 0)) - timedelta(hours=6)
    end_local = start_local + timedelta(hours=48)
    t0 = _datetime_to_time(start_local)
    t1 = _datetime_to_time(end_local)

    f = almanac.risings_and_settings(eph, moon, _OBSERVER)
    t, events = almanac.find_discrete(t0, t1, f)

    # events: 1 = rise, 0 = set
    for ti, event in zip(t, events):
        if event == 1:  # rise event
            ti_ist = ti.astimezone(_TZ)
            if ti_ist.date() == target:
                return ti_ist
    
    raise RuntimeError(f"No lunar rise found for {target}")


def get_lunar_set(target: date) -> datetime:
    """
    Return lunar set as an IST-aware datetime for *target* at the configured location.
    Uses Skyfield's almanac.risings_and_settings() which matches standard ephemeris sources.
    
    Returns the set that follows the rise on *target* (may be on the next day if early morning).
    """
    start_local = _TZ.localize(datetime(target.year, target.month, target.day, 0, 0, 0)) - timedelta(hours=6)
    end_local = start_local + timedelta(hours=72)  # Extend to 72 hours to capture next-day set
    t0 = _datetime_to_time(start_local)
    t1 = _datetime_to_time(end_local)

    f = almanac.risings_and_settings(eph, moon, _OBSERVER)
    t, events = almanac.find_discrete(t0, t1, f)

    # Find the rise on target date, then return the next set
    target_rise_found = False
    for ti, event in zip(t, events):
        ti_ist = ti.astimezone(_TZ)
        
        if event == 1 and ti_ist.date() == target:  # rise on target date
            target_rise_found = True
            continue
        
        if target_rise_found and event == 0:  # set after the rise
            return ti_ist
    
    raise RuntimeError(f"No lunar set found following rise on {target}")



# ─────────────────────────────────────────────────────────────────────
# Boundary finder  (bisection)
# ─────────────────────────────────────────────────────────────────────

def find_boundary_jd(
    value_fn,
    boundary: float,
    jd_lo: float,
    jd_hi: float,
    tolerance: float = 1e-7,
) -> float:
    """
    Binary-search for the Julian Day when *value_fn(jd)* first crosses
    *boundary* within [jd_lo, jd_hi].

    Used by calculations.py to find end-times for Tithi, Nakshatra, Yoga, Karana.

    Parameters
    ----------
    value_fn  : callable(jd) → float, monotonically increasing in [jd_lo, jd_hi]
    boundary  : the threshold the function should reach
    jd_lo/hi  : search interval in Julian Days
    tolerance : Julian Day precision (1e-7 ≈ 0.01 seconds)
    """
    lo, hi = jd_lo, jd_hi
    v_lo = value_fn(lo)
    v_hi = value_fn(hi)

    # Handle the 360°→0° wrap: if the function wraps, shift hi value up.
    if v_hi < v_lo:
        v_hi += 360.0

    if boundary < v_lo:
        boundary += 360.0

    for _ in range(60):   # 60 iterations → sub-millisecond accuracy
        mid = (lo + hi) / 2.0
        v_mid = value_fn(mid)
        if v_mid < v_lo:         # wrap occurred mid-interval
            v_mid += 360.0
        if v_mid < boundary:
            lo = mid
            v_lo = v_mid
        else:
            hi = mid
        if (hi - lo) < tolerance:
            break

    return (lo + hi) / 2.0


# ─────────────────────────────────────────────────────────────────────
# New Moon finder
# ─────────────────────────────────────────────────────────────────────

def find_last_new_moon_jd(jd: float) -> float:
    """
    Find the Julian Day of the last new moon on or before the given JD.
    
    Uses Skyfield's moon_phases almanac to find all phase events, then
    returns the JD of the most recent new moon. The search extends slightly
    into the future to capture new moons that occur later the same day.
    """
    # Search back 40 days and forward 1 day to capture boundary cases
    jd_search_start = jd - 40
    jd_search_end = jd + 1.5  # ~36 hours forward to capture same-day new moons
    
    t_start = ts.tt_jd(jd_search_start)
    t_end = ts.tt_jd(jd_search_end)
    
    f = almanac.moon_phases(eph)
    times, phases = almanac.find_discrete(t_start, t_end, f)
    
    # phases: 0=New, 1=First Quarter, 2=Full, 3=Last Quarter
    # Find the LAST New Moon (phase==0) that is at or close to jd
    last_new_moon_jd = None
    for ti, phase in zip(times, phases):
        ti_jd = float(ti.tt)
        if phase == 0:
            # Accept new moons that occur within 1.5 days (allows same-day captures)
            if ti_jd <= jd + 1.5:
                last_new_moon_jd = ti_jd
    
    if last_new_moon_jd is None:
        raise RuntimeError(f"Could not find new moon around JD {jd}")
    
    return last_new_moon_jd


def find_next_new_moon_jd(jd: float) -> float:
    """
    Find the Julian Day of the next new moon after the given JD.
    
    Searches forward from the given JD to find the next new moon event.
    """
    # Search forward 40 days from jd
    jd_search_start = jd
    jd_search_end = jd + 40
    
    t_start = ts.tt_jd(jd_search_start)
    t_end = ts.tt_jd(jd_search_end)
    
    f = almanac.moon_phases(eph)
    times, phases = almanac.find_discrete(t_start, t_end, f)
    
    # Find the first New Moon (phase==0) after jd
    for ti, phase in zip(times, phases):
        ti_jd = float(ti.tt)
        if phase == 0 and ti_jd > jd + 0.1:  # Ensure it's actually in the future
            return ti_jd
    
    raise RuntimeError(f"Could not find next new moon after JD {jd}")


def _rashi_index(sidereal_longitude: float) -> int:
    return int(sidereal_longitude / 30.0) % 12


def list_sankranti_jds(jd_start: float, jd_end: float) -> list[float]:
    """
    Return precise Sankranti instants (Sun entering a new sidereal sign)
    between jd_start and jd_end.
    """
    if jd_end <= jd_start:
        return []

    sankrantis: list[float] = []
    step_days = 0.25

    left = jd_start
    left_rashi = _rashi_index(sun_longitude(left))
    cursor = left + step_days

    while cursor <= jd_end + step_days:
        right = min(cursor, jd_end)
        right_rashi = _rashi_index(sun_longitude(right))

        if right_rashi != left_rashi:
            boundary = ((left_rashi + 1) % 12) * 30.0
            jd_cross = find_boundary_jd(sun_longitude, boundary, left, right + 0.5)
            if jd_start <= jd_cross <= jd_end:
                sankrantis.append(jd_cross)

        left = right
        left_rashi = right_rashi
        cursor += step_days

    return sankrantis


def count_sankrantis_between(jd_start: float, jd_end: float) -> int:
    """Count sidereal sign transits of the Sun between two Julian Days."""
    return len(list_sankranti_jds(jd_start, jd_end))
