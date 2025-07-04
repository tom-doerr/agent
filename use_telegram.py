#!/usr/bin/env python3
"""Use Telegram without MCP - direct and simple"""

import asyncio
from telethon import TelegramClient
from telethon.sessions import MemorySession
from dotenv import load_dotenv
import os

# Load credentials
load_dotenv('.env.telegram')
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")

# Your phone number - already authenticated
PHONE = "+491733415747"

async def get_messages():
    # Use memory session to avoid sqlite issues
    client = TelegramClient(MemorySession(), API_ID, API_HASH)
    
    # Start with your phone number
    await client.start(phone=PHONE)
    
    print("📱 Recent messages:\n")
    
    # Get recent chats
    async for dialog in client.iter_dialogs(limit=10):
        if dialog.message and dialog.message.text:
            print(f"💬 {dialog.name}: {dialog.message.text[:100]}")
            print()
    
    await client.disconnect()

if __name__ == "__main__":
    print("Getting your Telegram messages...")
    asyncio.run(get_messages())