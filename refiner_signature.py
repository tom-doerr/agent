"""Shared DSPy signature and helpers for schedule utilities and the refiner signature."""
from __future__ import annotations

import json
from datetime import datetime, date
from typing import Any, Iterable, List, Sequence

import dspy
from pydantic import BaseModel, Field, field_validator


class ArtifactEdit(BaseModel):
    """A single-line search/replace edit for the artifact."""
    search: str = Field(description="Single line to find (empty to append)")
    replace: str = Field(description="Replacement text (can be multi-line)")

    @field_validator("search")
    @classmethod
    def must_be_single_line(cls, v: str) -> str:
        if v and "\n" in v:
            raise ValueError("search must be a single line")
        return v


class ScheduleBlock(BaseModel):
    """Single block in the user's schedule."""

    start_time: str = Field(..., description="Start timestamp for the scheduled activity (e.g., '2025-10-07 18:30').")
    end_time: str = Field(..., description="End timestamp for the scheduled activity (same format as start_time).")
    description: str = Field(..., description="Concise description of the activity in this block.")


class SystemState(BaseModel):
    """Minimal system state passed to the refiner.

    For now it contains only the last time the artifact was changed, as an ISO timestamp.
    """

    last_artifact_update: str = Field(
        ..., description="ISO timestamp of the last artifact modification (previous write)."
    )


class RefineSignature(dspy.Signature):
    """Refine artifact via single-line search/replace edits. Use empty search to append."""

    constraints: str = dspy.InputField(desc="Active constraints influencing the artifact.")
    system_state: SystemState = dspy.InputField(desc="Minimal system state.")
    artifact: str = dspy.InputField(desc="Current artifact to refine.")
    context: str = dspy.InputField(desc="Ambient context (dates, telemetry, etc.).")
    edits: List[ArtifactEdit] = dspy.OutputField(desc="List of single-line edits.")
    summary: str = dspy.OutputField(desc="One sentence summary of changes.")


def normalize_schedule(data: Any) -> list[ScheduleBlock]:
    """Coerce arbitrary refiner output into validated schedule blocks."""
    if data is None or data == "":
        return []

    if isinstance(data, str):
        try:
            parsed = json.loads(data)
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive
            raise ValueError(f"Structured schedule string was not valid JSON: {exc}") from exc
        data = parsed

    if not isinstance(data, Iterable) or isinstance(data, (bytes, str)):
        raise ValueError("Structured schedule must be an iterable of schedule entries.")

    blocks: list[ScheduleBlock] = []
    for entry in data:
        if isinstance(entry, ScheduleBlock):
            blocks.append(entry)
        elif isinstance(entry, BaseModel):
            blocks.append(ScheduleBlock.model_validate(entry.model_dump()))
        elif isinstance(entry, dict):
            blocks.append(ScheduleBlock.model_validate(entry))
        else:
            raise ValueError(f"Unsupported schedule entry type: {type(entry)!r}")
    return blocks


def schedule_to_json(blocks: Sequence[ScheduleBlock]) -> str:
    """Serialize validated schedule blocks to pretty-printed JSON."""
    payload = [block.model_dump() for block in blocks]
    return json.dumps(payload, indent=2)


def _parse_time_value(value: str) -> datetime | None:
    value = (value or "").strip()
    if not value:
        return None
    value = value.replace("T", " ").replace("t", " ")
    value = value.rstrip("Z")
    parts = value.split()
    date_part: str | None = None
    time_part: str | None = None
    if len(parts) == 2:
        date_part, time_part = parts
    else:
        time_part = parts[0]
    year, month, day = 1900, 1, 1
    if date_part:
        try:
            year, month, day = (int(piece) for piece in date_part.split("-"))
        except ValueError:
            return None
    if time_part is None or ":" not in time_part:
        return None
    time_components = time_part.split(":")
    try:
        hour = int(time_components[0])
        minute = int(time_components[1]) if len(time_components) > 1 else 0
    except ValueError:
        return None
    try:
        return datetime(year, month, day, hour, minute)
    except ValueError:
        return None


def render_schedule_timeline(blocks: Sequence[ScheduleBlock], width: int = 48) -> str:
    """Render a simple ASCII timeline for the structured schedule."""

    if not blocks:
        return "Timeline unavailable (no blocks)."

    parsed: list[tuple[datetime, datetime, str]] = []
    base_date: date | None = None

    for block in blocks:
        start_raw = _parse_time_value(block.start_time)
        end_raw = _parse_time_value(block.end_time)
        if start_raw is None or end_raw is None:
            continue
        if start_raw.year != 1900:
            base_date = start_raw.date()
        if end_raw.year != 1900:
            base_date = end_raw.date()
        parsed.append((start_raw, end_raw, block.description))

    if not parsed:
        return "Timeline unavailable (unable to parse times)."

    if base_date is None:
        base_date = datetime.now().date()

    normalized: list[tuple[datetime, datetime, str]] = []
    for start_raw, end_raw, desc in parsed:
        start = start_raw
        end = end_raw
        if start.year == 1900:
            start = datetime.combine(base_date, start_raw.time())
        if end.year == 1900:
            end = datetime.combine(base_date, end_raw.time())
        if end <= start:
            continue
        normalized.append((start, end, desc))

    if not normalized:
        return "Timeline unavailable (unable to normalize schedule times)."

    normalized.sort(key=lambda entry: entry[0])
    earliest = normalized[0][0]
    latest = max(entry[1] for entry in normalized)
    total_minutes = max(1, int((latest - earliest).total_seconds() // 60))
    width = max(10, width)

    axis = f"{earliest.strftime('%H:%M')} " + "─" * width + f" {latest.strftime('%H:%M')}"
    lines = ["Timeline", axis]

    for start, end, desc in normalized:
        offset_minutes = int((start - earliest).total_seconds() // 60)
        duration_minutes = int((end - start).total_seconds() // 60)
        offset_chars = min(width - 1, int(offset_minutes / total_minutes * width)) if total_minutes else 0
        span_chars = max(1, int(duration_minutes / total_minutes * width)) if total_minutes else 1
        if offset_chars + span_chars > width:
            span_chars = max(1, width - offset_chars)
        bar = " " * max(0, offset_chars) + "█" * span_chars
        label = desc.strip() or "(unnamed)"
        lines.append(f"{label[:20]:<20} {bar}")

    return "\n".join(lines)
