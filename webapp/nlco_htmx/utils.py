"""Utilities for the HTMX web interface."""

from __future__ import annotations

from datetime import date, datetime
import re
from pathlib import Path
from typing import Iterable, Optional

from refiner_signature import ScheduleBlock, normalize_schedule

DATE_HEADING_RE = re.compile(r"^#\s*(\d{4}-\d{2}-\d{2})$")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def write_constraints_entry(path: Path, message: str, *, now: datetime | None = None) -> tuple[str, date]:
    """Append ``message`` to ``constraints.md`` with date heading.

    Returns the formatted line and the entry date.
    """

    now = now or datetime.now()
    message = message.strip()
    if not message:
        raise ValueError("message must not be empty")

    formatted_line = f"{now.strftime('%H%M')} {message}"
    entry_date = now.date()

    path.parent.mkdir(parents=True, exist_ok=True)
    existing = read_text(path)
    last_date = extract_last_constraints_date(existing)

    pieces: list[str] = []
    if existing and not existing.endswith("\n"):
        pieces.append("\n")
    if last_date != entry_date:
        if existing and not existing.endswith("\n\n"):
            pieces.append("\n")
        pieces.append(f"# {entry_date:%Y-%m-%d}\n")
    pieces.append(f"{formatted_line}\n")

    with path.open("a", encoding="utf-8") as handle:
        handle.write("".join(pieces))

    return formatted_line, entry_date


def extract_last_constraints_date(content: str) -> Optional[date]:
    for line in reversed(content.splitlines()):
        match = DATE_HEADING_RE.match(line.strip())
        if match:
            try:
                return datetime.strptime(match.group(1), "%Y-%m-%d").date()
            except ValueError:
                continue
    return None


def load_constraints_history(path: Path, limit: int = 200) -> list[tuple[str, list[str]]]:
    """Return most recent constraint entries grouped by date heading.

    ``limit`` counts individual lines excluding headings.
    """

    content = read_text(path)
    lines = [line for line in content.splitlines() if line.strip()]
    history: list[tuple[str, list[str]]] = []
    current_date: Optional[str] = None
    current_lines: list[str] = []

    for line in lines:
        match = DATE_HEADING_RE.match(line)
        if match:
            if current_date is not None and current_lines:
                history.append((current_date, current_lines))
            current_date = match.group(1)
            current_lines = []
        else:
            if current_date is None:
                current_date = date.today().strftime("%Y-%m-%d")
            current_lines.append(line)

    if current_date is not None and current_lines:
        history.append((current_date, current_lines))

    # Keep only most recent entries according to ``limit``
    trimmed: list[tuple[str, list[str]]] = []
    remaining = limit
    for date_str, entries in reversed(history):
        if remaining <= 0:
            break
        take = entries[-remaining:]
        trimmed.append((date_str, take))
        remaining -= len(take)
    trimmed.reverse()
    return trimmed


def load_text_and_mtime(path: Path) -> tuple[str, Optional[datetime]]:
    """Read file and return content plus modification time."""

    try:
        stat = path.stat()
    except FileNotFoundError:
        return "(not found)", None

    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:  # pragma: no cover - defensive guard
        return f"(error reading file: {exc})", None
    return text, datetime.fromtimestamp(stat.st_mtime)


def format_timedelta(reference: datetime, past: Optional[datetime]) -> str:
    if past is None:
        return "never"
    delta = reference - past
    total = int(delta.total_seconds())
    if total < 0:
        total = 0
    if total < 60:
        return f"{total}s ago"
    if total < 3600:
        minutes, seconds = divmod(total, 60)
        return f"{minutes}m {seconds}s ago"
    hours, remainder = divmod(total, 3600)
    minutes = remainder // 60
    return f"{hours}h {minutes}m ago"


def load_schedule_snapshot(path: Path) -> tuple[list[ScheduleBlock], Optional[datetime], Optional[str]]:
    """Load structured schedule blocks along with mtime and optional error."""

    try:
        stat = path.stat()
    except FileNotFoundError:
        return [], None, None

    try:
        raw = path.read_text(encoding="utf-8").strip()
    except Exception as exc:  # pragma: no cover - defensive guard
        return [], datetime.fromtimestamp(stat.st_mtime), f"Error reading schedule: {exc}"

    if not raw:
        return [], datetime.fromtimestamp(stat.st_mtime), None

    try:
        blocks = normalize_schedule(raw)
    except ValueError as exc:
        return [], datetime.fromtimestamp(stat.st_mtime), f"Unable to parse schedule: {exc}"

    return blocks, datetime.fromtimestamp(stat.st_mtime), None
