#!/usr/bin/env bash
# Script to set up the Python environment for the Agent project
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON=${PYTHON:-python3.11}
# If the configured python version isn't available or fails to run, fall back to
# `python3` which should be present on most systems. Simply checking for the
# command is insufficient when tools like `pyenv` provide shims that may be
# present but not functional, so we attempt to execute `--version`.
if ! "$PYTHON" --version >/dev/null 2>&1; then
    echo "$PYTHON not found or not functional, falling back to python3" >&2
    PYTHON=python3
fi

VENV_DIR="$SCRIPT_DIR/.venv"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"

if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "Could not find requirements file at $REQUIREMENTS_FILE" >&2
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    "$PYTHON" -m venv "$VENV_DIR"
fi

VENV_PYTHON="$VENV_DIR/bin/python"
if [ ! -x "$VENV_PYTHON" ]; then
    echo "Virtual environment is missing expected Python interpreter at $VENV_PYTHON" >&2
    exit 1
fi

install_with_pip() {
    "$VENV_PYTHON" -m pip install --requirement "$REQUIREMENTS_FILE"
}

# Install dependencies using uv if available, otherwise fall back to pip.
if command -v uv >/dev/null 2>&1; then
    if ! uv pip install --python "$VENV_PYTHON" --requirement "$REQUIREMENTS_FILE"; then
        echo "uv pip install failed, falling back to pip" >&2
        install_with_pip
    fi
else
    install_with_pip
fi

ENV_EXAMPLE="$SCRIPT_DIR/.env.example"
if [ ! -f "$ENV_EXAMPLE" ]; then
    cat > "$ENV_EXAMPLE" <<'ENV'
# Example environment variables for the Agent project
# Copy this file to `.env` and fill in your own values.
OPENROUTER_API_KEY=
FIRECRAWL_API_KEY=
OLLAMA_MODEL=phi3
OLLAMA_BASE_URL=http://localhost:11434
ENV
    echo "Created example environment file at $ENV_EXAMPLE"
fi

echo "Environment setup complete."
echo "Activate the virtual environment with: source '$VENV_DIR/bin/activate'"
