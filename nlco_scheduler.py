"""Utility helpers for deciding when NLCO iterations should run."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class RunDecision:
    """Represents the scheduler's decision for the next loop iteration."""

    should_run: bool
    message: Optional[str]
    is_stale_skip: bool
    next_last_mtime: Optional[float]
    next_last_run_time: Optional[datetime]
    trigger: str = "none"  # "constraints", "scheduled", "stale_skip", or "none"


def evaluate_run_decision(
    *,
    last_mtime: Optional[float],
    last_run_time: Optional[datetime],
    current_mtime: float,
    now: datetime,
    run_interval: timedelta,
    stale_interval: timedelta,
) -> RunDecision:
    """Determine whether the loop should trigger a new iteration.

    Returns a :class:`RunDecision` describing whether to run, and any
    associated message. The decision also provides updated bookkeeping
    values for ``last_mtime`` and ``last_run_time`` when appropriate.
    """

    mtime_changed = last_mtime is None or current_mtime != last_mtime
    due_to_timer = last_run_time is None or (now - last_run_time) >= run_interval
    constraint_age = now - datetime.fromtimestamp(current_mtime)
    is_stale = constraint_age >= stale_interval

    if mtime_changed:
        message = (
            f"Constraints changed at {datetime.fromtimestamp(current_mtime)}. Running iterations…"
        )
        return RunDecision(
            should_run=True,
            message=message,
            is_stale_skip=False,
            next_last_mtime=current_mtime,
            next_last_run_time=now,
            trigger="constraints",
        )

    if not due_to_timer:
        return RunDecision(
            should_run=False,
            message=None,
            is_stale_skip=False,
            next_last_mtime=last_mtime,
            next_last_run_time=last_run_time,
            trigger="none",
        )

    if is_stale:
        stale_msg = (
            "No constraint changes for >= 3 days (last modified "
            f"{datetime.fromtimestamp(current_mtime)}). Skipping scheduled iteration."
        )
        return RunDecision(
            should_run=False,
            message=stale_msg,
            is_stale_skip=True,
            next_last_mtime=current_mtime,
            next_last_run_time=now,
            trigger="stale_skip",
        )

    scheduled_msg = (
        "No constraint changes detected since "
        f"{last_run_time.strftime('%Y-%m-%d %H:%M:%S') if last_run_time else 'startup'}. "
        f"Running scheduled iteration at {now.strftime('%Y-%m-%d %H:%M:%S')}…"
    )
    return RunDecision(
        should_run=True,
        message=scheduled_msg,
        is_stale_skip=False,
        next_last_mtime=current_mtime,
        next_last_run_time=now,
        trigger="scheduled",
    )


__all__ = ["RunDecision", "evaluate_run_decision"]
