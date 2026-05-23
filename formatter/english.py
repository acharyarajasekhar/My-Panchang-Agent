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
    """Five limbs with complete transition timeline showing start and end times."""
    
    def _format_element_timeline(elem) -> str:
        """Format an element with full transition timeline."""
        lines = []
        
        # Current element with start→end times
        if elem.started_on_previous_day:
            lines.append(f"  • {elem.name_en} ({elem.started_at} → {elem.ends_at})")
        else:
            start_label = elem.started_at if elem.started_at else "day start"
            lines.append(f"  • {elem.name_en} ({start_label} → {elem.ends_at})")
        
        # Show next element if it starts on the same day
        if elem.next_name_en:
            indicator = " ⚠️" if elem.next_is_inauspicious else ""
            lines.append(f"  → {elem.next_name_en}{indicator} ({elem.next_starts_at} → {elem.next_ends_at})")
        
        # Show third element if it also fits on the same day
        if elem.next_next_name_en:
            indicator = " ⚠️" if elem.next_next_is_inauspicious else ""
            lines.append(f"  → {elem.next_next_name_en}{indicator} ({elem.next_next_starts_at} → {elem.next_next_ends_at})")
        
        return "\n".join(lines)
    
    # Format all four elements
    tithi_str = _format_element_timeline(r.tithi)
    nak_str = _format_element_timeline(r.nakshatra)
    yoga_str = _format_element_timeline(r.yoga)
    kar_str = _format_element_timeline(r.karana)
    
    lines = [
        "*⭐ Pancha Anga*",
        "```",
        f"🌙 Tithi:\n{tithi_str}",
        f"\n⭐ Nakshatra:\n{nak_str}",
        f"\n🔮 Yoga:\n{yoga_str}",
        f"\n🎯 Karana:\n{kar_str}",
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
