#!/usr/bin/env python3
"""
Test Script for Panchang Slack API
Generates valid Slack events with proper signatures to test the Panchang API backend

This script tests the Python backend that processes Slack events and generates Panchangam data.

Usage:
    python scripts/test_panchang_slack_api.py app_mention 2026-05-22
    python scripts/test_panchang_slack_api.py app_mention 2026-12-25
    python scripts/test_panchang_slack_api.py message 2026-07-04
    python scripts/test_panchang_slack_api.py all 2026-05-22
    python scripts/test_panchang_slack_api.py all

Environment Variables (from .env):
    SLACK_SIGNING_SECRET - Slack app signing secret
    WORKER_URL_PROD - Slack event endpoint URL (default: https://panchang-slack-bridge.workers.dev)
"""

import requests
import hmac
import hashlib
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Configuration - read from environment variables
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET", "your_slack_signing_secret_here")
WORKER_URL = os.environ.get("WORKER_URL_PROD", "https://panchang-slack-bridge.workers.dev")
WORKER_ENDPOINT = f"{WORKER_URL}/slack/events"

def generate_slack_signature(body: str, timestamp: str) -> str:
    """Generate a valid Slack signature"""
    sig_basestring = f"v0:{timestamp}:{body}"
    signature = hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"v0={signature}"

def send_event(event_data: Dict[str, Any], name: str = "Test Event") -> None:
    """Send an event to the worker"""
    timestamp = str(int(datetime.now().timestamp()))
    body = json.dumps(event_data)
    signature = generate_slack_signature(body, timestamp)
    
    headers = {
        "Content-Type": "application/json",
        "X-Slack-Request-Timestamp": timestamp,
        "X-Slack-Signature": signature,
    }
    
    print(f"\n📤 Sending: {name}")
    print(f"   Endpoint: {WORKER_ENDPOINT}")
    print(f"   Timestamp: {timestamp}")
    print(f"   Signature: {signature[:30]}...")
    
    try:
        response = requests.post(WORKER_ENDPOINT, json=event_data, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.text:
            try:
                print(f"   Response: {response.json()}")
            except:
                print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_url_verification():
    """Test Slack URL verification challenge"""
    event = {
        "type": "url_verification",
        "challenge": "3eZbrw1aBrHwhVoBEKw3xj3GdT3F2vA0F3wC",
        "token": "Iv2uVBnCLHcXKm8RyoGHwBzZ"
    }
    send_event(event, "URL Verification Challenge")

def test_app_mention(date: str = "2026-06-15"):
    """Test app_mention event with date"""
    event = {
        "token": "legacy-token",
        "team_id": "T12345678",
        "api_app_id": "A12345678",
        "event": {
            "type": "app_mention",
            "user": "U12345678",
            "text": f"<@U87654321> Please calculate panchangam for {date}",
            "ts": "1234567890.123456",
            "channel": "C12345678",
            "event_ts": "1234567890.123456"
        },
        "type": "event_callback",
        "event_id": "Ev12345678",
        "event_time": 1234567890,
        "response_url": "https://hooks.slack.com/actions/T12345678/..."
    }
    send_event(event, f"App Mention with Date ({date})")

def test_message(date: str = "2026-06-15"):
    """Test message event"""
    event = {
        "token": "legacy-token",
        "team_id": "T12345678",
        "api_app_id": "A12345678",
        "event": {
            "type": "message",
            "user": "U12345678",
            "text": f"calculate panchangam {date}",
            "ts": "1234567890.123456",
            "channel": "C12345678",
            "event_ts": "1234567890.123456"
        },
        "type": "event_callback",
        "event_id": "Ev12345678",
        "event_time": 1234567890,
        "response_url": "https://hooks.slack.com/actions/T12345678/..."
    }
    send_event(event, f"Message Event ({date})")

def test_message_no_date():
    """Test message without date (should fail parsing)"""
    event = {
        "token": "legacy-token",
        "team_id": "T12345678",
        "api_app_id": "A12345678",
        "event": {
            "type": "message",
            "user": "U12345678",
            "text": "hello world",
            "ts": "1234567890.123456",
            "channel": "C12345678",
            "event_ts": "1234567890.123456"
        },
        "type": "event_callback",
        "event_id": "Ev12345678",
        "event_time": 1234567890
    }
    send_event(event, "Message Without Date")

def test_invalid_signature():
    """Test with invalid signature (should be rejected)"""
    event = {
        "type": "event_callback",
        "event": {
            "type": "app_mention",
            "text": "@panchang 2026-06-15"
        }
    }
    
    timestamp = str(int(datetime.now().timestamp()))
    headers = {
        "Content-Type": "application/json",
        "X-Slack-Request-Timestamp": timestamp,
        "X-Slack-Signature": "v0=invalid_signature_12345",
    }
    
    print(f"\n📤 Sending: Invalid Signature Test")
    print(f"   Endpoint: {WORKER_ENDPOINT}")
    print(f"   Status: Should be 401 Unauthorized")
    
    try:
        response = requests.post(WORKER_ENDPOINT, json=event, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.text:
            try:
                print(f"   Response: {response.json()}")
            except:
                print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    print(f"🧪 Panchang Slack API Test Suite")
    print(f"====================================")
    print(f"Worker URL: {WORKER_URL}")
    print(f"Signing Secret: {'SET' if SLACK_SIGNING_SECRET != 'your-slack-signing-secret' else 'NOT SET (update code or env var)'}")
    
    if SLACK_SIGNING_SECRET == "your-slack-signing-secret":
        print("\n⚠️  WARNING: Update SLACK_SIGNING_SECRET in this file or set it as environment variable!")
        print("   You can get it from: https://api.slack.com/apps → Your App → Basic Information")
        return
    
    test_name = sys.argv[1] if len(sys.argv) > 1 else "all"
    date_input = sys.argv[2] if len(sys.argv) > 2 else "2026-06-15"
    
    tests = {
        "url_verification": test_url_verification,
        "app_mention": test_app_mention,
        "message": test_message,
        "message_no_date": test_message_no_date,
        "invalid_sig": test_invalid_signature,
    }
    
    if test_name == "all":
        for name, test_func in tests.items():
            if name in ["app_mention", "message"]:
                test_func(date_input)
            else:
                test_func()
    elif test_name in tests:
        if test_name in ["app_mention", "message"]:
            tests[test_name](date_input)
        else:
            tests[test_name]()
    else:
        print(f"\n❌ Unknown test: {test_name}")
        print(f"\nAvailable tests:")
        for name in tests.keys():
            print(f"  - {name}")
        print(f"\nUsage:")
        print(f"  python scripts/test_panchang_slack_api.py <test_name> [date]")
        print(f"\nExamples:")
        print(f"  python scripts/test_panchang_slack_api.py app_mention")
        print(f"  python scripts/test_panchang_slack_api.py app_mention 2026-05-22")
        print(f"  python scripts/test_panchang_slack_api.py message 2026-12-25")
        print(f"  python scripts/test_panchang_slack_api.py all 2026-07-04")

if __name__ == "__main__":
    main()
