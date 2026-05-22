"""
formatter/english.py
─────────────────────
Renders each section of the Panchangam as English mrkdwn strings
suitable for Slack Block Kit `fields`.
"""

from __future__ import annotations

from panchang.calculations import PanchangamResult
from panchang.timings import DailyTimings


def _warn(flag: bool) -> str:
    return "⚠️" if flag else ""


def _masa_label(r: PanchangamResult) -> str:
    if r.masa_status_en:
        return f"{r.masa_status_en} {r.masa_en} Masam"
    return f"{r.masa_en} Masam"


def _table_row(emoji: str, label: str, value: str) -> str:
    """Format a 2-column table row: emoji + label: (2 spaces) value"""
    return f"{emoji}  {label}:  {value}"


# ─────────────────────────────────────────────────────────────────────
# Section renderers — each returns a formatted table string
# ─────────────────────────────────────────────────────────────────────

def calendar_section(r: PanchangamResult) -> str:
    """Samvatsara, Ayana, Ritu, Masa, Paksha in English as 3-column table."""
    lines = [
        "*📆 Calendar*",
        "```",
        _table_row("🌞", "Samvatsara", r.samvatsara_en),
        _table_row("☀️", "Ayana", r.ayana_en),
        _table_row("🌿", "Ritu (Season)", r.ritu_en),
        _table_row("🌙", "Masa", _masa_label(r)),
        _table_row("✨", "Paksha", r.paksha_en),
        "```",
    ]
    return "\n".join(lines)


def pancha_anga_section(r: PanchangamResult) -> str:
    """Five limbs with end times as 3-column table."""
    # Format Tithi with chain of next elements
    tithi_str = f"{r.tithi.name_en} (ends {r.tithi.ends_at})"
    if r.tithi.next_name_en:
        tithi_str += f" → {r.tithi.next_name_en}"
        if r.tithi.next_ends_at and r.tithi.next_next_name_en:
            tithi_str += f" (ends {r.tithi.next_ends_at}) → {r.tithi.next_next_name_en}"
    
    # Format Nakshatra with chain of next elements
    nak_str = f"{r.nakshatra.name_en} (ends {r.nakshatra.ends_at})"
    if r.nakshatra.next_name_en:
        nak_str += f" → {r.nakshatra.next_name_en}"
        if r.nakshatra.next_ends_at and r.nakshatra.next_next_name_en:
            nak_str += f" (ends {r.nakshatra.next_ends_at}) → {r.nakshatra.next_next_name_en}"
    
    # Format Yoga with chain of next elements
    yoga_str = f"{r.yoga.name_en} {_warn(r.yoga.is_inauspicious)} (ends {r.yoga.ends_at})"
    if r.yoga.next_name_en:
        yoga_str += f" → {r.yoga.next_name_en}"
        if r.yoga.next_ends_at and r.yoga.next_next_name_en:
            yoga_str += f" (ends {r.yoga.next_ends_at}) → {r.yoga.next_next_name_en}"
    
    # Format Karana with chain of next elements
    kar_str = f"{r.karana.name_en} {_warn(r.karana.is_inauspicious)} (ends {r.karana.ends_at})"
    if r.karana.next_name_en:
        kar_str += f" → {r.karana.next_name_en}"
        if r.karana.next_ends_at and r.karana.next_next_name_en:
            kar_str += f" (ends {r.karana.next_ends_at}) → {r.karana.next_next_name_en}"
    
    lines = [
        "*⭐ Pancha Anga*",
        "```",
        _table_row("🌙", "Tithi", tithi_str),
        _table_row("⭐", "Nakshatra", nak_str),
        _table_row("🔮", "Yoga", yoga_str),
        _table_row("🎯", "Karana", kar_str),
        "```",
    ]
    return "\n".join(lines)


def timings_section(t: DailyTimings) -> str:
    """Sunrise/Sunset + all inauspicious windows as 3-column table."""
    varjyam_text = " | ".join(t.varjyam) if t.varjyam else "None"
    lines = [
        "*⏰ Key Timings*",
        "```",
        _table_row("🌅", "Sunrise", t.sunrise),
        _table_row("🌇", "Sunset", t.sunset),
        _table_row("🌙", "Lunar Rise", t.lunar_rise),
        _table_row("🌙", "Lunar Set", t.lunar_set),
        _table_row("🚫", "Rahu Kalam", str(t.rahu_kalam)),
        _table_row("⚠️", "Yamagandam", str(t.yamagandam)),
        _table_row("🛑", "Varjyam", varjyam_text),
        _table_row("🌑", "Gulika Kalam", str(t.gulika_kalam)),
        _table_row("⛔", "Durmuhurtam", f"{t.durmuhurtam_1} | {t.durmuhurtam_2}"),
        "```",
    ]
    return "\n".join(lines)
