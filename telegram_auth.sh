#!/bin/bash
echo "🔐 Telegram Authentication"
echo "========================="
echo ""
echo "You need to authenticate once with your phone number."
echo "After this, it will remember you."
echo ""
echo "Ready? Press Enter to continue..."
read

.venv/bin/python telegram_first_run.py