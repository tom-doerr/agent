#!/usr/bin/env python3
"""Helper for curating `truth_set.ndjson`.

Features
========
1. Reads **decisions.ndjson** (created by `ambient_agent.py`).
2. Filters only the rows where `helpful == "yes"`.
3. Interactive or batch modes:
   • Default *interactive* mode: presents each helpful item, you press
     `y` to add to truth set, `n` to skip, `q` to quit.
   • `--export` *path* : non-interactive – export **all** helpful rows
     to the given NDJSON file (defaults to `truth_set.ndjson`). Existing
     file is appended to.
   • `--print` : just pretty-print helpful items and exit.

This keeps the prototype minimal and without extra dependencies – only
`json` and stdlib.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Iterable, List

DEFAULT_DECISIONS = Path("decisions.ndjson")
DEFAULT_TRUTH = Path("truth_set.ndjson")


# ---------------------------------------------------------------------------
# Helpers – shared with ambient_agent (duplicated to avoid import time cost)
# ---------------------------------------------------------------------------

def ndjson_iter(path: Path) -> Iterable[Dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def append(path: Path, obj: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Core functionality
# ---------------------------------------------------------------------------


def load_helpful(decisions_path: Path = DEFAULT_DECISIONS) -> List[Dict]:
    """Return list of items where the model decided `helpful == "yes"`."""
    return [row for row in ndjson_iter(decisions_path) if row.get("helpful") == "yes"]


def export_helpful(out_path: Path, decisions_path: Path = DEFAULT_DECISIONS) -> int:
    """Append all helpful rows to *out_path*.  Returns number of rows written."""
    rows = load_helpful(decisions_path)
    for r in rows:
        # Remove classification fields – leave user to edit if needed
        r = {k: v for k, v in r.items() if k not in {"helpful", "nugget"}}
        append(out_path, r)
    return len(rows)


def interactive_label(decisions_path: Path = DEFAULT_DECISIONS, truth_path: Path = DEFAULT_TRUTH) -> None:
    """Interactive TUI in the terminal (stdin/stdout).

    Shows each helpful candidate and waits for user input:
    y / ENTER  → add to truth set
    n          → skip
    q          → quit
    """
    rows = load_helpful(decisions_path)
    if not rows:
        print("No helpful rows found – run ambient_agent.py first")
        return

    print("Press y/ENTER to accept, n to skip, q to quit\n")
    for row in rows:
        print("-" * 80)
        print(f"ID: {row['id']}")
        print(f"Text:\n{row['text']}")
        print("-" * 80)
        ans = input("Add to truth set? [Y/n/q]: ").strip().lower()
        if ans in {"", "y", "yes"}:
            cleaned = {k: v for k, v in row.items() if k not in {"helpful", "nugget"}}
            append(truth_path, cleaned)
            print("✓ added\n")
        elif ans == "q":
            print("Quitting …")
            break
        else:
            print("✗ skipped\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: List[str] | None = None) -> argparse.Namespace:  # noqa: D401 – simple
    p = argparse.ArgumentParser(description="Label helper for ambient agent decisions")
    p.add_argument("--decisions", type=Path, default=DEFAULT_DECISIONS, help="Path to decisions.ndjson")
    group = p.add_mutually_exclusive_group()
    group.add_argument("--print", action="store_true", help="Just print helpful items and exit")
    group.add_argument("--export", nargs="?", const=str(DEFAULT_TRUTH), help="Export all helpful to given NDJSON (default truth_set.ndjson)")
    return p.parse_args(argv)


def main(argv: List[str] | None = None) -> None:  # noqa: D401 – simple
    args = parse_args(argv)

    if args.print:
        for row in load_helpful(args.decisions):
            print(json.dumps(row, indent=2, ensure_ascii=False))
        return

    if args.export is not None:
        out = Path(args.export)
        n = export_helpful(out, args.decisions)
        print(f"Wrote {n} rows to {out}")
        return

    # default: interactive
    interactive_label(args.decisions, DEFAULT_TRUTH)


if __name__ == "__main__":
    main()
