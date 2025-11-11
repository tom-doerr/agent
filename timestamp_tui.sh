#!/usr/bin/env sh
# Minimal wrapper: harden TTY/locale and run the timestamp TUI with lenient input.
set -e

# Enable UTF-8 input on real TTYs
[ -t 0 ] && stty iutf8

# Force UTF-8 locale
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

exec ./timestamp_textual_app.py --lenient-input --fallback-encoding cp1252 "$@"

