#!/usr/bin/env python3
"""Pair-wise ranking helper for the ambient agent pipeline.

Goal: learn a ranker that, given two event texts, selects which one is more
useful for you.  The training data is a strictly ordered file
`ranking_set.ndjson`; the **row order encodes usefulness** (top = best).

Usage (CLI)::

    python3 ranking_agent.py --train                # (re)train ranker
    python3 ranking_agent.py --eval decisions.ndjson --percentile 90 \
                             --comparisons 25 --output top.ndjson

Flags
-----
--train            Only train the ranker and exit.
--eval  PATH       Evaluate candidates from PATH (default: decisions.ndjson).
--percentile PCT   Keep items whose empirical percentile >= PCT (default 90).
--comparisons N    Comparisons per candidate (default 25).
--output PATH      Where to store kept candidates.

Internals are kept minimal for easy unit testing – see tests/test_ranking_agent.py
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from utils.io import ndjson_iter, append_ndjson as append
from utils.models import ModelManager, build_or_load_model

try:
    import dspy  # heavy import – mocked in tests
except ModuleNotFoundError:  # pragma: no cover – replaced by stub in tests
    dspy = None  # type: ignore

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
RANKING_FILE = Path("ranking_set.ndjson")
MODEL_PATH = Path("models/ranker_latest.pkl")

# ---------------------------------------------------------------------------
# Training data utilities
# ---------------------------------------------------------------------------

def _load_ranking() -> List[Dict[str, Any]]:
    return list(ndjson_iter(RANKING_FILE))


def _prepare_pairs(rows: List[Dict[str, Any]]):  # noqa: D401 – simple helper
    """Return **all** text pairs (i<j) as DSPy Examples; earlier row is better.

    The ranking file is ordered best→worst, therefore row *i* should beat any
    row *j* where j>i.  We create one example per unordered pair and shuffle
    the resulting list so that the optimiser sees a mixed dataset.
    """
    if dspy is None:  # pragma: no cover
        return []

    class RankSig(dspy.Signature):  # type: ignore
        text_a: str = dspy.InputField()
        text_b: str = dspy.InputField()
        better: str = dspy.OutputField(desc="a|b")

    pairs = []
    n = len(rows)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = rows[i], rows[j]
            pairs.append(
                dspy.Example(text_a=a["text"], text_b=b["text"], better="a").with_inputs("text_a", "text_b")
            )
    random.shuffle(pairs)  # mix order
    return RankSig, pairs

# ---------------------------------------------------------------------------
# Ranker – build / load (mirror build_judge style)
# ---------------------------------------------------------------------------

def build_ranker(force_retrain: bool = False):  # noqa: D401 – simple
    if dspy is None:  # pragma: no cover
        raise RuntimeError("dspy unavailable – cannot build ranker")

    if MODEL_PATH.exists() and not force_retrain:
        try:
            return dspy.Module.load(MODEL_PATH)
        except Exception:
            print("warning: failed to load existing ranker – retraining")

    # Ensure LM is configured for this process – DeepSeek Reasoner supports structured outputs
    dspy.configure(
        lm=dspy.LM(
            "deepseek/deepseek-chat-v3",
            max_tokens=4000,
            temperature=0.7,
        )
    )

    rows = _load_ranking()
    Sig, train_pairs = _prepare_pairs(rows)

    base = dspy.Predict(Sig)  # type: ignore[attr-defined]

    # Skip training if less than 2 rows
    if len(train_pairs) < 1:
        print("not enough ranking data to train – using zero-shot model")
        ranker = base
    else:
        RS = getattr(dspy.teleprompt, "BootstrapFewShotWithRandomSearch", None)
        if RS is None:
            RS = getattr(dspy.teleprompt, "BootstrapFewShot", None)
        if RS is None:
            ranker = base
        else:
            try:
                ranker = RS(metric=None, max_bootstrapped_demos=2).compile(base, trainset=train_pairs, num_threads=8)
            except Exception as exc:
                print(f"ranker optimisation failed: {exc} – falling back to zero-shot model")
                ranker = base

    MODEL_PATH.parent.mkdir(exist_ok=True)
    ts = int(time.time())
    save_path = MODEL_PATH.with_name(f"ranker_{ts}.pkl")
    ranker.save(save_path)
    try:
        if MODEL_PATH.exists() or MODEL_PATH.is_symlink():
            MODEL_PATH.unlink()
        MODEL_PATH.symlink_to(save_path)
    except OSError:
        append = False  # ignore – copy fallback not crucial here
    return ranker

# ---------------------------------------------------------------------------
# Evaluation utilities
# ---------------------------------------------------------------------------

def _win(candidate_text: str, ref_text: str, ranker) -> bool:
    """Return True if *candidate* wins (model says better == 'a')."""
    res = ranker(text_a=candidate_text, text_b=ref_text)
    return res.better == "a"


def compute_percentile(candidate: Dict[str, Any], ranking_rows: List[Dict[str, Any]], *, ranker, comparisons: int = 25) -> float:
    wins = 0
    for _ in range(comparisons):
        ref = random.choice(ranking_rows)
        if _win(candidate["text"], ref["text"], ranker):
            wins += 1
    return 100.0 * wins / comparisons if comparisons else 0.0


def compute_accuracy(ranking_rows: List[Dict[str, Any]], *, ranker) -> float:
    correct = 0
    total = 0
    for i in range(len(ranking_rows)):
        for j in range(i + 1, len(ranking_rows)):
            if _win(ranking_rows[i]["text"], ranking_rows[j]["text"], ranker):
                correct += 1
            total += 1
    return correct / total if total else 0.0


def compute_top_k_accuracy(ranking_rows: List[Dict[str, Any]], k: int, *, ranker) -> float:
    correct = 0
    total = 0
    for i in range(len(ranking_rows)):
        top_k = sorted(ranking_rows, key=lambda x: _win(x["text"], ranking_rows[i]["text"], ranker), reverse=True)[:k]
        if ranking_rows[i] in top_k:
            correct += 1
        total += 1
    return correct / total if total else 0.0


# ---------------------------------------------------------------------------
# CLI entry
# ---------------------------------------------------------------------------

def _parse_args(argv: List[str] | None = None):
    p = argparse.ArgumentParser(description="Pair-wise ranking agent")
    subparsers = p.add_subparsers(dest="command", required=True)

    train_parser = subparsers.add_parser("train", help="Train the ranker")
    train_parser.add_argument("--force", action="store_true", help="Force retrain ranker")

    infer_parser = subparsers.add_parser("infer", help="Run inference")
    infer_parser.add_argument("--eval", metavar="PATH", type=Path, default=Path("decisions.ndjson"), help="Candidates file (default decisions.ndjson)")
    infer_parser.add_argument("--percentile", type=float, default=90, help="Percentile cutoff")
    infer_parser.add_argument("--comparisons", type=int, default=25, help="Comparisons per candidate")
    infer_parser.add_argument("--output", type=Path, default=Path("ranked_output.ndjson"), help="Where to write kept candidates")

    evaluate_parser = subparsers.add_parser("evaluate", help="Evaluate ranker accuracy")
    evaluate_parser.add_argument("--top_k", type=int, default=1, help="Top k accuracy")

    return p.parse_args(argv)


def main(argv: List[str] | None = None):  # noqa: D401 – simple
    args = _parse_args(argv)

    if args.command == "train":
        build_ranker(force_retrain=args.force)
    elif args.command == "infer":
        ranking_rows = _load_ranking()
        if not ranking_rows:
            print(f"{RANKING_FILE} missing or empty – cannot run inference")
            return

        ranker = build_ranker(False)

        kept = 0
        for row in ndjson_iter(args.eval):
            pct = compute_percentile(row, ranking_rows, ranker=ranker, comparisons=args.comparisons)
            row["percentile"] = pct
            if pct >= args.percentile:
                append(args.output, row)
                kept += 1
            print(json.dumps({"id": row.get("id"), "pct": pct}, ensure_ascii=False))

        print(f"kept {kept} rows >= {args.percentile}th pct into {args.output}")
    elif args.command == "evaluate":
        ranking_rows = _load_ranking()
        if not ranking_rows:
            print(f"{RANKING_FILE} missing or empty – cannot evaluate accuracy")
            return

        ranker = build_ranker(False)

        accuracy = compute_accuracy(ranking_rows, ranker=ranker)
        print(f"Accuracy: {accuracy:.4f}")

        top_k_accuracy = compute_top_k_accuracy(ranking_rows, args.top_k, ranker=ranker)
        print(f"Top {args.top_k} accuracy: {top_k_accuracy:.4f}")


if __name__ == "__main__":
    main()
