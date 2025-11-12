from __future__ import annotations

import os
from pathlib import Path
from datetime import datetime

from constraints_io import append_line
from webapp.nlco_htmx import utils


def test_backups_created_on_append_line(tmp_path: Path, monkeypatch) -> None:
    backup_dir = tmp_path / "bk"
    monkeypatch.setenv("NLCO_BACKUP_DIR", str(backup_dir))
    cpath = tmp_path / "constraints.md"
    cpath.write_text("A\n", encoding="utf-8")
    append_line(cpath, "B")

    hourly = backup_dir / "hourly"
    daily = backup_dir / "daily"
    weekly = backup_dir / "weekly"
    assert hourly.exists() and daily.exists() and weekly.exists()
    # Exactly one file each on a clean run
    hfiles = list(hourly.glob("*.md"))
    dfiles = list(daily.glob("*.md"))
    wfiles = list(weekly.glob("*.md"))
    assert len(hfiles) == 1 and len(dfiles) == 1 and len(wfiles) == 1
    assert hfiles[0].read_text(encoding="utf-8").strip() == "A"


def test_backups_created_in_htmx_writer(tmp_path: Path, monkeypatch) -> None:
    backup_dir = tmp_path / "bk"
    monkeypatch.setenv("NLCO_BACKUP_DIR", str(backup_dir))
    cpath = tmp_path / "constraints.md"
    cpath.write_text("old\n", encoding="utf-8")
    fixed = datetime(2025, 11, 12, 15, 0, 0)
    utils.write_constraints_entry(cpath, "msg", now=fixed)

    # We don't know exact filenames without coupling to datetime; ensure one file exists in each bucket
    for sub in ("hourly", "daily", "weekly"):
        files = list((backup_dir / sub).glob("*.md"))
        assert len(files) == 1
        # content equals the pre-write content
        assert files[0].read_text(encoding="utf-8").strip() == "old"

