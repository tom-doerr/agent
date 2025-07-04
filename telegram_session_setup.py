#!/usr/bin/env python3
"""Setup Telegram session interactively"""

import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv
import os

# Load credentials
load_dotenv('.env.telegram')
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")

async def setup_session():
    print("🔧 Telegram Session Setup")
    print("=" * 40)
    
    # Use StringSession to get a portable session string
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    
    await client.start()
    
    print("\n✅ Successfully logged in!")
    
    # Get session string
    session_string = client.session.save()
    
    print("\n📝 Your session string (save this!):")
    print("=" * 40)
    print(session_string)
    print("=" * 40)
    
    print("\n💡 Add this to your .env.telegram file:")
    print(f"TELEGRAM_SESSION_STRING={session_string}")
    
    # Show user info
    me = await client.get_me()
    print(f"\n👤 Logged in as: {me.first_name} (@{me.username})")
    
    await client.disconnect()

if __name__ == "__main__":
    print("This will authenticate you with Telegram.")
    print("You'll need to enter your phone number and the code Telegram sends you.\n")
    asyncio.run(setup_session())