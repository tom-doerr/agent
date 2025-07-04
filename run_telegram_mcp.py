#!/usr/bin/env python3
"""Run the Telegram MCP server"""

import os
import sys
from pathlib import Path

# Add the telegram-mcp repo to Python path
telegram_mcp_path = Path(__file__).parent / "telegram-mcp-repo"
sys.path.insert(0, str(telegram_mcp_path))

# Set environment variables if not already set
if "TELEGRAM_API_ID" not in os.environ:
    print("Please set TELEGRAM_API_ID environment variable")
    print("Get it from https://my.telegram.org")
    sys.exit(1)

if "TELEGRAM_API_HASH" not in os.environ:
    print("Please set TELEGRAM_API_HASH environment variable")
    print("Get it from https://my.telegram.org")
    sys.exit(1)

# Import and run the main module
from main import main

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())