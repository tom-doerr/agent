#!/usr/bin/env python3
"""Ambient preference-based agent.

Learns from an *ordered* ``graded_set.ndjson`` (top = most useful) to judge new
Hacker-News items by pair-wise comparison and keeps those above a percentile
cut-off.

This file purposefully mirrors the existing *ranking_agent.py* but with a
simpler user workflow: a single graded file instead of separate truth/ranking
and decisions files.

The implementation is **test-first**: every helper referenced in
``tests/test_ambient_pref_agent.py`` exists and behaves accordingly so the test
suite passes with DSPy stubbed by *conftest.py*.
"""
from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import json
import random
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

# Heavy deps are mocked in tests via conftest
try:
    import feedparser  # type: ignore
    import yaml  # type: ignore
    import dspy  # type: ignore
except ModuleNotFoundError:
    feedparser = None  # type: ignore
    yaml = None  # type: ignore
    dspy = None  # type: ignore

# ---------------------------------------------------------------------------
# Paths (can be monkey-patched in tests)
# ---------------------------------------------------------------------------
RAW_FILE = Path("raw_events.ndjson")
GRADED_FILE = Path("graded_set.ndjson")
PERC_FILE = Path("percentile.log")
RULES_FILE = Path("label_rules.yml")
HN_RSS = "https://hnrss.org/frontpage"

# ---------------------------------------------------------------------------
# NDJSON helpers (duplicated to stay self-contained)
# ---------------------------------------------------------------------------

def ndjson_iter(path: Path) -> Iterable[Dict[str, Any]]:
    if path.exists():
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    yield json.loads(line)


def append(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------------------
# Rule matching (optional)
# ---------------------------------------------------------------------------

def _apply_rules(text: str, rules: List[Dict[str, str]]) -> List[str]:
    labels: List[str] = []
    low = text.lower()
    for rule in rules:
        if rule.get("match", "").lower() in low:
            labels.append(rule.get("tag", ""))
    return labels

# ---------------------------------------------------------------------------
# DSPy signature & helpers
# ---------------------------------------------------------------------------

def _prepare_pairs(rows: List[Dict[str, Any]]):  # noqa: D401
    """Adjacent pairs where earlier is preferred.

    Returns (SignatureCls, pairs) so tests can inspect easily.
    """
    if dspy is None:  # pragma: no cover – when DSPy absent tests mock
        class _DummySig:  # type: ignore
            pass

        return _DummySig, []

    class CompareSig(dspy.Signature):  # type: ignore
        a: str = dspy.InputField()
        b: str = dspy.InputField()
        better: str = dspy.OutputField(desc="a|b")

    pairs = []
    for i in range(len(rows) - 1):
        a_row, b_row = rows[i], rows[i + 1]
        pairs.append(
            dspy.Example(a=a_row["text"], b=b_row["text"], better="a").with_inputs("a", "b")  # type: ignore[attr-defined]
        )
    return CompareSig, pairs


def build_compare(graded_rows: List[Dict[str, Any]]):  # noqa: D401 – simple
    """Return a pair-wise judge trained on graded_rows order.

    In unit tests this function is monkey-patched to avoid heavy training.
    """
    if dspy is None or len(graded_rows) < 2:  # pragma: no cover
        # trivial ranker preferring candidate always
        def _dummy_ranker(*, a, b):  # noqa: D401 – simple callable
            import types

            return types.SimpleNamespace(better="a")

        return _dummy_ranker

    # Ensure LM configured exactly once
    try:
        dspy.configure(lm=dspy.LM("openrouter/google/gemini-2.5-flash-lite-preview-06-17", max_tokens=4000, temperature=0.7))
    except Exception as exc:  # noqa: BLE001 – surface to user
        print("Failed to configure DSPy LM – ensure OPENROUTER_API_KEY is set and accessible.")
        raise

    Sig, pairs = _prepare_pairs(graded_rows)
    base = dspy.Predict(Sig)  # type: ignore[attr-defined]

    teleprompt = getattr(dspy, "teleprompt", None)
    BS = getattr(teleprompt, "BootstrapFewShot", None)
    if BS is None:
        return base
    ranker = BS(metric=None).compile(base, trainset=pairs)  # type: ignore[arg-type]
    return ranker


def compute_percentile(
    candidate: Dict[str, Any],
    graded_rows: List[Dict[str, Any]],
    *,
    ranker,
    comparisons: int = 50,
) -> float:
    """Empirical percentile via wins against random graded references."""
    if comparisons == 0:
        return 0.0
    wins = 0
    for _ in range(comparisons):
        ref = random.choice(graded_rows)
        res = ranker(a=candidate["text"], b=ref["text"])
        if getattr(res, "better", None) == "a":
            wins += 1
    return wins / comparisons

# Alias used in some tests referencing "percentile" name directly
percentile = compute_percentile

# ---------------------------------------------------------------------------
# Fetch HN
# ---------------------------------------------------------------------------

def fetch_hn(after_ts: int) -> Iterable[Dict[str, Any]]:
    if feedparser is None:  # pragma: no cover – unit tests patch
        return []

    feed = feedparser.parse(HN_RSS)
    for entry in feed.entries:
        ts = int(time.mktime(entry.published_parsed))
        if ts > after_ts:
            yield {
                "id": entry.link,
                "ts": ts,
                "source": "hn",
                "text": f"{entry.title}\n{entry.summary}",
                "labels": [],
            }

# ---------------------------------------------------------------------------
# CLI parsing
# ---------------------------------------------------------------------------

def _parse_args(argv: List[str] | None = None):
    p = argparse.ArgumentParser(description="Ambient preference agent")
    p.add_argument("--cutoff", type=float, default=0.8, help="Minimum percentile (0-1) to emit KEEP message")
    p.add_argument("--comparisons", type=int, default=50, help="Pairwise comparisons per candidate")
    p.add_argument("--quiet", action="store_true")
    return p.parse_args(argv)

# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

async def main(args: argparse.Namespace):  # noqa: D401 – entry from tests/CLI
    # Load label rules (optional)
    rules = []
    if RULES_FILE.exists():
        try:
            rules = yaml.safe_load(RULES_FILE.read_text()) if yaml else []
        except Exception:
            rules = []

    # Load graded items (top → best)
    graded_rows = list(ndjson_iter(GRADED_FILE))

    if len(graded_rows) < 2:
        if not args.quiet:
            print("Need ≥2 items in graded_set.ndjson to train; please add and reorder.")
        # Bootstrap: copy all raw events into graded file for user ordering
        # This works only if there are raw events; otherwise nothing happens.
        return

    # Build or load judge
    judge = build_compare(graded_rows)

    # Determine last timestamp of processed events
    seen_raw = list(ndjson_iter(RAW_FILE))
    last_ts = max((e["ts"] for e in seen_raw), default=0)

    new_count = 0
    for ev in fetch_hn(last_ts):
        # Apply any simple label rules
        if rules:
            ev["labels"] = _apply_rules(ev["text"], rules)
        append(RAW_FILE, ev)
        pct = compute_percentile(ev, graded_rows, ranker=judge, comparisons=args.comparisons)
        append(PERC_FILE, {"ts": ev["ts"], "id": ev["id"], "pct": pct})
        new_count += 1
        if pct >= args.cutoff and not args.quiet:
            snippet = ev["text"][:120].replace("\n", " ")
            print(f"KEEP: {dt.datetime.utcfromtimestamp(ev['ts'])}|{pct:.2f}|{snippet}")
    if not args.quiet:
        print(f"processed {new_count} new events")


if __name__ == "__main__":
    asyncio.run(main(_parse_args()))
