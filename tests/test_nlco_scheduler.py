from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nlco_scheduler import evaluate_run_decision


def test_run_when_mtime_changes():
    now = datetime(2025, 10, 6, 12, 0, 0)
    mtime = now.timestamp()
    decision = evaluate_run_decision(
        last_mtime=None,
        last_run_time=None,
        current_mtime=mtime,
        now=now,
        run_interval=timedelta(hours=1),
        stale_interval=timedelta(days=3),
    )
    assert decision.should_run
    assert decision.next_last_mtime == mtime
    assert decision.next_last_run_time == now
    assert not decision.is_stale_skip
    assert "Constraints changed" in (decision.message or "")


def test_run_on_hourly_schedule_when_not_stale():
    now = datetime(2025, 10, 6, 13, 0, 0)
    last_run = datetime(2025, 10, 6, 12, 0, 0)
    mtime = datetime(2025, 10, 6, 9, 0, 0).timestamp()
    decision = evaluate_run_decision(
        last_mtime=mtime,
        last_run_time=last_run,
        current_mtime=mtime,
        now=now,
        run_interval=timedelta(hours=1),
        stale_interval=timedelta(days=3),
    )
    assert decision.should_run
    assert decision.next_last_mtime == mtime
    assert decision.next_last_run_time == now
    assert "Running scheduled iteration" in (decision.message or "")


def test_skip_when_stale():
    now = datetime(2025, 10, 10, 12, 0, 0)
    stale_mtime = datetime(2025, 10, 6, 10, 0, 0).timestamp()
    last_run = datetime(2025, 10, 9, 12, 0, 0)
    decision = evaluate_run_decision(
        last_mtime=stale_mtime,
        last_run_time=last_run,
        current_mtime=stale_mtime,
        now=now,
        run_interval=timedelta(hours=1),
        stale_interval=timedelta(days=3),
    )
    assert not decision.should_run
    assert decision.is_stale_skip
    assert decision.next_last_run_time == now
    assert "Skipping scheduled iteration" in (decision.message or "")


def test_no_run_when_interval_not_elapsed():
    now = datetime(2025, 10, 6, 12, 30, 0)
    last_run = datetime(2025, 10, 6, 12, 0, 0)
    mtime = datetime(2025, 10, 6, 11, 0, 0).timestamp()
    decision = evaluate_run_decision(
        last_mtime=mtime,
        last_run_time=last_run,
        current_mtime=mtime,
        now=now,
        run_interval=timedelta(hours=1),
        stale_interval=timedelta(days=3),
    )
    assert not decision.should_run
    assert not decision.is_stale_skip
    assert decision.next_last_run_time == last_run
    assert decision.message is None
