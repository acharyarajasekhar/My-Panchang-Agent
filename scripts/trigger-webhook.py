#!/usr/bin/env python3
"""
Trigger Panchangam GitHub Workflow Dispatch
Manually trigger the Panchangam calculation workflow via GitHub API

Usage:
    # Windows (with virtual environment)
    .\.venv\Scripts\python.exe scripts\trigger-webhook.py                    # Uses today's date
    .\.venv\Scripts\python.exe scripts\trigger-webhook.py "2026-06-15"       # Specific date
    .\.venv\Scripts\python.exe scripts\trigger-webhook.py --date "2026-06-15"

    # Linux/Mac (with virtual environment activated)
    python scripts/trigger-webhook.py                    # Uses today's date
    python scripts/trigger-webhook.py "2026-06-15"       # Specific date
    python scripts/trigger-webhook.py --date "2026-06-15"

Environment Variables (from .env):
    PANCHANG_GITHUB_TOKEN - GitHub personal access token
    GITHUB_OWNER - Repository owner username
    GITHUB_REPO - Repository name
"""

import requests
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Configuration - read from environment variables
GITHUB_TOKEN = os.environ.get("PANCHANG_GITHUB_TOKEN")
GITHUB_OWNER = os.environ.get("GITHUB_OWNER")
GITHUB_REPO = os.environ.get("GITHUB_REPO")
GITHUB_EVENT_TYPE = os.environ.get("GITHUB_EVENT_TYPE", "panchang-webhook")


def validate_date(date_str: str) -> bool:
    """Validate date format YYYY-MM-DD"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def trigger_workflow(date: str) -> bool:
    """
    Trigger GitHub workflow dispatch
    
    Args:
        date: Date in YYYY-MM-DD format
        
    Returns:
        True if successful, False otherwise
    """
    if not GITHUB_TOKEN:
        print("❌ Error: GitHub token not found.")
        print("   Set PANCHANG_GITHUB_TOKEN in .env file or environment")
        return False
    
    if not GITHUB_OWNER:
        print("❌ Error: GitHub owner not found.")
        print("   Set GITHUB_OWNER in .env file or environment")
        return False
    
    if not GITHUB_REPO:
        print("❌ Error: GitHub repository name not found.")
        print("   Set GITHUB_REPO in .env file or environment")
        return False
    
    if not validate_date(date):
        print(f"❌ Error: Invalid date format: {date}")
        print("   Use YYYY-MM-DD format (e.g., 2026-06-15)")
        return False
    
    # Prepare request
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.github.v3+json"
    }
    
    payload = {
        "event_type": GITHUB_EVENT_TYPE,
        "client_payload": {
            "date": date
        }
    }
    
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/dispatches"
    
    print(f"\n🔄 Triggering workflow for date: {date}")
    print(f"📦 Repository: {GITHUB_OWNER}/{GITHUB_REPO}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 204:
            print(f"✅ Workflow triggered successfully!")
            print(f"📍 Check status: https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/actions")
            return True
        elif response.status_code == 401:
            print("❌ Error: Invalid GitHub token (401 Unauthorized)")
            return False
        elif response.status_code == 404:
            print(f"❌ Error: Repository not found (404)")
            print(f"   Check GITHUB_OWNER and GITHUB_REPO settings")
            return False
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending request: {e}")
        return False


def main():
    """Main entry point"""
    # Parse command line arguments
    date = None
    
    if len(sys.argv) > 1:
        # Handle --date flag or positional argument
        if sys.argv[1] in ["--date", "-d"] and len(sys.argv) > 2:
            date = sys.argv[2]
        else:
            date = sys.argv[1]
    
    # Use today's date if not provided
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Trigger the workflow
    success = trigger_workflow(date)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
