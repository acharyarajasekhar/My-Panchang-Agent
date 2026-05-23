"""
formatter/blocks.py
────────────────────
Assembles the complete Slack Block Kit JSON payload from a PanchangamResult
and DailyTimings, mimicking a traditional Hindu calendar leaf.

Layout (sequential bilingual leaf style):
  ┌────────────────────────────────────────────────────────────────┐
  │  🕉  Daily Panchangam  |  గుంటూరు పంచాంగం          [header]  │
  ├────────────────────────────────────────────────────────────────┤
  │  📅 Thursday, 21 May 2026  |  గురువారం, 21 మే 2026           │
    │  📆 Calendar (EN)                                         │
    │  ⭐ Pancha Anga (EN)                                      │
    │  ⏰ Key Timings (EN)                                      │
    ├────────────────────────────────────────────────────────────────┤
    │  📆 పంచాంగ వివరాలు (TE)                                     │
    │  ⭐ పంచాంగ అంగాలు (TE)                                     │
    │  ⏰ ముఖ్యమైన సమయాలు (TE)                                   │
  ├────────────────────────────────────────────────────────────────┤
  │  📍 Guntur • IST • Swiss Ephemeris  [context footer]           │
  └────────────────────────────────────────────────────────────────┘
"""

from __future__ import annotations

from panchang.calculations import PanchangamResult
from panchang.timings import DailyTimings
import formatter.english as en
import formatter.telugu as te

# ── Telugu month name map for the date header ─────────────────────────
_TE_MONTHS = [
    "జనవరి", "ఫిబ్రవరి", "మార్చి", "ఏప్రిల్",
    "మే",     "జూన్",     "జులై",   "ఆగస్టు",
    "సెప్టెంబర్", "అక్టోబర్", "నవంబర్", "డిసెంబర్",
]


def _mrkdwn(text: str) -> dict:
    return {"type": "mrkdwn", "text": text}


def _plain(text: str) -> dict:
    return {"type": "plain_text", "text": text, "emoji": True}


def _divider() -> dict:
    return {"type": "divider"}


def _header(text: str) -> dict:
    return {"type": "header", "text": _plain(text)}


def _section_text(text: str) -> dict:
    return {"type": "section", "text": _mrkdwn(text)}


def _leaf_break(label: str) -> dict:
    return _section_text(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n*{label}*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


def _context(text: str) -> dict:
    return {
        "type": "context",
        "elements": [_mrkdwn(text)],
    }


# ─────────────────────────────────────────────────────────────────────
# Date header line
# ─────────────────────────────────────────────────────────────────────

def _date_header_bilingual(r: PanchangamResult) -> str:
    d = r.gregorian_date
    te_month = _TE_MONTHS[d.month - 1]
    en_weekday = r.weekday_en
    sa_weekday = r.weekday_sa
    te_weekday = r.weekday_te
    en_date = d.strftime("%d %B %Y")
    te_date = f"{d.day} {te_month} {d.year}"
    return f"📅  *{en_weekday} / {sa_weekday} / {te_weekday}*\n     {en_date} / {te_date}\n📍  Guntur, Andhra Pradesh, India"


def _date_header_english(r: PanchangamResult) -> str:
    d = r.gregorian_date
    te_month = _TE_MONTHS[d.month - 1]
    en_weekday = r.weekday_en
    sa_weekday = r.weekday_sa
    te_weekday = r.weekday_te
    en_date = d.strftime("%d %B %Y")
    te_date = f"{d.day} {te_month} {d.year}"
    return f"📅  *{en_weekday} / {sa_weekday} / {te_weekday}*\n     {en_date} / {te_date}\n📍  Guntur, Andhra Pradesh, India"


def _date_header_telugu(r: PanchangamResult) -> str:
    d = r.gregorian_date
    te_month = _TE_MONTHS[d.month - 1]
    sa_weekday_te = r.weekday_sa_te
    te_weekday = r.weekday_te
    te_date = f"{d.day} {te_month} {d.year}"
    return f"📅  *{sa_weekday_te} / {te_weekday}*\n     {te_date}\n📍  గుంటూరు, ఆంధ్రప్రదేశ్, భారతదేశం"


def _normalize_languages(languages: list[str] | tuple[str, ...] | str | None) -> tuple[str, ...]:
    if languages is None:
        return ("telugu",)
    if isinstance(languages, str):
        requested = [languages]
    else:
        requested = list(languages)

    normalized: list[str] = []
    for language in requested:
        if language not in {"english", "telugu"}:
            raise ValueError(
                f"Invalid language: {language!r}. Must be 'english' or 'telugu'."
            )
        if language not in normalized:
            normalized.append(language)

    if not normalized:
        return ("telugu",)
    if len(normalized) == 2:
        return ("english", "telugu")
    return tuple(normalized)


def _title_for_languages(languages: tuple[str, ...]) -> str:
    if languages == ("english",):
        return "🕉  Daily Panchangam"
    if languages == ("telugu",):
        return "🕉  నిత్య పంచాంగం"
    return "🕉  Daily Panchangam  •  నిత్య పంచాంగం"


def _date_header_for_languages(result: PanchangamResult, languages: tuple[str, ...]) -> str:
    if languages == ("english",):
        return _date_header_english(result)
    if languages == ("telugu",):
        return _date_header_telugu(result)
    return _date_header_bilingual(result)


# ─────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────

def build_payload(
    result: PanchangamResult,
    timings: DailyTimings,
    languages: list[str] | tuple[str, ...] | str | None = None,
) -> dict:
    """
    Return a complete Slack Incoming Webhook payload dict (JSON-serialisable).

    Parameters
    ----------
    result : PanchangamResult
        The calculated Panchangam data for the day.
    timings : DailyTimings
        Daily timing information (sunrise, sunset, inauspicious windows).
    languages : list[str] or str
        Message language(s): list like ["telugu"], ["english"], or ["english", "telugu"].
        For backward compatibility, can also be a string ("english" or "telugu").
        Defaults to ["telugu"].

    Pass directly to ``json.dumps()`` and POST to the webhook URL.
    """
    languages = _normalize_languages(languages)

    blocks = [
        # ── Title ─────────────────────────────────────────────────────
        _header(_title_for_languages(languages)),

        # ── Date & Location ───────────────────────────────────────────
        _section_text(_date_header_for_languages(result, languages)),
        _divider(),
    ]

    if languages == ("english", "telugu"):
        blocks.extend([
            _leaf_break("English"),
            _section_text(en.calendar_section(result)),
            _divider(),
            _section_text(en.pancha_anga_section(result)),
            _divider(),
            _section_text(en.timings_section(timings)),
            _divider(),
        ])
        if result.festival_today_en:
            blocks.extend([
                _section_text(en.festival_section(result)),
                _divider(),
            ])
        blocks.extend([
            _leaf_break("తెలుగు"),
            _section_text(te.calendar_section(result)),
            _divider(),
            _section_text(te.pancha_anga_section(result)),
            _divider(),
            _section_text(te.timings_section(timings)),
            _divider(),
        ])
        if result.festival_today_te:
            blocks.extend([
                _section_text(te.festival_section(result)),
            ])
    elif languages == ("english",):
        blocks.extend([
            _section_text(en.calendar_section(result)),
            _divider(),
            _section_text(en.pancha_anga_section(result)),
            _divider(),
            _section_text(en.timings_section(timings)),
            _divider(),
        ])
        if result.festival_today_en:
            blocks.extend([
                _section_text(en.festival_section(result)),
            ])
    else:
        blocks.extend([
            _section_text(te.calendar_section(result)),
            _divider(),
            _section_text(te.pancha_anga_section(result)),
            _divider(),
            _section_text(te.timings_section(timings)),
            _divider(),
        ])
        if result.festival_today_te:
            blocks.extend([
                _section_text(te.festival_section(result)),
            ])

    blocks.extend([
        _divider(),
        # ── Footer ────────────────────────────────────────────────────
        _context(
            "📍 Guntur (16.3067°N, 80.4365°E)  •  IST (UTC+5:30)  •  "
            "Calculated with Skyfield — Lahiri Ayanamsa  •  "
            "🕉 శుభం భూయాత్"
        ),
    ])

    return {"blocks": blocks}
