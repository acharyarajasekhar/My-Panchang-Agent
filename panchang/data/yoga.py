"""
27 Yogas.

Yoga index = floor((sun_lon + moon_lon) % 360 / (360/27))
Each Yoga spans 360/27 ≈ 13.333° of the combined Sun+Moon longitude.

Inauspicious Yogas: Vishkamba(0), Atiganda(5), Shula(8), Ganda(9),
                    Vyaghata(12), Vajra(14), Vyatipata(16), Parigha(18),
                    Vaidhriti(26)
"""

# Each entry: (english_name, telugu_name, is_inauspicious)
YOGA: list[tuple[str, str, bool]] = [
    ("Vishkamba",   "విష్కంభ",  True),   # 0
    ("Priti",       "ప్రీతి",    False),  # 1
    ("Ayushman",    "ఆయుష్మాన్", False),  # 2
    ("Saubhagya",   "సౌభాగ్య",  False),  # 3
    ("Shobhana",    "శోభన",     False),  # 4
    ("Atiganda",    "అతిగండ",   True),   # 5
    ("Sukarman",    "సుకర్మ",   False),  # 6
    ("Dhriti",      "ధృతి",     False),  # 7
    ("Shula",       "శూల",      True),   # 8
    ("Ganda",       "గండ",      True),   # 9
    ("Vriddhi",     "వృద్ధి",   False),  # 10
    ("Dhruva",      "ధ్రువ",    False),  # 11
    ("Vyaghata",    "వ్యాఘాత",  True),   # 12
    ("Harshana",    "హర్షణ",    False),  # 13
    ("Vajra",       "వజ్ర",     True),   # 14
    ("Siddhi",      "సిద్ధి",   False),  # 15
    ("Vyatipata",   "వ్యతీపాత", True),   # 16
    ("Variyan",     "వరీయాన్",  False),  # 17
    ("Parigha",     "పరిఘ",     True),   # 18
    ("Shiva",       "శివ",      False),  # 19
    ("Siddha",      "సిద్ధ",    False),  # 20
    ("Sadhya",      "సాధ్య",    False),  # 21
    ("Shubha",      "శుభ",      False),  # 22
    ("Shukla",      "శుక్ల",    False),  # 23
    ("Brahma",      "బ్రహ్మ",   False),  # 24
    ("Aindra",      "ఐంద్ర",    False),  # 25
    ("Vaidhriti",   "వైధృతి",   True),   # 26
]

YOGA_SPAN_DEG: float = 360.0 / 27  # ≈ 13.3333°


def get_yoga(sun_lon: float, moon_lon: float) -> tuple[int, tuple[str, str, bool]]:
    """Return (index, yoga_tuple) for given Sun and Moon longitudes (degrees)."""
    combined = (sun_lon + moon_lon) % 360.0
    idx = int(combined / YOGA_SPAN_DEG) % 27
    return idx, YOGA[idx]


def get_yoga_by_index(idx: int) -> tuple[str, str, bool]:
    """Return yoga tuple (english, telugu, is_inauspicious) for a given index (0-26)."""
    return YOGA[idx % 27]
