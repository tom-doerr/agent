#!/usr/bin/env python3
"""Check Telegram authentication status"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load credentials
load_dotenv('.env.telegram')

print("🔍 Telegram Setup Status")
print("=" * 40)

# Check API credentials
api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")

print(f"✅ API_ID: {api_id}")
print(f"✅ API_HASH: {api_hash[:8]}...")

# Check for existing session
session_file = Path("telegram_session.session")
if session_file.exists():
    print(f"✅ Session file exists: {session_file}")
    print("   You should be able to connect without authentication!")
else:
    print(f"❌ No session file found")
    print("   You need to authenticate once with your phone number")
    print("\n📱 Run this command to authenticate:")
    print("   .venv/bin/python telegram_first_run.py")
    print("\n   This is only needed ONCE. After that, it remembers you.")

print("\n💡 Think of it like:")
print("   - API ID/Hash = Your app's credentials (✅ done)")
print("   - Phone auth = Logging into your account (❌ needed once)")