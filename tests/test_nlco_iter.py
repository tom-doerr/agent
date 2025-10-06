import asyncio
import sys
from types import SimpleNamespace
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import nlco_iter


@pytest.mark.asyncio
async def test_iteration_loop_triggers_async_memory(monkeypatch, tmp_path):
    constraints_path = tmp_path / "constraints.md"
    artifact_path = tmp_path / "artifact.md"
    constraints_path.write_text("Keep focus")
    artifact_path.write_text("Draft artifact")

    monkeypatch.setattr(nlco_iter, "CONSTRAINTS_FILE", constraints_path)
    monkeypatch.setattr(nlco_iter, "ARTIFACT_FILE", artifact_path)
    monkeypatch.setattr(nlco_iter, "MAX_ITERATIONS", 1)
    monkeypatch.setattr(nlco_iter, "MLFLOW_ENABLED", False)

    monkeypatch.setattr(nlco_iter, "create_context_string", lambda: "context")

    memory_calls = []
    memory_event = asyncio.Event()

    async def fake_memory_manager_async(*, constraints, context, artifact):
        memory_calls.append((constraints, context, artifact))
        await asyncio.sleep(0)
        memory_event.set()
        return "Memory updated"

    monkeypatch.setattr(nlco_iter, "memory_manager_async", fake_memory_manager_async)

    monkeypatch.setattr(
        nlco_iter,
        "affect_module",
        SimpleNamespace(run=lambda **_: None),
    )

    def fake_run_with_metrics(name, func, **kwargs):
        return func(**kwargs)

    monkeypatch.setattr(nlco_iter, "run_with_metrics", fake_run_with_metrics)

    class CriticResult:
        critique = "Needs edits"

    class RefinerResult:
        refined_artifact = "Refined artifact"

    def fake_critic(*, constraints, context, artifact):
        assert constraints == "Keep focus"
        assert context == "context"
        assert artifact == "Draft artifact"
        return CriticResult()

    def fake_refiner(*, constraints, context, critique, artifact):
        assert critique == "Needs edits"
        return RefinerResult()

    monkeypatch.setattr(nlco_iter, "critic", fake_critic)
    monkeypatch.setattr(nlco_iter, "refiner", fake_refiner)

    await nlco_iter.iteration_loop()

    assert memory_event.is_set(), "Memory async task was not awaited"
    assert memory_calls == [("Keep focus", "context", "Draft artifact")]
    assert artifact_path.read_text() == "Refined artifact"
