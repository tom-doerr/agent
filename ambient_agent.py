"""Minimal self-contained ambient agent that ingests Hacker-News front-page RSS,
labels events via simple keyword rules, judges them with a DSPy program and
stores everything in NDJSON/text files.  No database, OAuth or external state
required.  The script is written to be *idempotent*: only items newer than the
latest timestamp previously seen are processed in each run.

The script is intentionally kept in a single file so that it can be triggered 
from cron, executed locally, copied around and read in minutes.

Run once-off:
    python ambient_agent.py

Cron every 15 minutes (example):
    */15 * * * * /usr/bin/python /path/to/ambient_agent.py
"""
from __future__ import annotations
import asyncio
import datetime as dt
import json
import time
import calendar
import shutil  
from pathlib import Path
from typing import Any, Dict, Iterable, List

import feedparser  # type: ignore
from utils.io import ndjson_iter, append_ndjson as append


try:
    import dspy  # heavy import, but fine for runtime execution
except ModuleNotFoundError:  # pragma: no cover – tests monkey-patch a stub
    dspy = None  # type: ignore

# ---------------------------------------------------------------------------
# Paths (relative to working directory)
# ---------------------------------------------------------------------------
RAW_FILE = Path("raw_events.ndjson")      # all seen events (append-only)
TRUTH_FILE = Path("truth_set.ndjson")     # your thumbs-up / thumbs-down labels

NOTIFY_FILE = Path("notify.log")          # what was pinged to you
DECISIONS_FILE = Path("decisions.ndjson")  # model decisions (all events)

HN_RSS = "https://hnrss.org/frontpage"     # source – no auth required

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ts_now() -> int:  # Unix timestamp shortcut
    return int(time.time())

# ---------------------------------------------------------------------------
# File helpers – ensure config files exist
# ---------------------------------------------------------------------------

def _ensure_config_files() -> None:
    """Touch required NDJSON/text files if they don't exist."""
    for p in (RAW_FILE, TRUTH_FILE, NOTIFY_FILE, DECISIONS_FILE):
        if not p.exists():
            p.touch()

# ---------------------------------------------------------------------------
# DSPy judge
# ---------------------------------------------------------------------------

MODEL_ID = "openrouter/google/gemini-2.5-flash-lite-preview-06-17"  # Gemini 2.5 Flash-Lite

if dspy is not None:

    class JudgeSig(dspy.Signature):
        text: str = dspy.InputField()
        helpful: str = dspy.OutputField(desc="yes|no")
        nugget: str = dspy.OutputField()


    def load_truth():
        """Return user-provided truth rows (can be empty)."""
        return list(ndjson_iter(TRUTH_FILE))


    def build_judge():
        """Load saved judge if available, else train fresh and return."""
        from pathlib import Path

        saved_path = Path("models/judge_flash_v1.pkl")  # default path
        # Ensure DSPy uses Flash 2.5 Lite
        dspy.configure(lm=dspy.LM(MODEL_ID, max_tokens=4000, temperature=0.7))

        if saved_path.exists():
            try:
                return dspy.Module.load(saved_path)
            except Exception:
                print("Warning: failed to load saved judge – rebuilding…")

        ReActCls = getattr(dspy, "ReAct", None)
        if ReActCls is not None:
            try:
                base = ReActCls(JudgeSig, tools=[])
            except TypeError:
                base = dspy.Predict(JudgeSig)
        else:
            # DSPy version without ReAct – use simple Predict wrapper
            base = dspy.Predict(JudgeSig)
        truth = load_truth()
        if truth:
            def _try_compile(trainer_cls, **kwargs):  # type: ignore
                try:
                    trainer = trainer_cls(**kwargs)
                    try:
                        # Older API variant
                        return trainer.compile(base, trainset=truth)
                    except TypeError:
                        # Newer API signature
                        return trainer.compile(base, trainset=truth, valset=None)
                except Exception:
                    return None
            judge_prog = None
        else:
            judge_prog = base
            _try_compile = None  # type: ignore
        # Prefer RandomSearch optimizer if available
        teleprompt = getattr(dspy, "teleprompt", None)
        if truth and teleprompt is not None and _try_compile is not None:
            RS = getattr(teleprompt, "BootstrapFewShotWithRandomSearch", None)
            if RS is not None:
                judge_prog = _try_compile(RS)
        if truth and judge_prog is None and _try_compile is not None:
            BS = getattr(dspy, "BootstrapFewShot", None)
            if BS is not None:
                judge_prog = _try_compile(BS)
        # Fallback: no optimisation, just base
        if judge_prog is None:
            judge_prog = base

        ts = int(time.time())
        versioned = saved_path.with_name(f"judge_flash_{ts}.pkl")
        versioned.parent.mkdir(exist_ok=True)
        judge_prog.save(versioned)
        # Point saved_path to latest model file
        try:
            if saved_path.exists() or saved_path.is_symlink():
                saved_path.unlink()
            saved_path.symlink_to(versioned)
        except OSError:
            # Fall-back where symlinks are unsupported
            shutil.copyfile(versioned, saved_path)
        return judge_prog

else:  # pragma: no cover – makes the script importable without dspy

    def build_judge():  # type: ignore[return-value]
        raise RuntimeError("dspy is not available – cannot build judge")

# ---------------------------------------------------------------------------
# Source – Hacker News
# ---------------------------------------------------------------------------

def fetch_hn(after_ts: int) -> Iterable[Dict[str, Any]]:
    """Yield events newer than *after_ts* from Hacker-News front-page RSS."""
    feed = feedparser.parse(HN_RSS)
    for entry in feed.entries:
        published = int(calendar.timegm(entry.published_parsed))
        if published > after_ts:
            yield {
                "id": entry.link,
                "ts": published,
                "source": "hn",
                "text": f"{entry.title}\n{entry.summary}",
                "labels": [],
            }

# ---------------------------------------------------------------------------
# Main loop (can be executed by cron)
# ---------------------------------------------------------------------------

async def main(force: bool = False, verbose: bool = True) -> None:  # pragma: no cover – executed manually/cron
    seen = list(ndjson_iter(RAW_FILE))
    last_ts = 0 if force else max((e["ts"] for e in seen), default=0)

    if verbose:
        print(f"[ambient-agent] previously seen: {len(seen)} events, last_ts={last_ts}")

    _ensure_config_files()
    judge = build_judge()

    new_events: List[Dict[str, Any]] = []
    for ev in fetch_hn(last_ts):
        append(RAW_FILE, ev)
        new_events.append(ev)

    if verbose:
        print(f"[ambient-agent] fetched {len(new_events)} new events")

    for ev in new_events:
        res = judge(text=ev["text"])
        if verbose:
            print(f"[ambient-agent] judge -> helpful={res.helpful}")
        # log decision for every event
        decision = {
            **ev,
            "helpful": res.helpful,
            "nugget": getattr(res, "nugget", ""),
        }
        append(DECISIONS_FILE, decision)

        if res.helpful == "yes":
            msg = f"{dt.datetime.utcfromtimestamp(ev['ts'])} | {decision['nugget']}"
            print("PING:", msg)
            append(NOTIFY_FILE, {"ts": ts_now(), "msg": msg})


if __name__ == "__main__":
    import argparse, sys
    p = argparse.ArgumentParser(description="Run ambient agent")
    p.add_argument("--force", action="store_true", help="Ignore last timestamp and process all RSS items")
    p.add_argument("-q", "--quiet", action="store_true", help="Suppress verbose output")
    ns = p.parse_args()
    try:
        asyncio.run(main(force=ns.force, verbose=not ns.quiet))
    except KeyboardInterrupt:
        sys.exit(1)
