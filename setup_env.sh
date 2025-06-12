#!/usr/bin/env bash
# Script to set up the Python environment for the Agent project
set -euo pipefail

PYTHON=${PYTHON:-python3.11}
if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "$PYTHON not found, falling back to python3" >&2
    PYTHON=python3
fi

if [ ! -d ".venv" ]; then
    "$PYTHON" -m venv .venv
fi

source .venv/bin/activate

# Install dependencies using uv if available, otherwise pip
if command -v uv >/dev/null 2>&1; then
    uv pip install -r requirements.txt
else
    pip install -r requirements.txt
fi

if [ ! -f .env ]; then
    cat > .env.example <<'ENV'
# Copy to .env and fill in your secrets
OPENROUTER_API_KEY=
FIRECRAWL_API_KEY=
OLLAMA_MODEL=phi3
OLLAMA_BASE_URL=http://localhost:11434
ENV
fi

echo "Environment setup complete. Activate with 'source .venv/bin/activate'"
