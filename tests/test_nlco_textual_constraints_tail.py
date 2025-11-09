from pathlib import Path
import pytest

import nlco_textual


@pytest.mark.asyncio
async def test_constraints_pane_shows_tail(monkeypatch, tmp_path: Path):
    constraints = tmp_path / "constraints.md"
    artifact = tmp_path / "artifact.md"
    memory = tmp_path / "memory.md"
    short_term = tmp_path / "short_term.md"
    schedule = tmp_path / "structured_schedule.json"

    # Create 50 lines; tail (40) should include lines 11..50
    constraints.write_text("\n".join(f"L{i}" for i in range(1, 51)))
    artifact.write_text("")
    memory.write_text("")

    monkeypatch.setattr(nlco_textual, "CONSTRAINTS_FILE", constraints)
    monkeypatch.setattr(nlco_textual, "ARTIFACT_FILE", artifact)
    monkeypatch.setattr(nlco_textual, "MEMORY_FILE", memory)
    monkeypatch.setattr(nlco_textual, "SHORT_TERM_PATH", short_term)
    monkeypatch.setattr(nlco_textual, "STRUCTURED_SCHEDULE_FILE", schedule)

    # Make heavy deps no-ops
    def fake_setup(self):
        self._primary_lm = object()
        self._support_lm = object()

    def fake_config(self):
        self._mlflow_enabled = False

    monkeypatch.setattr(nlco_textual.NLCOTextualApp, "_setup_language_models", fake_setup)
    monkeypatch.setattr(nlco_textual.NLCOTextualApp, "_configure_mlflow", fake_config)

    app = nlco_textual.NLCOTextualApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        log = app.query_one("#constraints-log", nlco_textual.Log)
        rendered = [str(line) for line in log.lines]
        txt = "".join(rendered)
        assert txt.startswith("L11")  # tail of 40 out of 50 starts at L11
        assert "L49" in txt
        assert "L50" in txt
