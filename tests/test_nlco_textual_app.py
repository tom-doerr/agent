"""Tests for the NLCO Textual interface."""

from __future__ import annotations

from types import SimpleNamespace, MethodType
from pathlib import Path
import sys

import pytest
from textual.widgets import TextArea

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import nlco_textual


@pytest.fixture
def app_factory(monkeypatch, tmp_path):
    """Create NLCOTextualApp instances with heavy dependencies stubbed out."""

    constraints_path = tmp_path / "constraints.md"
    artifact_path = tmp_path / "artifact.md"
    short_term_path = tmp_path / "short_term.md"
    memory_path = tmp_path / "memory.md"
    schedule_path = tmp_path / "structured_schedule.json"

    monkeypatch.setattr(nlco_textual, "CONSTRAINTS_FILE", constraints_path)
    monkeypatch.setattr(nlco_textual, "ARTIFACT_FILE", artifact_path)
    monkeypatch.setattr(nlco_textual, "SHORT_TERM_PATH", short_term_path)
    monkeypatch.setattr(nlco_textual, "MEMORY_FILE", memory_path)
    monkeypatch.setattr(nlco_textual, "STRUCTURED_SCHEDULE_FILE", schedule_path)

    def fake_setup(self) -> None:
        self._primary_lm = object()
        self._support_lm = object()

    def fake_config(self) -> None:
        self._mlflow_enabled = False

    monkeypatch.setattr(nlco_textual.NLCOTextualApp, "_setup_language_models", fake_setup)
    monkeypatch.setattr(nlco_textual.NLCOTextualApp, "_configure_mlflow", fake_config)

    def fake_run_worker(self, work, name="", group="default", description="", exit_on_error=True, start=True, exclusive=False, thread=False):
        try:
            work()
        except Exception as exc:  # pragma: no cover - test diagnostics
            worker = SimpleNamespace(error=exc)
            self._on_worker_error(worker)
        else:
            worker = SimpleNamespace(error=None)
            self._on_worker_finished(worker)
        return worker

    monkeypatch.setattr(nlco_textual.NLCOTextualApp, "run_worker", fake_run_worker, raising=False)

    class DummyTimeModule:
        def __init__(self, *args, **kwargs):  # noqa: D401 - test stub
            pass

        def run(self, **kwargs):  # noqa: D401 - test stub
            return "time ok"

    class DummyMemoryModule:
        def __init__(self, *args, **kwargs):  # noqa: D401 - test stub
            pass

        def run(self, **kwargs):  # noqa: D401 - test stub
            return "memory ok"

    class DummyPlanningModule:
        def __init__(self, *args, **kwargs):  # noqa: D401 - test stub
            pass

        def run(self, **kwargs):  # noqa: D401 - test stub
            return "plan ok"

    class DummyAffectModule:
        def __init__(self, *args, **kwargs):  # noqa: D401 - test stub
            pass

        def run(self, **kwargs):  # noqa: D401 - test stub
            return nlco_textual.AffectReport(
                emotions=["focused"],
                urgency="low",
                confidence="high",
                rationale="",
                suggested_focus="",
                goal_scores={"Keep schedule updated": 7},
            )

    monkeypatch.setattr(nlco_textual, "TimewarriorModule", DummyTimeModule)
    monkeypatch.setattr(nlco_textual, "MemoryModule", DummyMemoryModule)
    monkeypatch.setattr(nlco_textual, "PlanningModule", DummyPlanningModule)
    monkeypatch.setattr(nlco_textual, "AffectModule", DummyAffectModule)

    def factory(refined_text: str = "refined artifact", initial_artifact: str = "", initial_memory: str = ""):
        artifact_path.write_text(initial_artifact)
        memory_path.write_text(initial_memory)
        def fake_run_with_metrics(name, func, **kwargs):
            if name == "Critic":
                return SimpleNamespace(critique="stub critique")
            if name == "Refiner":
                return SimpleNamespace(
                    refined_artifact=refined_text,
                    structured_schedule=[],
                )
            return SimpleNamespace()

        monkeypatch.setattr(nlco_textual, "run_with_metrics", fake_run_with_metrics)
        app = nlco_textual.NLCOTextualApp()
        def fake_iteration(self, *, iteration_index: int, constraints_text: str) -> None:
            self._update_stage_log("timewarrior", "time ok")
            self._update_stage_log("memory", "memory ok")
            self._update_stage_log("planning", "plan ok")
            self._update_stage_log("critique", "stub critique")
            self._update_stage_log("refine", refined_text)
            self._update_stage_log("schedule", "[]")
            report = nlco_textual.AffectReport(
                emotions=["focused"],
                urgency="low",
                confidence="high",
                rationale="",
                suggested_focus="",
                goal_scores={"Keep schedule updated": 7},
            )
            self._update_affect(report)
            nlco_textual.ARTIFACT_FILE.write_text(refined_text)
            self._update_artifact(refined_text)
            self._update_artifact_editor(refined_text)
        app._run_iteration = MethodType(fake_iteration, app)
        return app, constraints_path, artifact_path, memory_path

    return factory


@pytest.mark.asyncio
async def test_constraint_messages_persist_to_file(app_factory):
    app, constraints_path, _, _ = app_factory()

    async with app.run_test() as pilot:
        app._handle_new_message("Review the roadmap")
        await pilot.pause()

        assert app._constraint_messages == ["Review the roadmap"]
        assert constraints_path.read_text() == "Review the roadmap"


@pytest.mark.asyncio
async def test_iteration_uses_entered_constraints(app_factory):
    refined_text = "Refined artifact body"
    app, constraints_path, artifact_path, _ = app_factory(refined_text=refined_text)
    artifact_path.write_text("Initial artifact")

    async with app.run_test() as pilot:
        app._handle_new_message("Respond to urgent emails")
        await pilot.pause()

        artifact_editor = app.query_one("#artifact-editor", TextArea)
        artifact_editor.text = "Initial artifact contents"

        app.action_run_iteration()
        for _ in range(20):
            if not app.is_running:
                break
            await pilot.pause()

        assert not app.is_running
        assert app.iteration_counter == 1
        if app._worker and app._worker.error:
            raise app._worker.error
        assert constraints_path.read_text() == "Respond to urgent emails"
        assert artifact_path.read_text() == refined_text
        assert app.query_one("#artifact-editor", TextArea).text == refined_text


@pytest.mark.asyncio
async def test_initial_artifact_displayed(app_factory):
    initial_text = "Existing artifact text"
    app, _, _, _ = app_factory(initial_artifact=initial_text)

    async with app.run_test() as pilot:
        await pilot.pause()
        artifact_log = app.query_one("#artifact-log", nlco_textual.Log)
        log_text = "\n".join(str(line) for line in artifact_log.lines)
        assert initial_text in log_text
        editor = app.query_one("#artifact-editor", TextArea)
        assert editor.text == initial_text


@pytest.mark.asyncio
async def test_initial_memory_displayed(app_factory):
    initial_memory = "Known memory line"
    app, _, _, memory_path = app_factory(initial_memory=initial_memory)

    async with app.run_test() as pilot:
        await pilot.pause()
        memory_log = app.query_one("#memory-log", nlco_textual.Log)
        log_text = "\n".join(str(line) for line in memory_log.lines)
        assert initial_memory in log_text
        assert memory_path.read_text() == initial_memory
