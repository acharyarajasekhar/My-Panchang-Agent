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
    """తిథి, నక్షత్రం, యోగం, కరణం — సంపూర్ణ సమయ విచారణతో."""
    
    def _format_element_timeline(elem) -> str:
        """Format an element with full transition timeline in Telugu."""
        lines = []
        
        # Show previous element if it exists
        if elem.prev_name_te:
            indicator = " ⚠️" if elem.prev_is_inauspicious else ""
            lines.append(f"  • {elem.prev_name_te}{indicator} (← {elem.prev_ends_at})")
        
        # If element started on previous day, show it with end time
        if elem.started_on_previous_day:
            lines.append(f"  • {elem.name_te} ({elem.started_at} → {elem.ends_at})")
        else:
            started_str = elem.started_at if elem.started_at else "రోజు ప్రారంభం"
            lines.append(f"  • {elem.name_te} ({started_str} → {elem.ends_at})")
        
        # Show next element if it starts on the same day
        if elem.next_name_te:
            indicator = " ⚠️" if elem.next_is_inauspicious else ""
            lines.append(f"  → {elem.next_name_te}{indicator} ({elem.next_starts_at} → {elem.next_ends_at})")
        
        # Show third element if it also fits on the same day
        if elem.next_next_name_te:
            indicator = " ⚠️" if elem.next_next_is_inauspicious else ""
            lines.append(f"  → {elem.next_next_name_te}{indicator} ({elem.next_next_starts_at} → {elem.next_next_ends_at})")
        
        return "\n".join(lines)
    
    # Format Tithi with transitions
    tithi_str = _format_element_timeline(r.tithi)
    
    # Format Nakshatra with transitions
    nak_str = _format_element_timeline(r.nakshatra)
    
    # Format Yoga with transitions
    yoga_str = _format_element_timeline(r.yoga)
    
    # Format Karana with transitions
    kar_str = _format_element_timeline(r.karana)
    
    lines = [
        "*⭐ పంచాంగ అంగాలు*",
        "```",
        f"🌙 తిథి:\n{tithi_str}",
        f"\n⭐ నక్షత్రం:\n{nak_str}",
        f"\n🔮 యోగం:\n{yoga_str}",
        f"\n🎯 కరణం:\n{kar_str}",
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


def festival_section(r: PanchangamResult) -> str:
    """పండుగ సమాచారం ఈ రోజుకు."""
    if not r.festival_today_te:
        return ""
    
    lines = [
        "*🎉 ఈ రోజు పండుగ*",
        "```",
        f"{r.festival_today_te}",
        "```",
    ]
    return "\n".join(lines)
