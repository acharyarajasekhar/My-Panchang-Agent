#!/usr/bin/env python3
"""
Test Script for Cloudflare Worker (Slack Bridge)
Generates properly signed Slack events for testing the Cloudflare Worker

This script tests the Cloudflare Worker that acts as a bridge between Slack and GitHub Actions.

Usage:
    python scripts/test_cloudflare_worker.py              # Tests against local worker
    WORKER_URL=<url> python scripts/test_cloudflare_worker.py  # Tests against specific URL
"""

import json
import hashlib
import hmac
import time
import requests
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Configuration - read from environment variables
SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET", "your_slack_signing_secret_here")
WORKER_URL = os.environ.get("WORKER_URL", "http://localhost:8787")
WORKER_URL_PROD = os.environ.get("WORKER_URL_PROD", "https://panchang-slack-bridge.workers.dev")


def create_slack_signature(timestamp: str, body: str, secret: str) -> str:
    """
    Create a valid Slack request signature.
    
    Slack uses HMAC-SHA256 of the format:
    v0:timestamp:body
    """
    sig_basestring = f"v0:{timestamp}:{body}"
    signature = hmac.new(
        secret.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"v0={signature}"


def send_slack_event(event_data: dict, url: str, use_valid_signature: bool = True):
    """Send a Slack event to the worker"""
    
    timestamp = str(int(time.time()))
    body = json.dumps(event_data)
    
    headers = {
        "Content-Type": "application/json",
        "X-Slack-Request-Timestamp": timestamp,
    }
    
    if use_valid_signature:
        headers["X-Slack-Signature"] = create_slack_signature(
            timestamp, body, SIGNING_SECRET
        )
    else:
        headers["X-Slack-Signature"] = "v0=invalid"
    
    print(f"\n{'='*60}")
    print(f"Sending event to: {url}")
    print(f"{'='*60}")
    print(f"Event Type: {event_data.get('type', 'unknown')}")
    print(f"Timestamp: {timestamp}")
    print(f"Signature: {headers['X-Slack-Signature']}")
    print(f"Body: {json.dumps(event_data, indent=2)}")
    
    try:
        response = requests.post(
            url,
            headers=headers,
            data=body,
            timeout=10
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Event accepted!")
        else:
            print(f"❌ Event rejected: {response.status_code}")
            
        return response
        
    except Exception as e:
        print(f"❌ Error sending event: {e}")
        return None


# Test Events

def test_url_verification():
    """Test Slack URL verification challenge"""
    event = {
        "type": "url_verification",
        "challenge": "3eZbrw1aBrskbtA"
    }
    return send_slack_event(event, f"{WORKER_URL}/slack/events")


def test_app_mention_simple():
    """Test app mention with simple YYYY-MM-DD date"""
    event = {
        "type": "event_callback",
        "event": {
            "type": "app_mention",
            "user": "U12345678",
            "text": "<@U999999> please calculate for 2026-06-15",
            "channel": "C87654321",
            "ts": "1234567890.000100"
        }
    }
    return send_slack_event(event, f"{WORKER_URL}/slack/events")


def test_message_with_date():
    """Test message containing date"""
    event = {
        "type": "event_callback",
        "event": {
            "type": "message",
            "user": "U12345678",
            "text": "Calculate panchangam for 2026-06-15",
            "channel": "C87654321",
            "ts": "1234567890.000100",
            "thread_ts": "1234567890.000050"
        }
    }
    return send_slack_event(event, f"{WORKER_URL}/slack/events")


def test_invalid_signature():
    """Test with invalid signature (should be rejected)"""
    event = {
        "type": "event_callback",
        "event": {
            "type": "app_mention",
            "text": "<@U999999> 2026-06-15",
            "user": "U12345678",
            "channel": "C87654321",
        }
    }
    return send_slack_event(event, f"{WORKER_URL}/slack/events", use_valid_signature=False)


def test_invalid_date_format():
    """Test with invalid date format (should be rejected)"""
    event = {
        "type": "event_callback",
        "event": {
            "type": "app_mention",
            "text": "<@U999999> please calculate for 2026-13-45",
            "user": "U12345678",
            "channel": "C87654321",
        }
    }
    return send_slack_event(event, f"{WORKER_URL}/slack/events")


def test_message_no_date():
    """Test message without date (should be ignored)"""
    event = {
        "type": "event_callback",
        "event": {
            "type": "message",
            "user": "U12345678",
            "text": "Just a regular message",
            "channel": "C87654321",
        }
    }
    return send_slack_event(event, f"{WORKER_URL}/slack/events")


def test_natural_language_date():
    """Test natural language date format"""
    event = {
        "type": "event_callback",
        "event": {
            "type": "message",
            "user": "U12345678",
            "text": "Calculate panchangam for June 15, 2026",
            "channel": "C87654321",
        }
    }
    return send_slack_event(event, f"{WORKER_URL}/slack/events")


def test_health_check():
    """Test health check endpoint"""
    try:
        response = requests.get(f"{WORKER_URL}/health")
        print(f"\n{'='*60}")
        print("Health Check")
        print(f"{'='*60}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Worker is healthy!")
        return response
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return None


def main():
    """Run tests"""
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        
        tests = {
            "health": test_health_check,
            "verify": test_url_verification,
            "mention": test_app_mention_simple,
            "message": test_message_with_date,
            "invalid_sig": test_invalid_signature,
            "invalid_date": test_invalid_date_format,
            "no_date": test_message_no_date,
            "natural": test_natural_language_date,
        }
        
        if test_name in tests:
            tests[test_name]()
        else:
            print(f"Unknown test: {test_name}")
            print(f"Available tests: {', '.join(tests.keys())}")
    else:
        print("Cloudflare Worker (Slack Bridge) - Test Suite")
        print("="*60)
        print("\nUsage: python scripts/test_cloudflare_worker.py <test_name>")
        print("\nAvailable tests:")
        print("  health      - Health check")
        print("  verify      - Slack URL verification")
        print("  mention     - App mention with date")
        print("  message     - Message with date")
        print("  invalid_sig - Test invalid signature (should fail)")
        print("  invalid_date - Test invalid date format")
        print("  no_date     - Message without date (should be ignored)")
        print("  natural     - Natural language date")
        print("\nRun all tests:")
        print("  python scripts/test_cloudflare_worker.py verify && \\")
        print("  python scripts/test_cloudflare_worker.py mention && \\")
        print("  python scripts/test_cloudflare_worker.py message && \\")
        print("  python scripts/test_cloudflare_worker.py invalid_sig")


if __name__ == "__main__":
    main()
