#!/usr/bin/env python3
"""Append a single line to constraints.md with daily headings.

Minimal CLI:
  - Positional message text (required)
  - Optional --now 'YYYY-MM-DD HH:MM:SS' for tests

Paths resolve via timestamp_app_core so files live outside the repo by default
(~/.nlco/private/*) unless overridden by env (e.g., NLCO_CONSTRAINTS_PATH).
"""
from __future__ import annotations

from datetime import datetime, date
from pathlib import Path
import argparse
import sys

from pathlib import Path as _P
import sys as _sys
_sys.path.insert(0, str(_P(__file__).resolve().parents[1]))
from timestamp_app_core import resolve_constraints_path
from file_lock import locked_file
from constraints_io import build_append_block
from backups import ensure_backups


def _extract_last_date(text: str) -> date | None:
    for line in reversed(text.splitlines()):
        s = line.strip()
        if s.startswith("# ") and len(s) >= 12:
            try:
                return datetime.strptime(s[2:], "%Y-%m-%d").date()
            except ValueError:
                continue
    return None


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument("message", nargs=argparse.REMAINDER, help="text to append")
    p.add_argument("--now", dest="now", default=None, help="override timestamp (tests)")
    ns = p.parse_args(argv)

    msg = " ".join(ns.message).strip()
    if not msg:
        print("usage: constraints_add_entry.py <message>", file=sys.stderr)
        return 2

    now = (
        datetime.strptime(ns.now, "%Y-%m-%d %H:%M:%S") if ns.now else datetime.now()
    )
    d = now.date()
    line = f"{now.strftime('%H:%M:%S')} {msg}"

    path: Path = resolve_constraints_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    with locked_file(path, "a+") as fh:
        try:
            fh.seek(0)
            existing = fh.read()
        except Exception:
            existing = ""
        try:
            ensure_backups(path, content=existing)
        except Exception:
            pass
        needs_heading = (_extract_last_date(existing) != d) and (f"# {d:%Y-%m-%d}" not in existing)
        fh.seek(0, 2)
        fh.write(build_append_block(existing, needs_heading, f"{d:%Y-%m-%d}", line))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
