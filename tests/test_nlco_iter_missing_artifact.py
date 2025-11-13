import asyncio
from pathlib import Path
from types import SimpleNamespace

import pytest

import nlco_iter


@pytest.mark.asyncio
async def test_iteration_creates_missing_artifact(monkeypatch, tmp_path: Path):
    constraints = tmp_path / "constraints.md"
    artifact = tmp_path / "artifact.md"  # intentionally not created

    constraints.write_text("c1")

    # point headless at temp files
    monkeypatch.setattr(nlco_iter, "CONSTRAINTS_FILE", constraints)
    monkeypatch.setattr(nlco_iter, "ARTIFACT_FILE", artifact)
    monkeypatch.setattr(nlco_iter, "MLFLOW_ENABLED", False)
    monkeypatch.setattr(nlco_iter, "MAX_ITERATIONS", 1)

    # keep external modules quiet
    monkeypatch.setattr(nlco_iter, "create_context_string", lambda: "CTX")

    async def mem_async(**_):
        return None

    monkeypatch.setattr(nlco_iter, "memory_manager_async", mem_async)
    monkeypatch.setattr(nlco_iter.affect_module, "run", lambda **_: None)

    class Result:
        refined_artifact = "A1"
        structured_schedule = []

    def fake_run_with_metrics(name, func, **kwargs):
        # return a minimal refiner result
        return Result()

    monkeypatch.setattr(nlco_iter, "run_with_metrics", fake_run_with_metrics)

    # Should not crash despite missing artifact; should create it
    await nlco_iter.iteration_loop(max_iterations=1)
    assert artifact.exists()
    assert artifact.read_text() == "A1"

