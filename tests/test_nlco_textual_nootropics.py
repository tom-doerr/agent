import pytest
from pathlib import Path

import nlco_textual


@pytest.mark.asyncio
async def test_nootropics_panel_renders(monkeypatch, tmp_path: Path):
    # Point app files to tmp so no real files are touched
    monkeypatch.setattr(nlco_textual, "CONSTRAINTS_FILE", tmp_path / "constraints.md")
    monkeypatch.setattr(nlco_textual, "ARTIFACT_FILE", tmp_path / "artifact.md")
    monkeypatch.setattr(nlco_textual, "MEMORY_FILE", tmp_path / "memory.md")
    monkeypatch.setattr(nlco_textual, "SHORT_TERM_PATH", tmp_path / "short_term.md")
    monkeypatch.setattr(nlco_textual, "STRUCTURED_SCHEDULE_FILE", tmp_path / "structured_schedule.json")

    # Make the heavy deps no-ops
    def fake_setup(self):
        self._primary_lm = object()
        self._support_lm = object()

    def fake_config(self):
        self._mlflow_enabled = False

    monkeypatch.setattr(nlco_textual.NLCOTextualApp, "_setup_language_models", fake_setup)
    monkeypatch.setattr(nlco_textual.NLCOTextualApp, "_configure_mlflow", fake_config)

    # Stub nootropics loader
    monkeypatch.setattr(nlco_textual, "load_recent_nootropics_lines", lambda: ['{"ts":"2025-11-06 12:00:00","note":"alpha"}'])

    app = nlco_textual.NLCOTextualApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        widget = app.query_one("#nootropics-log", nlco_textual.Log)
        text = "\n".join(str(line) for line in widget.lines)
        assert "alpha" in text
