"""Utility helpers for measuring LLM request usage in nlco workflows."""

from __future__ import annotations

import time
from typing import Any, Callable

import dspy


def run_with_metrics(
    name: str,
    func: Callable[..., Any],
    /,
    **kwargs: Any,
) -> Any:
    """Execute a callable while capturing latency, token counts, and billed cost."""
    start = time.perf_counter()
    with dspy.track_usage() as tracker:
        result = func(**kwargs)
    elapsed = time.perf_counter() - start

    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0
    models: set[str] = set()

    for model_name, usage_entries in tracker.usage_data.items():
        models.add(model_name)
        for entry in usage_entries:
            prompt_tokens += entry.get("prompt_tokens") or 0
            completion_tokens += entry.get("completion_tokens") or 0
            total_tokens += entry.get("total_tokens") or 0

    model_list = ", ".join(sorted(models)) if models else "<cached>"
    print(
        f"{name} | model: {model_list} | duration: {elapsed:.2f}s | "
        f"input tokens: {prompt_tokens} | output tokens: {completion_tokens} | "
        f"total tokens: {total_tokens}"
    )

    return result
