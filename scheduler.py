"""
scheduler.py
─────────────
Configures an APScheduler BlockingScheduler to fire main.run_once()
every morning at 06:00 IST.

Run this module directly to start the scheduler daemon:
    python scheduler.py

The scheduler blocks the calling thread.  Run it inside a process manager
(systemd, Docker, supervisord) for production use.
"""

from __future__ import annotations

import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

import config

log = logging.getLogger(__name__)


def start() -> None:
    """Start the blocking daily scheduler.  Never returns unless interrupted."""
    scheduler = BlockingScheduler(timezone=config.TIMEZONE)

    scheduler.add_job(
        func=_job,
        trigger=CronTrigger(
            hour=config.SCHEDULE_HOUR,
            minute=config.SCHEDULE_MINUTE,
            timezone=config.TIMEZONE,
        ),
        id="daily_panchangam",
        name="Daily Panchangam → Slack",
        misfire_grace_time=300,   # allow up to 5 min late start
        replace_existing=True,
    )

    log.info(
        "Scheduler started. Panchangam will post at %02d:%02d IST daily.",
        config.SCHEDULE_HOUR,
        config.SCHEDULE_MINUTE,
    )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log.info("Scheduler stopped.")


def _job() -> None:
    """APScheduler job: calculate today's Panchangam and post to Slack."""
    # Import here to avoid circular issues and to keep the scheduler module light.
    import main  # noqa: PLC0415
    main.run_once()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    start()
