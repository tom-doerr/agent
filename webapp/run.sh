#!/bin/bash
# Script to run the webapp with proper environment setup

# Load environment from parent directory if exists
if [ -f "../.env" ]; then
    echo "Loading environment from ../.env"
    export $(grep -v '^#' ../.env | xargs)
fi

# Load local environment if exists
if [ -f ".env" ]; then
    echo "Loading environment from .env"
    export $(grep -v '^#' .env | xargs)
fi

# Check for API key
if [ -z "$GEMINI_API_KEY" ] && [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  Warning: No Gemini API key found!"
    echo "Please set GEMINI_API_KEY or GOOGLE_API_KEY in your .env file"
    echo "Get your API key from: https://makersuite.google.com/app/apikey"
    echo ""
    echo "Running in mock mode..."
fi

# Run docker compose with environment
docker compose up "$@"