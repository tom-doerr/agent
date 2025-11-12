from __future__ import annotations

from pathlib import Path
import pytest

import timestamp_textual_app as wrap
from textual.containers import Vertical


@pytest.mark.asyncio
async def test_constraints_rows_env_controls_height_and_tail_wrapper(monkeypatch, tmp_path: Path):
    # Prepare 50 lines
    c = tmp_path / "constraints.md"
    c.write_text("\n".join(f"L{i:03d}" for i in range(1, 51)), encoding="utf-8")

    app = wrap.TimestampLogApp(constraints_path=c)
    monkeypatch.setenv("TIMESTAMP_CONSTRAINTS_ROWS", "12")  # rows -> tail = rows-2 = 10
    captured: dict[str, str] = {}

    async with app.run_test() as pilot:
        container = app.query_one("#constraints-container", Vertical)
        assert str(container.styles.height) == "12"

        view = app.query_one("#constraints-view", wrap.Markdown)
        def spy_update(text: str):
            captured["txt"] = text
        view.update = spy_update  # type: ignore[assignment]
        app._load_constraints()
        txt = captured.get("txt", "")
        # Expect last 10 lines visible (L041..L050) and L040 not present
        assert "L041" in txt and "L040" not in txt

