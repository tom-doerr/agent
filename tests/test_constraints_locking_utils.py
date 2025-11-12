from __future__ import annotations

from multiprocessing import Process
from pathlib import Path
from datetime import datetime

from webapp.nlco_htmx import utils


def _worker(path: str, prefix: str, n: int) -> None:
    p = Path(path)
    now = datetime(2025, 11, 12, 10, 0, 0)
    for i in range(n):
        utils.write_constraints_entry(p, f"{prefix}-{i}", now=now)


def test_constraints_locking_prevents_race(tmp_path: Path) -> None:
    path = tmp_path / "constraints.md"
    n = 50
    p1 = Process(target=_worker, args=(str(path), "p1", n))
    p2 = Process(target=_worker, args=(str(path), "p2", n))
    p1.start(); p2.start(); p1.join(); p2.join()

    text = path.read_text(encoding="utf-8")
    # One heading for the fixed date
    assert text.count("# 2025-11-12\n") == 1
    # All entries present
    for i in range(n):
        assert f"p1-{i}" in text
        assert f"p2-{i}" in text

