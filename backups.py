from __future__ import annotations

import os
from pathlib import Path
from datetime import datetime


def _backup_root() -> Path:
    return Path(os.getenv("NLCO_BACKUP_DIR", ".nlco/backups"))


def ensure_backups(src_path: Path, *, content: str, now: datetime | None = None) -> None:
    """Write hourly, daily, and weekly snapshots of ``content`` if missing.

    - Minimal: creates a single file per period boundary; no rotation.
    - Safe: if ``content`` is empty, does nothing.
    """
    if not content:
        return
    ts = now or datetime.now()
    root = _backup_root()
    stem = src_path.stem or "constraints"

    hourly = root / "hourly"
    daily = root / "daily"
    weekly = root / "weekly"
    for d in (hourly, daily, weekly):
        d.mkdir(parents=True, exist_ok=True)

    files: list[tuple[Path, str]] = []
    files.append((hourly / f"{stem}-{ts:%Y%m%d%H}.md", content))
    files.append((daily / f"{stem}-{ts:%Y%m%d}.md", content))
    iso_year, iso_week, _ = ts.isocalendar()
    files.append((weekly / f"{stem}-{iso_year}W{iso_week:02d}.md", content))

    for path, data in files:
        if not path.exists():
            path.write_text(data, encoding="utf-8")

