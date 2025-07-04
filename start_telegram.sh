#!/bin/bash
# Super simple Telegram MCP starter

echo "🚀 Telegram MCP - Simple Start"
echo ""

# Check if credentials exist
if [ -z "$TG_ID" ]; then
    echo "📱 First time? Get your credentials:"
    echo "   1. Visit: https://my.telegram.org"
    echo "   2. Login and create an app"
    echo ""
    read -p "Enter your API_ID: " TG_ID
    read -p "Enter your API_HASH: " TG_HASH
    
    echo ""
    echo "# Add to your .bashrc or .zshrc:" 
    echo "export TG_ID=$TG_ID"
    echo "export TG_HASH=$TG_HASH"
    echo ""
    
    export TG_ID
    export TG_HASH
fi

# Run it
python telegram_mcp_simple.py