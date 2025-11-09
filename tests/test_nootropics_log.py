from pathlib import Path
from datetime import datetime, timedelta
import os

from nootropics_log import load_recent_nootropics_lines


def test_load_recent_nootropics_lines_filters_by_72h(tmp_path: Path, monkeypatch):
    path = tmp_path / "noo.jsonl"
    now = datetime.now()
    old = now - timedelta(hours=80)
    recent1 = now - timedelta(hours=2)
    recent2 = now - timedelta(hours=10)
    content = "\n".join(
        [
            {"ts": old.isoformat(), "item": "old"}.__repr__().replace("'", '"'),
            {"ts": recent1.isoformat(), "item": "r1"}.__repr__().replace("'", '"'),
            {"ts": recent2.isoformat(), "item": "r2"}.__repr__().replace("'", '"'),
        ]
    )
    path.write_text(content)

    monkeypatch.setenv("NLCO_NOOTROPICS_LOG", str(path))

    before = path.read_text()
    lines = load_recent_nootropics_lines(hours=72, limit=10)
    after = path.read_text()

    # No writes/changes
    assert before == after

    # Only 2 recent entries
    assert len(lines) == 2
    assert '"item": "r1"' in lines[-2] or '"item": "r1"' in lines[-1]
    assert '"item": "r2"' in lines[-2] or '"item": "r2"' in lines[-1]


def test_load_recent_limit(tmp_path: Path, monkeypatch):
    path = tmp_path / "noo.jsonl"
    now = datetime.now()
    items = []
    for i in range(5):
        items.append({"ts": (now - timedelta(hours=1+i)).isoformat(), "i": i})
    text = "\n".join([repr(x).replace("'", '"') for x in items])
    path.write_text(text)
    monkeypatch.setenv("NLCO_NOOTROPICS_LOG", str(path))
    lines = load_recent_nootropics_lines(hours=72, limit=2)
    assert len(lines) == 2
