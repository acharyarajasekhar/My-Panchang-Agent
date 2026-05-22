"""
Configuration for My-Panchang-Agent
All location, timezone, and Slack settings are centralized here.
"""

from dotenv import load_dotenv
import os

# Load environment variables from .env file (if it exists)
load_dotenv()

# --- Location Settings ---
LOCATION = "Guntur, Andhra Pradesh, India"
LATITUDE = 16.3067   # degrees North
LONGITUDE = 80.4365  # degrees East
ALTITUDE = 30        # metres above sea level (approximate)
TIMEZONE = "Asia/Kolkata"

# --- Slack Settings ---
# Set your Slack Incoming Webhook URL as an environment variable:
#   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ
SLACK_WEBHOOK_URL: str = os.environ.get("SLACK_WEBHOOK_URL", "")

# Message languages for Slack: list of "english" and/or "telugu"
# ["telugu"] = Telugu only
# ["english"] = English only
# ["english", "telugu"] or ["telugu", "english"] = Side-by-side bilingual
MESSAGE_LANGUAGE = ["telugu"]

# --- Scheduler Settings ---
# Time to post every morning (24-hour, IST)
SCHEDULE_HOUR = 6
SCHEDULE_MINUTE = 0
