from __future__ import annotations

from pathlib import Path

import timestamp_app_core as core


def test_constraints_tail_auto_uses_pane_height(monkeypatch, tmp_path: Path):
    # Prepare constraints with 100 lines
    c = tmp_path / "constraints.md"
    c.write_text("\n".join(f"L{i:03d}" for i in range(1, 101)), encoding="utf-8")

    app = core.TimestampLogApp(constraints_path=c)
    captured = {}

    class DummySize:
        def __init__(self, h: int) -> None:
            self.height = h

    class DummyMd:
        def __init__(self) -> None:
            self.size = DummySize(10)  # pretend 10 rows high
        def update(self, text: str):
            captured["text"] = text

    class DummyTitle:
        def update(self, text: str):
            captured["title"] = text

    app._constraints_view = DummyMd()
    app._constraints_title = DummyTitle()
    monkeypatch.setenv("TIMESTAMP_CONSTRAINTS_TAIL", "auto")

    app._load_constraints()
    txt = captured.get("text", "")
    # height=10 -> tail = max(10 - 2, 1) = 8 lines => expect L093..L100 present, L092 absent
    assert "L093" in txt and "L092" not in txt

