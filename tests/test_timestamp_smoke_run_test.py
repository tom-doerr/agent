from pathlib import Path
import pytest

import timestamp_app_core as core
import timestamp_textual_app as wrap
from textual.widgets import Markdown, Static


@pytest.mark.asyncio
async def test_core_app_smoke_run_test(tmp_path: Path):
    a = tmp_path / "artifact.md"
    a.write_text("Line A\nLine B", encoding="utf-8")
    c = tmp_path / "constraints.md"
    c.write_text("# 2025-11-12\n1200 hello\n", encoding="utf-8")

    app = core.TimestampLogApp(artifact_path=a, constraints_path=c)
    async with app.run_test() as pilot:
        await pilot.pause()
        art_view = app.query_one("#artifact-view", Markdown)
        cons_view = app.query_one("#constraints-view", Markdown)
        assert isinstance(art_view, Markdown) and isinstance(cons_view, Markdown)
        # Core sets a short status after initial load
        assert isinstance(app.query_one("#artifact-status", Static), Static)
        assert "Artifact" in app._artifact_status_message


@pytest.mark.asyncio
async def test_wrapper_app_smoke_run_test(tmp_path: Path):
    a = tmp_path / "artifact.md"
    a.write_text("Hello\nWorld", encoding="utf-8")
    c = tmp_path / "constraints.md"
    c.write_text("# 2025-11-12\n1201 hi\n", encoding="utf-8")

    app = wrap.TimestampLogApp(artifact_path=a, constraints_path=c)
    async with app.run_test() as pilot:
        await pilot.pause()
        art_view = app.query_one("#artifact-view", Markdown)
        cons_view = app.query_one("#constraints-view", Markdown)
        help_panel = app.query_one("#help-panel", Static)
        assert isinstance(art_view, Markdown) and isinstance(cons_view, Markdown)
        assert help_panel.visible
        assert app._artifact_status_message.startswith("Artifact")

