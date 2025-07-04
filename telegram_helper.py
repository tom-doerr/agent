#!/usr/bin/env python3
"""Simple Telegram helper for DSPy integration"""

import asyncio
from telethon import TelegramClient
from dotenv import load_dotenv
import os

# Load credentials
load_dotenv('.env.telegram')
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")

class TelegramHelper:
    def __init__(self):
        self.client = TelegramClient('telegram_session', API_ID, API_HASH)
        self.connected = False
    
    async def connect(self):
        """Connect to Telegram (reuses existing session)"""
        if not self.connected:
            await self.client.start()
            self.connected = True
    
    async def get_messages(self, chat=None, limit=10):
        """Get recent messages from a chat or all chats"""
        await self.connect()
        
        messages = []
        if chat:
            # Get from specific chat
            async for msg in self.client.iter_messages(chat, limit=limit):
                messages.append({
                    'text': msg.text,
                    'from': msg.sender_id,
                    'date': msg.date.isoformat()
                })
        else:
            # Get from recent chats
            async for dialog in self.client.iter_dialogs(limit=limit):
                if dialog.message:
                    messages.append({
                        'chat': dialog.name,
                        'text': dialog.message.text,
                        'date': dialog.message.date.isoformat()
                    })
        
        return messages
    
    async def send_message(self, chat, text):
        """Send a message"""
        await self.connect()
        await self.client.send_message(chat, text)
        return f"Sent to {chat}: {text}"
    
    async def disconnect(self):
        """Disconnect from Telegram"""
        if self.connected:
            await self.client.disconnect()
            self.connected = False


# Simple functions for direct use
async def get_latest_messages(limit=10):
    """Get latest messages - one function call"""
    tg = TelegramHelper()
    messages = await tg.get_messages(limit=limit)
    await tg.disconnect()
    return messages


# Example usage in DSPy
if __name__ == "__main__":
    # Test it
    async def test():
        messages = await get_latest_messages(5)
        for msg in messages:
            print(f"{msg['chat']}: {msg['text'][:50]}...")
    
    asyncio.run(test())