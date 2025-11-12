import os
from pathlib import Path
import pytest

import timestamp_app_core as core


@pytest.mark.asyncio
async def test_constraints_tail_displayed(monkeypatch, tmp_path: Path):
    # Write 50 lines, expect last 3 shown
    constraints = tmp_path / "constraints.md"
    constraints.write_text("\n".join(f"L{i}" for i in range(1, 51)))

    app = core.TimestampLogApp(
        artifact_path=tmp_path / "artifact.md",
        constraints_path=constraints,
    )

    # Stub a small pane height so tail=3 (height 5 -> 3)
    captured = {"text": ""}

    class DummySize:
        def __init__(self, h: int) -> None:
            self.height = h

    class DummyMd:
        def __init__(self):
            self.size = DummySize(5)
        def update(self, text: str):
            captured["text"] = text

    class DummyTitle:
        def update(self, text: str):
            pass

    app._constraints_view = DummyMd()
    app._constraints_title = DummyTitle()

    app._load_constraints()
    rendered = captured["text"]
    assert "L48" in rendered and "L49" in rendered and "L50" in rendered
    assert "L1" not in rendered


@pytest.mark.asyncio
async def test_constraints_scrolls_to_end_on_reload(monkeypatch, tmp_path: Path):
    constraints = tmp_path / "constraints.md"
    constraints.write_text("A\nB\nC\n")

    app = core.TimestampLogApp(
        artifact_path=tmp_path / "artifact.md",
        constraints_path=constraints,
    )

    async with app.run_test() as pilot:
        await pilot.pause()
        view = app.query_one("#constraints-view", core.Markdown)
        called = {"n": 0}

        def _spy_scroll_end(*args, **kwargs):
            called["n"] += 1

        # Monkeypatch instance method to detect calls
        try:
            view.scroll_end = _spy_scroll_end  # type: ignore[attr-defined]
        except Exception:
            pytest.skip("Markdown widget lacks scroll_end in this Textual version")

        constraints.write_text("A\nB\nC\nD\nE\n")
        app._load_constraints()
        assert called["n"] >= 1
