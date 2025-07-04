#!/usr/bin/env python3
"""Test Telegram connection"""

import asyncio
from telethon import TelegramClient
from dotenv import load_dotenv
import os

# Load credentials
load_dotenv('.env.telegram')
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")

async def test_connection():
    print("🔄 Testing Telegram connection...")
    
    client = TelegramClient('test_session', API_ID, API_HASH)
    
    try:
        await client.start()
        print("✅ Connected to Telegram!")
        
        # Get your user info
        me = await client.get_me()
        print(f"👤 Logged in as: {me.first_name} (@{me.username})")
        
        # Get recent chats
        print("\n📱 Recent chats:")
        dialogs = await client.get_dialogs(limit=5)
        for dialog in dialogs:
            print(f"  - {dialog.name}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_connection())