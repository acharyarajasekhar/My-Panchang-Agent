"""
main.py
────────
Entry point for the Panchangam agent.

Usage
─────
Run immediately (calculate today and post to Slack):
    python main.py --now

Start the 6 AM IST daily scheduler (blocks until Ctrl-C):
    python main.py

Dry-run (print the formatted payload to stdout, do NOT post to Slack):
    python main.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import date, datetime
from zoneinfo import ZoneInfo

log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────
# Core function — called by scheduler and by --now / --dry-run
# ─────────────────────────────────────────────────────────────────────

def run_once(target: date | None = None, dry_run: bool = False) -> None:
    """
    Calculate the Panchangam for *target* (defaults to today), build the
    Slack payload, and optionally post it.

    Parameters
    ----------
    target  : The date to calculate for.  Defaults to ``date.today()``.
    dry_run : If True, print the payload JSON to stdout instead of sending.
    """
    from panchang.calculations import calculate
    from panchang.timings import get_timings
    from formatter.blocks import build_payload
    from slack_sender import send
    from config import MESSAGE_LANGUAGE, TIMEZONE

    if target is None:
        target = datetime.now(ZoneInfo(TIMEZONE)).date()

    log.info("Calculating Panchangam for %s …", target.isoformat())

    panchang_result = calculate(target)
    timings         = get_timings(target)
    payload         = build_payload(panchang_result, timings, languages=MESSAGE_LANGUAGE)

    if dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        log.info("Dry-run complete — payload printed to stdout.")
        return

    send(payload)
    log.info("Done.")


# ─────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="My-Panchang-Agent — Daily Panchangam for Guntur via Slack",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--now",
        action="store_true",
        help="Calculate today's Panchangam and post to Slack immediately.",
    )
    group.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the Slack payload JSON to stdout without posting.",
    )
    parser.add_argument(
        "--date",
        type=date.fromisoformat,
        default=None,
        metavar="YYYY-MM-DD",
        help="Override the date (default: today).  Works with --now and --dry-run.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    args = _parse_args()

    if args.now:
        run_once(target=args.date, dry_run=False)

    elif args.dry_run:
        run_once(target=args.date, dry_run=True)

    else:
        # Default: start the 6 AM scheduler
        import scheduler
        scheduler.start()
