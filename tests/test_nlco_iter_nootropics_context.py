from types import SimpleNamespace
from pathlib import Path

import pytest

import nlco_iter


@pytest.mark.asyncio
async def test_headless_context_includes_nootropics(monkeypatch, tmp_path: Path):
    # Redirect files to tmp
    constraints = tmp_path / "constraints.md"
    artifact = tmp_path / "artifact.md"
    schedule = tmp_path / "structured_schedule.json"
    constraints.write_text("stay focused")
    artifact.write_text("initial artifact")
    monkeypatch.setattr(nlco_iter, "CONSTRAINTS_FILE", constraints)
    monkeypatch.setattr(nlco_iter, "ARTIFACT_FILE", artifact)
    monkeypatch.setattr(nlco_iter, "STRUCTURED_SCHEDULE_FILE", schedule)

    # Stable base context
    monkeypatch.setattr(nlco_iter, "create_context_string", lambda: "CTX")
    monkeypatch.setattr(nlco_iter, "_extract_last_reasoning_text", lambda: None)

    # Nootropics lines via helper
    import nootropics_log as nl
    monkeypatch.setattr(nl, "load_recent_nootropics_lines", lambda **kwargs: ['{"ts":"2025-11-06 10:00:00","note":"alpha"}'])

    # Async memory stub
    async def _mem_async(**kwargs):
        return "mem ok"

    monkeypatch.setattr(nlco_iter, "memory_manager_async", _mem_async)

    # Affect stub
    class DummyReport:
        emotions = []
        urgency = "low"
        confidence = "high"
        goal_scores = {}

    monkeypatch.setattr(nlco_iter.affect_module, "run", lambda **kwargs: DummyReport())

    # Capture contexts used by Critic/Refiner
    seen = []

    def fake_run_with_metrics(name, func, **kwargs):
        seen.append(kwargs.get("context", ""))
        # ensure constraints unchanged
        assert kwargs.get("constraints") == "stay focused"
        if name == "Critic":
            return SimpleNamespace(critique="ok")
        if name == "Refiner":
            return SimpleNamespace(refined_artifact="new", structured_schedule=[])
        return SimpleNamespace()

    monkeypatch.setattr(nlco_iter, "run_with_metrics", fake_run_with_metrics)

    await nlco_iter.iteration_loop(max_iterations=1)

    assert seen, "Expected contexts to be passed"
    ctx = "\n".join(seen)
    assert "CTX" in ctx
    assert "Nootropics (last 72h)" in ctx
    assert "alpha" in ctx
