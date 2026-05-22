"""
formatter/telugu.py
────────────────────
Renders each section of the Panchangam in Telugu script as mrkdwn strings
suitable for Slack Block Kit `fields`.
"""

from __future__ import annotations

from panchang.calculations import PanchangamResult
from panchang.timings import DailyTimings


def _warn(flag: bool) -> str:
    return "⚠️" if flag else ""


def _masa_label(r: PanchangamResult) -> str:
    if r.masa_status_te:
        return f"{r.masa_status_te} {r.masa_te} మాసం"
    return f"{r.masa_te} మాసం"


def _table_row(emoji: str, label: str, value: str) -> str:
    """Format a 2-column table row: emoji + label: (2 spaces) value"""
    return f"{emoji}  {label}:  {value}"


# ─────────────────────────────────────────────────────────────────────
# Section renderers
# ─────────────────────────────────────────────────────────────────────

def calendar_section(r: PanchangamResult) -> str:
    """సంవత్సరం, అయనం, ఋతువు, మాసం, పక్షం as 3-column table."""
    lines = [
        "*📆 పంచాంగ వివరాలు*",
        "```",
        _table_row("🌞", "సంవత్సరం", r.samvatsara_te),
        _table_row("☀️", "అయనం", r.ayana_te),
        _table_row("🌿", "ఋతువు", r.ritu_te),
        _table_row("🌙", "మాసం", _masa_label(r)),
        _table_row("✨", "పక్షం", r.paksha_te),
        "```",
    ]
    return "\n".join(lines)


def pancha_anga_section(r: PanchangamResult) -> str:
    """తిథి, నక్షత్రం, యోగం, కరణం — ముగింపు సమయాలతో as 3-column table."""
    # Format Tithi with chain of next elements
    tithi_str = f"{r.tithi.name_te} ({r.tithi.ends_at})"
    if r.tithi.next_name_te:
        tithi_str += f" → {r.tithi.next_name_te}"
        if r.tithi.next_ends_at and r.tithi.next_next_name_te:
            tithi_str += f" ({r.tithi.next_ends_at}) → {r.tithi.next_next_name_te}"
    
    # Format Nakshatra with chain of next elements
    nak_str = f"{r.nakshatra.name_te} ({r.nakshatra.ends_at})"
    if r.nakshatra.next_name_te:
        nak_str += f" → {r.nakshatra.next_name_te}"
        if r.nakshatra.next_ends_at and r.nakshatra.next_next_name_te:
            nak_str += f" ({r.nakshatra.next_ends_at}) → {r.nakshatra.next_next_name_te}"
    
    # Format Yoga with chain of next elements
    yoga_str = f"{r.yoga.name_te} {_warn(r.yoga.is_inauspicious)} ({r.yoga.ends_at})"
    if r.yoga.next_name_te:
        yoga_str += f" → {r.yoga.next_name_te}"
        if r.yoga.next_ends_at and r.yoga.next_next_name_te:
            yoga_str += f" ({r.yoga.next_ends_at}) → {r.yoga.next_next_name_te}"
    
    # Format Karana with chain of next elements
    kar_str = f"{r.karana.name_te} {_warn(r.karana.is_inauspicious)} ({r.karana.ends_at})"
    if r.karana.next_name_te:
        kar_str += f" → {r.karana.next_name_te}"
        if r.karana.next_ends_at and r.karana.next_next_name_te:
            kar_str += f" ({r.karana.next_ends_at}) → {r.karana.next_next_name_te}"
    
    lines = [
        "*⭐ పంచాంగ అంగాలు*",
        "```",
        _table_row("🌙", "తిథి", tithi_str),
        _table_row("⭐", "నక్షత్రం", nak_str),
        _table_row("🔮", "యోగం", yoga_str),
        _table_row("🎯", "కరణం", kar_str),
        "```",
    ]
    return "\n".join(lines)


def timings_section(t: DailyTimings) -> str:
    """సూర్యోదయం, సూర్యాస్తమయం మరియు అశుభ సమయాలు as 3-column table."""
    varjyam_text = " | ".join(t.varjyam) if t.varjyam else "లేదు"
    lines = [
        "*⏰ ముఖ్యమైన సమయాలు*",
        "```",
        _table_row("🌅", "సూర్యోదయం", t.sunrise),
        _table_row("🌇", "సూర్యాస్తమయం", t.sunset),
        _table_row("🌙", "చంద్రోదయం", t.lunar_rise),
        _table_row("🌙", "చంద్రాస్తమయం", t.lunar_set),
        _table_row("🚫", "రాహుకాలం", str(t.rahu_kalam)),
        _table_row("⚠️", "యమగండం", str(t.yamagandam)),
        _table_row("🛑", "వర్జ్యం", varjyam_text),
        _table_row("🌑", "గుళికకాలం", str(t.gulika_kalam)),
        _table_row("⛔", "దుర్ముహూర్తం", f"{t.durmuhurtam_1} | {t.durmuhurtam_2}"),
        "```",
    ]
    return "\n".join(lines)
