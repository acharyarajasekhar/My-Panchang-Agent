"""
Karana lookup tables.

A lunar month has 60 half-Tithis (Karanas).
  • Position 0     : Kimstughna (fixed)
  • Positions 1–56 : 8 × 7 repeating Karanas (Bava … Vishti)
  • Position 57    : Shakuni (fixed)
  • Position 58    : Chatushpada (fixed)
  • Position 59    : Naga (fixed)

Karana number within month = 2*(tithi_index) + half
  where half = 0 (first half of Tithi) or 1 (second half).

For display we only need the name at the current moment; the calculation
module resolves the exact half via the elongation fraction.
"""

# ── Repeating Karanas (cycle index 0-6) ──────────────────────────────
REPEATING_KARANA: list[tuple[str, str]] = [
    ("Bava",        "బవ"),        # 0
    ("Balava",      "బాలవ"),      # 1
    ("Kaulava",     "కౌలవ"),      # 2
    ("Taitila",     "తైతిల"),     # 3
    ("Garaja",      "గరజ"),       # 4
    ("Vanija",      "వణిజ"),      # 5
    ("Vishti",      "విష్టి"),    # 6  (also called Bhadra — inauspicious)
]

# ── Fixed Karanas ─────────────────────────────────────────────────────
FIXED_KARANA: dict[str, tuple[str, str]] = {
    "Kimstughna":  ("Kimstughna",  "కింస్తుఘ్న"),
    "Shakuni":     ("Shakuni",     "శకుని"),
    "Chatushpada": ("Chatushpada", "చతుష్పద"),
    "Naga":        ("Naga",        "నాగ"),
}


def get_karana(tithi_index: int, elongation_deg: float) -> tuple[str, str]:
    """
    Return (english, telugu) Karana name.

    Parameters
    ----------
    tithi_index    : 0-based Tithi index (0 = Shukla Pratipada … 29 = Amavasya)
    elongation_deg : Moon-Sun elongation in degrees (0-360)
    """
    # Which half of the Tithi are we in? (0 = first 6°, 1 = second 6°)
    half = 0 if (elongation_deg % 12.0) < 6.0 else 1

    karana_pos = tithi_index * 2 + half  # 0-59
    return get_karana_by_position(karana_pos)


def get_karana_by_position(karana_pos: int) -> tuple[str, str]:
    """Return (english, telugu) Karana name by position (0-59)."""
    karana_pos = karana_pos % 60
    if karana_pos == 0:
        return FIXED_KARANA["Kimstughna"]
    if karana_pos == 57:
        return FIXED_KARANA["Shakuni"]
    if karana_pos == 58:
        return FIXED_KARANA["Chatushpada"]
    if karana_pos == 59:
        return FIXED_KARANA["Naga"]
    cycle_idx = (karana_pos - 1) % 7
    return REPEATING_KARANA[cycle_idx]
