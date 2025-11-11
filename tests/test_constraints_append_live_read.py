from pathlib import Path
import pytest

import nlco_textual


@pytest.mark.asyncio
async def test_append_and_run_reads_from_file(monkeypatch, tmp_path: Path):
    constraints = tmp_path / "constraints.md"
    artifact = tmp_path / "artifact.md"
    memory = tmp_path / "memory.md"
    short_term = tmp_path / "short.md"
    schedule = tmp_path / "structured_schedule.json"

    monkeypatch.setattr(nlco_textual, "CONSTRAINTS_FILE", constraints)
    monkeypatch.setattr(nlco_textual, "ARTIFACT_FILE", artifact)
    monkeypatch.setattr(nlco_textual, "MEMORY_FILE", memory)
    monkeypatch.setattr(nlco_textual, "SHORT_TERM_PATH", short_term)
    monkeypatch.setattr(nlco_textual, "STRUCTURED_SCHEDULE_FILE", schedule)

    # Stub heavy deps
    def fake_setup(self):
        self._primary_lm = object()
        self._support_lm = object()

    def fake_config(self):
        self._mlflow_enabled = False

    monkeypatch.setattr(nlco_textual.NLCOTextualApp, "_setup_language_models", fake_setup)
    monkeypatch.setattr(nlco_textual.NLCOTextualApp, "_configure_mlflow", fake_config)
    monkeypatch.setattr(nlco_textual, "TimewarriorModule", lambda *a, **k: type("X", (), {"run": lambda self, **kw: "ok"})())
    monkeypatch.setattr(nlco_textual, "PlanningModule", lambda *a, **k: type("X", (), {"run": lambda self, **kw: "ok"})())
    monkeypatch.setattr(nlco_textual, "AffectModule", lambda *a, **k: type("X", (), {"run": lambda self, **kw: None})())
    monkeypatch.setattr(nlco_textual, "run_with_metrics", lambda *a, **k: type("Y", (), {"refined_artifact": "", "structured_schedule": []})())

    app = nlco_textual.NLCOTextualApp()
    async with app.run_test() as pilot:
        # Append twice; app should read file at run time
        app._handle_new_message("L1")
        app._handle_new_message("L2")
        await pilot.pause()
        # Sanity: file contains both lines
        text = constraints.read_text()
        assert "L1" in text and "L2" in text

        # Now run; worker receives the snapshot read from file
        captured = {}

        def spy_run_iteration(*, iteration_index: int, constraints_text: str):
            captured["constraints_text"] = constraints_text

        app._run_iteration = spy_run_iteration  # type: ignore
        app.action_run_iteration()
        for _ in range(50):
            if not app.is_running:
                break
            await pilot.pause()

        assert "L1" in captured.get("constraints_text", "")
        assert "L2" in captured.get("constraints_text", "")

