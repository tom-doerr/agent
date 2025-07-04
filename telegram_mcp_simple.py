#!/usr/bin/env python3
"""
Simple Telegram MCP Server - Just run it!
"""

import os
import sys
import asyncio
from pathlib import Path

# Auto-install dependencies if needed
try:
    from telethon import TelegramClient
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Installing dependencies...")
    os.system("uv pip install telethon mcp python-dotenv")
    from telethon import TelegramClient
    from mcp.server.fastmcp import FastMCP

# Load from .env.telegram
from dotenv import load_dotenv
load_dotenv('.env.telegram')

# Simple setup
API_ID = os.getenv("TELEGRAM_API_ID", "")
API_HASH = os.getenv("TELEGRAM_API_HASH", "")

if not API_ID:
    print("\n🔑 Quick Setup:")
    print("1. Go to https://my.telegram.org")
    print("2. Get your API_ID and API_HASH")
    print("3. Run: export TG_ID=your_id TG_HASH=your_hash")
    print("4. Run this script again\n")
    sys.exit(1)

# Create MCP server
mcp = FastMCP("telegram")
client = TelegramClient("session", int(API_ID), API_HASH)

@mcp.tool()
async def send_message(chat: str, text: str) -> str:
    """Send a message to a Telegram chat"""
    await client.send_message(chat, text)
    return f"Sent: {text}"

@mcp.tool()
async def get_messages(chat: str, limit: int = 10) -> list:
    """Get recent messages from a chat"""
    messages = []
    async for msg in client.iter_messages(chat, limit=limit):
        messages.append({"from": msg.sender_id, "text": msg.text})
    return messages

# Run it
async def main():
    await client.start()
    print("✅ Telegram MCP running!")
    await mcp.run()

if __name__ == "__main__":
    asyncio.run(main())