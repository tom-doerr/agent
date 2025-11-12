import os
from pathlib import Path
import pytest

import timestamp_app_core as core


@pytest.mark.asyncio
async def test_constraints_tail_default_shows_all_when_small(monkeypatch, tmp_path: Path):
    # Create a small constraints file (10 lines); default tail=200 should not trim
    constraints = tmp_path / "constraints.md"
    constraints.write_text("\n".join(f"L{i}" for i in range(1, 11)))

    app = core.TimestampLogApp(
        artifact_path=tmp_path / "artifact.md",
        constraints_path=constraints,
    )

    monkeypatch.delenv("TIMESTAMP_CONSTRAINTS_TAIL", raising=False)

    # Force a tall pane: height 20 -> tail 18, so all 10 lines visible
    captured = {"text": ""}

    class DummySize:
        def __init__(self, h: int) -> None:
            self.height = h

    class DummyMd:
        def __init__(self):
            self.size = DummySize(20)
        def update(self, text: str):
            captured["text"] = text

    class DummyTitle:
        def update(self, text: str):
            pass

    app._constraints_view = DummyMd()
    app._constraints_title = DummyTitle()
    app._load_constraints()
    out = captured["text"]
    assert "L1" in out and "L10" in out
