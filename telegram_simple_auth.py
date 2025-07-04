#!/usr/bin/env python3
"""Simple Telegram auth - handles the sqlite issue"""

import asyncio
import sys
import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

# Load credentials
load_dotenv('.env.telegram')
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")

async def auth():
    # Use string session to avoid sqlite issues
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    
    await client.start()
    
    # Save the session string
    session_string = client.session.save()
    
    # Write to file
    with open('telegram_session.txt', 'w') as f:
        f.write(session_string)
    
    me = await client.get_me()
    print(f"\n✅ Success! Logged in as: {me.first_name}")
    print(f"📝 Session saved to: telegram_session.txt")
    
    await client.disconnect()

if __name__ == "__main__":
    print("Enter your phone and code when prompted...")
    asyncio.run(auth())