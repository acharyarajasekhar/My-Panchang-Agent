"""
slack_sender.py
────────────────
Sends a pre-built Slack Block Kit payload to the configured Incoming Webhook.

Usage:
    from slack_sender import send
    send(payload)   # payload = formatter/blocks.py → build_payload(...)

Security:
  • The webhook URL is read from the SLACK_WEBHOOK_URL environment variable
    (never hard-coded).  See config.py.
  • Raises SlackSendError on any non-2xx response so the caller can log/retry.
"""

from __future__ import annotations

import json
import logging

import requests

from config import SLACK_WEBHOOK_URL

log = logging.getLogger(__name__)

_TIMEOUT_SECONDS = 10


class SlackSendError(RuntimeError):
    """Raised when Slack returns a non-2xx response."""


def send(payload: dict) -> None:
    """
    POST *payload* as JSON to the configured Slack Incoming Webhook.

    Parameters
    ----------
    payload : dict
        A Slack Block Kit payload, as returned by ``formatter.blocks.build_payload()``.

    Raises
    ------
    SlackSendError
        If the webhook URL is not configured, or Slack returns a non-2xx status.
    requests.exceptions.RequestException
        On network-level errors (timeout, DNS failure, etc.).
    """
    if not SLACK_WEBHOOK_URL:
        raise SlackSendError(
            "SLACK_WEBHOOK_URL is not set. "
            "Export it as an environment variable before running."
        )

    response = requests.post(
        SLACK_WEBHOOK_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        timeout=_TIMEOUT_SECONDS,
    )

    if response.status_code != 200:
        raise SlackSendError(
            f"Slack webhook returned HTTP {response.status_code}: {response.text!r}"
        )

    log.info("Panchangam posted to Slack successfully.")
