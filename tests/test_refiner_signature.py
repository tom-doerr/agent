from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from refiner_signature import ScheduleBlock, render_schedule_timeline


def test_render_schedule_timeline_basic() -> None:
    blocks = [
        ScheduleBlock(
            start_time="2025-10-07 18:30",
            end_time="2025-10-07 19:15",
            description="Dinner",
        ),
        ScheduleBlock(
            start_time="2025-10-07 19:30",
            end_time="2025-10-07 20:00",
            description="Study session",
        ),
    ]

    timeline = render_schedule_timeline(blocks)

    assert "Timeline" in timeline
    assert "Dinner" in timeline
    assert "Study session" in timeline
    assert "18:30" in timeline and "20:00" in timeline


def test_render_schedule_timeline_handles_unparseable_blocks() -> None:
    blocks = [
        ScheduleBlock(start_time="??", end_time="??", description="unknown"),
    ]
    timeline = render_schedule_timeline(blocks)
    assert "unable to parse" in timeline.lower()


def test_render_schedule_timeline_empty() -> None:
    timeline = render_schedule_timeline([])
    assert "no blocks" in timeline.lower()
