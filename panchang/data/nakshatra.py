"""
27 Nakshatras (lunar mansions).

Index 0 = Ashwini.  Each spans 360/27 ≈ 13.333° of ecliptic longitude.
Nakshatra index = floor(moon_longitude / (360/27))
"""

# Each entry: (english_name, telugu_name, ruling_planet)
NAKSHATRA: list[tuple[str, str, str]] = [
    ("Ashwini",             "అశ్విని",          "Ketu"),      # 0
    ("Bharani",             "భరణి",              "Venus"),     # 1
    ("Krittika",            "కృత్తిక",           "Sun"),       # 2
    ("Rohini",              "రోహిణి",            "Moon"),      # 3
    ("Mrigashirsha",        "మృగశిర",            "Mars"),      # 4
    ("Ardra",               "ఆర్ద్ర",            "Rahu"),      # 5
    ("Punarvasu",           "పునర్వసు",          "Jupiter"),   # 6
    ("Pushya",              "పుష్య",             "Saturn"),    # 7
    ("Ashlesha",            "ఆశ్లేష",            "Mercury"),   # 8
    ("Magha",               "మఘ",                "Ketu"),      # 9
    ("Purva Phalguni",      "పూర్వ ఫల్గుణి",    "Venus"),     # 10
    ("Uttara Phalguni",     "ఉత్తర ఫల్గుణి",    "Sun"),       # 11
    ("Hasta",               "హస్త",              "Moon"),      # 12
    ("Chitra",              "చిత్ర",             "Mars"),      # 13
    ("Swati",               "స్వాతి",            "Rahu"),      # 14
    ("Vishakha",            "విశాఖ",             "Jupiter"),   # 15
    ("Anuradha",            "అనూరాధ",            "Saturn"),    # 16
    ("Jyeshtha",            "జ్యేష్ఠ",           "Mercury"),   # 17
    ("Mula",                "మూల",               "Ketu"),      # 18
    ("Purva Ashadha",       "పూర్వాషాఢ",         "Venus"),     # 19
    ("Uttara Ashadha",      "ఉత్తరాషాఢ",         "Sun"),       # 20
    ("Shravana",            "శ్రవణ",             "Moon"),      # 21
    ("Dhanishtha",          "ధనిష్ఠ",            "Mars"),      # 22
    ("Shatabhisha",         "శతభిష",             "Rahu"),      # 23
    ("Purva Bhadrapada",    "పూర్వభాద్ర",        "Jupiter"),   # 24
    ("Uttara Bhadrapada",   "ఉత్తరభాద్ర",        "Saturn"),    # 25
    ("Revati",              "రేవతి",             "Mercury"),   # 26
]

NAKSHATRA_SPAN_DEG: float = 360.0 / 27  # ≈ 13.3333°


def get_nakshatra(moon_longitude: float) -> tuple[int, tuple[str, str, str]]:
    """
    Return (index, nakshatra_tuple) for a given Moon ecliptic longitude (0–360°).
    """
    idx = int(moon_longitude / NAKSHATRA_SPAN_DEG) % 27
    return idx, NAKSHATRA[idx]


def get_nakshatra_by_index(idx: int) -> tuple[str, str, str]:
    """Return nakshatra tuple (english, telugu, ruling_planet) for a given index (0-26)."""
    return NAKSHATRA[idx % 27]
