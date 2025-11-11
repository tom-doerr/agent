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

    async with app.run_test() as pilot:
        await pilot.pause()
        view = app.query_one("#constraints-view", core.Markdown)
        captured = {"text": ""}

        def _spy_update(text: str):
            captured["text"] = text

        view.update = _spy_update  # type: ignore[assignment]
        app._load_constraints()
        out = captured["text"]
        assert "L1" in out and "L10" in out

