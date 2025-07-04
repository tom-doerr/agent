#!/usr/bin/env python3
"""First-time Telegram setup - run this once to authenticate"""

import asyncio
from telethon import TelegramClient
from dotenv import load_dotenv
import os

# Load credentials
load_dotenv('.env.telegram')
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")

async def first_setup():
    print("🔧 Telegram First-Time Setup")
    print("=" * 40)
    print("You'll need to:")
    print("1. Enter your phone number (with country code, e.g., +1234567890)")
    print("2. Enter the code Telegram sends you")
    print("3. Enter your 2FA password if you have one")
    print("=" * 40)
    print()
    
    client = TelegramClient('telegram_session', API_ID, API_HASH)
    
    # This will prompt for phone/code
    await client.start()
    
    # Test that it works
    me = await client.get_me()
    print(f"\n✅ Success! Logged in as: {me.first_name} (@{me.username})")
    
    # Show recent messages
    print("\n📱 Your recent chats:")
    count = 0
    async for dialog in client.iter_dialogs(limit=5):
        count += 1
        print(f"  {count}. {dialog.name}")
    
    print("\n✅ Setup complete! You can now use the other scripts without authentication.")
    print("Session saved to: telegram_session.session")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(first_setup())