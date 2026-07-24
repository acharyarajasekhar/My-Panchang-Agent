# My-Panchang-Agent - Future Reference Guide V2

This document is the operational reference for maintaining and extending this project.

## 1) Purpose

Generate a daily Panchangam for Guntur, Andhra Pradesh, and deliver it to Slack at 06:00 IST with English + Telugu sections.

Core stack:
- Astronomy: Skyfield (local ephemeris file: de421.bsp)
- Scheduling: APScheduler (blocking scheduler)
- Delivery: Slack Incoming Webhook

## 2) Current Architecture

- config.py
  - Location, timezone, scheduler time, language selection, webhook config
- main.py
  - One-shot execution entry and CLI
- scheduler.py
  - Daily cron trigger (06:00 Asia/Kolkata)
- panchang/ephemeris.py
  - Sunrise/sunset, sidereal longitudes, new moon, Sankranti detection
- panchang/calculations.py
  - Tithi, Nakshatra, Yoga, Karana, Masa, Paksha, Samvatsara, Ayana, Ritu
- panchang/timings.py
  - Rahu Kalam, Yamagandam, Gulika Kalam, Durmuhurtam
- formatter/english.py
  - English rendering strings
- formatter/telugu.py
  - Telugu rendering strings
- formatter/blocks.py
  - Slack Block Kit payload assembly
- slack_sender.py
  - Webhook POST transport

## 3) Config and Secrets

All runtime configuration is in config.py.

Required for production posting:
- SLACK_WEBHOOK_URL environment variable

Optional local fallback:
- SLACK_WEBHOOK_URL_FALLBACK environment variable

Recommended language default:
- MESSAGE_LANGUAGE = ["english", "telugu"]

## 4) How to Run

From workspace root:

1. Install dependencies
   - pip install -r requirements.txt

2. Dry run (no Slack post)
   - python main.py --dry-run

3. Post once immediately
   - python main.py --now

4. Start scheduler daemon (daily at configured time)
   - python main.py

## 5) Panchangam Calculation Notes

### 5.1 Sidereal conversion
- Tropical ecliptic longitudes from Skyfield are converted to Nirayana using Lahiri ayanamsha.

### 5.2 Tithi / Nakshatra / Yoga / Karana
- Tithi: (Moon - Sun) / 12 degrees
- Nakshatra: Moon / (360/27)
- Yoga: (Sun + Moon) / (360/27)
- Karana: half-Tithi (6 degree elongation blocks)
- End times are solved using boundary crossing search in Julian day space.

### 5.3 Masa and Adhika/Nija rules (Amanta)
- Lunar month boundaries are new moon to new moon.
- Month status is based on Sankranti count between consecutive new moons:
  - 0 Sankrantis: Adhika month
  - Month after an Adhika cycle with transit restored: Nija month
- Month naming uses Amanta mapping offset from the Sun sign at new moon.

## 6) Formatter and Message Layout

Current Slack style is sequential bilingual:
1. Header + date/location
2. English section (calendar, pancha anga, timings)
3. Telugu section (calendar, pancha anga, timings)
4. Footer context

## 7) Troubleshooting

### 7.1 Webhook error
Symptom:
- SlackSendError: SLACK_WEBHOOK_URL is not set

Action:
- Export SLACK_WEBHOOK_URL before running --now or scheduler mode.

### 7.2 Unexpected Masa label
Action checklist:
- Verify de421.bsp is present in repo root.
- Dry-run target date and inspect new moon + Sankranti values.
- Confirm configured location/timezone values are correct.

### 7.3 Scheduler not posting
Action checklist:
- Confirm process is alive.
- Confirm system clock/timezone are correct.
- Confirm network access to hooks.slack.com.

## 8) Known Limitations

- Varjyam is computed from Nakshatra tyajya offsets; verify against local almanac references if you tune constants.
- Samvatsara rollover logic uses a practical approximation around Ugadi in April.
- No automated unit-test suite yet.

## 9) Recommended Next Improvements

1. Implement full Varjyam calculation from Nakshatra segment logic.
2. Add regression tests for known reference dates (including Adhika/Nija transitions).
3. Add structured logging with daily run summaries.
4. Add retry/backoff for transient Slack network failures.

## 10) Clean Workspace Policy

The following are generated artifacts and should not be committed:
- output.txt
- __pycache__/ directories
- virtual environment files

Project .gitignore already excludes these.
