"""
30 Tithis (lunar days).

Index 0–14  = Shukla Pratipada … Purnima
Index 15–29 = Krishna Pratipada … Amavasya

Tithi index = floor((moon_lon - sun_lon) % 360 / 12)
Each Tithi spans exactly 12° of elongation.
"""

from typing import NamedTuple


class TithiInfo(NamedTuple):
    index: int          # 0-based (0 = Shukla Pratipada)
    english: str
    telugu: str
    paksha_en: str      # "Shukla" or "Krishna"
    paksha_te: str      # "శుక్ల" or "కృష్ణ"
    number: int         # 1-15 within paksha


# (english_name, telugu_name)  — ordered Shukla 1…15 then Krishna 1…15
_NAMES: list[tuple[str, str]] = [
    # ── Shukla Paksha ──────────────────────────────────────────────────
    ("Pratipada",   "పాడ్యమి"),        # 0  Shukla 1
    ("Dvitiya",     "విదియ"),           # 1  Shukla 2
    ("Tritiya",     "తదియ"),            # 2  Shukla 3
    ("Chaturthi",   "చవితి"),           # 3  Shukla 4
    ("Panchami",    "పంచమి"),           # 4  Shukla 5
    ("Shashthi",    "షష్ఠి"),           # 5  Shukla 6
    ("Saptami",     "సప్తమి"),          # 6  Shukla 7
    ("Ashtami",     "అష్టమి"),          # 7  Shukla 8
    ("Navami",      "నవమి"),            # 8  Shukla 9
    ("Dashami",     "దశమి"),            # 9  Shukla 10
    ("Ekadashi",    "ఏకాదశి"),          # 10 Shukla 11
    ("Dvadashi",    "ద్వాదశి"),         # 11 Shukla 12
    ("Trayodashi",  "త్రయోదశి"),        # 12 Shukla 13
    ("Chaturdashi", "చతుర్దశి"),        # 13 Shukla 14
    ("Purnima",     "పౌర్ణమి"),         # 14 Shukla 15
    # ── Krishna Paksha ─────────────────────────────────────────────────
    ("Pratipada",   "పాడ్యమి"),         # 15 Krishna 1
    ("Dvitiya",     "విదియ"),           # 16 Krishna 2
    ("Tritiya",     "తదియ"),            # 17 Krishna 3
    ("Chaturthi",   "చవితి"),           # 18 Krishna 4
    ("Panchami",    "పంచమి"),           # 19 Krishna 5
    ("Shashthi",    "షష్ఠి"),           # 20 Krishna 6
    ("Saptami",     "సప్తమి"),          # 21 Krishna 7
    ("Ashtami",     "అష్టమి"),          # 22 Krishna 8
    ("Navami",      "నవమి"),            # 23 Krishna 9
    ("Dashami",     "దశమి"),            # 24 Krishna 10
    ("Ekadashi",    "ఏకాదశి"),          # 25 Krishna 11
    ("Dvadashi",    "ద్వాదశి"),         # 26 Krishna 12
    ("Trayodashi",  "త్రయోదశి"),        # 27 Krishna 13
    ("Chaturdashi", "చతుర్దశి"),        # 28 Krishna 14
    ("Amavasya",    "అమావాస్య"),        # 29 Krishna 15 / Amavasya
]

TITHI_SPAN_DEG: float = 12.0  # degrees of Moon-Sun elongation


def get_tithi(moon_lon: float, sun_lon: float) -> TithiInfo:
    """Return TithiInfo for the given Moon and Sun ecliptic longitudes (degrees)."""
    elongation = (moon_lon - sun_lon) % 360.0
    idx = int(elongation / TITHI_SPAN_DEG) % 30
    en, te = _NAMES[idx]
    if idx < 15:
        paksha_en, paksha_te, number = "Shukla", "శుక్ల", idx + 1
    else:
        paksha_en, paksha_te, number = "Krishna", "కృష్ణ", idx - 14
    return TithiInfo(
        index=idx,
        english=en,
        telugu=te,
        paksha_en=paksha_en,
        paksha_te=paksha_te,
        number=number,
    )


def get_tithi_by_index(idx: int) -> TithiInfo:
    """Return TithiInfo for a given Tithi index (0-29)."""
    idx = idx % 30
    en, te = _NAMES[idx]
    if idx < 15:
        paksha_en, paksha_te, number = "Shukla", "శుక్ల", idx + 1
    else:
        paksha_en, paksha_te, number = "Krishna", "కృష్ణ", idx - 14
    return TithiInfo(
        index=idx,
        english=en,
        telugu=te,
        paksha_en=paksha_en,
        paksha_te=paksha_te,
        number=number,
    )
