#!/usr/bin/env python3
"""Get newest Telegram messages - simple and direct"""

import asyncio
from telethon import TelegramClient
from dotenv import load_dotenv
import os
from datetime import datetime

# Load credentials
load_dotenv('.env.telegram')
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")

async def get_recent_messages():
    # Use a persistent session file
    client = TelegramClient('telegram_session', API_ID, API_HASH)
    
    try:
        # This will use existing session or ask for phone/code on first run
        await client.start()
        print("✅ Connected!\n")
        
        # Get recent dialogs (chats)
        print("📱 Recent messages:\n")
        
        async for dialog in client.iter_dialogs(limit=10):
            # Skip if no messages
            if not dialog.message:
                continue
                
            # Format time
            time_str = dialog.message.date.strftime("%H:%M")
            
            # Get sender name
            if dialog.message.out:
                sender = "You"
            else:
                sender = dialog.name
            
            # Print message
            print(f"[{time_str}] {dialog.name}")
            print(f"  {sender}: {dialog.message.text or '[Media]'}")
            print()
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(get_recent_messages())