#!/usr/bin/env bash
# Launch the NLCO HTMX FastAPI server with sensible defaults.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${SCRIPT_DIR}"
cd "${REPO_ROOT}"

APP_MODULE="${NLCO_WEB_APP_MODULE:-webapp.nlco_htmx.app:app}"
HOST="${NLCO_WEB_HOST:-127.0.0.1}"
PORT="${NLCO_WEB_PORT:-48123}"
RELOAD="${NLCO_WEB_RELOAD:-true}"
WORKERS="${NLCO_WEB_WORKERS:-1}"
LOG_LEVEL="${NLCO_WEB_LOG_LEVEL:-}" # allow override or default to uvicorn's default
EXTRA_OPTS="${NLCO_WEB_EXTRA_OPTS:-}" # optional additional CLI flags
PYTHON_BIN="${NLCO_PYTHON_BIN:-python}"

ENV_FILE="${NLCO_ENV_FILE:-.env}"
if [[ -f "${ENV_FILE}" ]]; then
  echo "Loading environment overrides from ${ENV_FILE}"
  set -a
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
  set +a
fi

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "Error: ${PYTHON_BIN} not found on PATH." >&2
  exit 1
fi

export PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"

cmd=("${PYTHON_BIN}" -m uvicorn "${APP_MODULE}" --host "${HOST}" --port "${PORT}")

if [[ "${RELOAD}" == "true" ]]; then
  cmd+=(--reload)
else
  cmd+=(--workers "${WORKERS}")
fi

if [[ -n "${LOG_LEVEL}" ]]; then
  cmd+=(--log-level "${LOG_LEVEL}")
fi

if [[ -n "${EXTRA_OPTS}" ]]; then
  # shellcheck disable=SC2206
  extra_args=(${EXTRA_OPTS})
  cmd+=("${extra_args[@]}")
fi

echo "Running: ${cmd[*]}"
exec "${cmd[@]}"
