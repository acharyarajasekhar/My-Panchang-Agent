"""
12 Lunar months (Masa), Ritu (season) mapping, and Ayana.

Masa is determined by the Sun's sign at the new moon that begins the month.
  Sun in Aries (0°)   → Chaitra (month 1)
  Sun in Taurus (30°) → Vaisakha (month 2)
  … and so on.

Masa index = floor(sun_longitude_at_new_moon / 30) % 12
"""

from typing import NamedTuple


class MasaInfo(NamedTuple):
    index: int          # 0 = Chaitra
    english: str
    telugu: str
    ritu_en: str
    ritu_te: str
    ayana_en: str       # "Uttarayana" or "Dakshinayana"
    ayana_te: str       # "ఉత్తరాయణం" or "దక్షిణాయనం"


# ── Raw table ─────────────────────────────────────────────────────────
# (english, telugu, ritu_en, ritu_te)
_MASA_RAW: list[tuple[str, str, str, str]] = [
    ("Chaitra",      "చైత్రం",       "Vasanta",    "వసంత"),     # 0  (Mar-Apr)
    ("Vaisakha",     "వైశాఖం",        "Vasanta",    "వసంత"),     # 1  (Apr-May)
    ("Jyeshtha",     "జ్యేష్ఠం",      "Grishma",    "గ్రీష్మ"),   # 2  (May-Jun)
    ("Ashadha",      "ఆషాఢం",         "Grishma",    "గ్రీష్మ"),   # 3  (Jun-Jul)
    ("Shravana",     "శ్రావణం",        "Varsha",     "వర్ష"),      # 4  (Jul-Aug)
    ("Bhadrapada",   "భాద్రపదం",      "Varsha",     "వర్ష"),      # 5  (Aug-Sep)
    ("Ashwina",      "ఆశ్వయుజం",      "Sharad",     "శరద్"),      # 6  (Sep-Oct)
    ("Kartika",      "కార్తీకం",       "Sharad",     "శరద్"),      # 7  (Oct-Nov)
    ("Margashirsha", "మార్గశీర్షం",    "Hemanta",    "హేమంత"),    # 8  (Nov-Dec)
    ("Pausha",       "పుష్యం",         "Hemanta",    "హేమంత"),    # 9  (Dec-Jan)
    ("Magha",        "మాఘం",           "Shishira",   "శిశిర"),     # 10 (Jan-Feb)
    ("Phalguna",     "ఫాల్గుణం",       "Shishira",   "శిశిర"),     # 11 (Feb-Mar)
]

# Ayana: Uttarayana = Capricorn entry (≈ Pausha/Magha, months 9-10 onward)
#        Dakshinayana = Cancer entry  (≈ Ashadha/Shravana, months 3-4 onward)
# Simple approximation: months 9,10,11,0,1,2 → Uttarayana; rest → Dakshinayana
_UTTARAYANA_MONTHS = {9, 10, 11, 0, 1, 2}


def build_masa_info(index: int) -> MasaInfo:
    en, te, ritu_en, ritu_te = _MASA_RAW[index % 12]
    if index % 12 in _UTTARAYANA_MONTHS:
        ayana_en, ayana_te = "Uttarayana", "ఉత్తరాయణం"
    else:
        ayana_en, ayana_te = "Dakshinayana", "దక్షిణాయనం"
    return MasaInfo(
        index=index % 12,
        english=en,
        telugu=te,
        ritu_en=ritu_en,
        ritu_te=ritu_te,
        ayana_en=ayana_en,
        ayana_te=ayana_te,
    )


def get_masa(sun_longitude: float) -> MasaInfo:
    """
    Derive Masa from the Sun's current ecliptic longitude.

    Note: For a fully accurate Masa (e.g. Adhika/leap-month detection), the
    calculation layer cross-checks the Sun's sign at the preceding new moon.
    This function provides a fast approximation sufficient for most dates.
    """
    # Amanta naming: month is identified by the full moon nakshatra,
    # equivalent to shifting the new-moon Sun-sign mapping by +1.
    idx = (int(sun_longitude / 30.0) + 1) % 12
    return build_masa_info(idx)
