import os
from pathlib import Path
import pytest

import timestamp_app_core as core


@pytest.mark.asyncio
async def test_constraints_scroll_disabled(monkeypatch, tmp_path: Path):
    constraints = tmp_path / "constraints.md"
    constraints.write_text("A\nB\nC\n")

    app = core.TimestampLogApp(
        artifact_path=tmp_path / "artifact.md",
        constraints_path=constraints,
    )

    monkeypatch.setenv("TIMESTAMP_AUTO_SCROLL", "0")

    async with app.run_test() as pilot:
        await pilot.pause()
        view = app.query_one("#constraints-view", core.Markdown)
        called = {"n": 0}

        def _spy_scroll_end(*args, **kwargs):
            called["n"] += 1

        try:
            view.scroll_end = _spy_scroll_end  # type: ignore[attr-defined]
        except Exception:
            pytest.skip("Markdown widget lacks scroll_end in this Textual version")

        constraints.write_text("A\nB\nC\nD\nE\n")
        app._load_constraints()
        assert called["n"] == 0

