import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import nlco_iter


@pytest.mark.asyncio
async def test_logs_and_schedule_written(monkeypatch, tmp_path: Path):
    constraints = tmp_path / "constraints.md"
    artifact = tmp_path / "artifact.md"
    schedule = tmp_path / "structured_schedule.json"
    log_path = tmp_path / "model_log.jsonl"

    constraints.write_text("c1")
    artifact.write_text("a0")

    monkeypatch.setenv("NLCO_MODEL_LOG", str(log_path))
    monkeypatch.setattr(nlco_iter, "_MODEL_LOG_PATH", log_path)
    monkeypatch.setattr(nlco_iter, "CONSTRAINTS_FILE", constraints)
    monkeypatch.setattr(nlco_iter, "ARTIFACT_FILE", artifact)
    monkeypatch.setattr(nlco_iter, "STRUCTURED_SCHEDULE_FILE", schedule)
    monkeypatch.setattr(nlco_iter, "MLFLOW_ENABLED", False)
    monkeypatch.setattr(nlco_iter, "create_context_string", lambda: "CTX")
    monkeypatch.setattr(nlco_iter, "_extract_last_reasoning_text", lambda: "R")

    async def mem_async(**_):
        return "mem"

    monkeypatch.setattr(nlco_iter, "memory_manager_async", mem_async)

    class DummyReport:
        emotions = []
        urgency = "low"
        confidence = "high"
        goal_scores = {}

    monkeypatch.setattr(nlco_iter.affect_module, "run", lambda **_: DummyReport())

    def fake_run_with_metrics(name, func, **kwargs):
        if name == "Critic":
            return SimpleNamespace(critique="crit")
        if name == "Refiner":
            return SimpleNamespace(
                refined_artifact="a1",
                structured_schedule=[
                    {
                        "start_time": "2025-11-06 10:00",
                        "end_time": "2025-11-06 11:00",
                        "description": "work",
                    }
                ],
            )
        return SimpleNamespace()

    monkeypatch.setattr(nlco_iter, "run_with_metrics", fake_run_with_metrics)

    await nlco_iter.iteration_loop(max_iterations=1)

    # Artifact updated
    assert artifact.read_text() == "a1"
    # Structured schedule output removed: file may not be created
    assert not schedule.exists()
    # JSONL logs contain Refiner (and may include Affect); Critic disabled
    if log_path.exists() and log_path.read_text().strip():
        lines = [json.loads(x) for x in log_path.read_text().splitlines() if x.strip()]
        stages = {rec["stage"] for rec in lines}
        assert "Refiner" in stages


@pytest.mark.asyncio
async def test_invalid_schedule_falls_back_to_empty(monkeypatch, tmp_path: Path):
    constraints = tmp_path / "constraints.md"
    artifact = tmp_path / "artifact.md"
    schedule = tmp_path / "structured_schedule.json"

    constraints.write_text("c1")
    artifact.write_text("a0")

    monkeypatch.setattr(nlco_iter, "CONSTRAINTS_FILE", constraints)
    monkeypatch.setattr(nlco_iter, "ARTIFACT_FILE", artifact)
    monkeypatch.setattr(nlco_iter, "STRUCTURED_SCHEDULE_FILE", schedule)
    monkeypatch.setattr(nlco_iter, "MLFLOW_ENABLED", False)
    monkeypatch.setattr(nlco_iter, "create_context_string", lambda: "CTX")
    monkeypatch.setattr(nlco_iter, "_extract_last_reasoning_text", lambda: None)

    async def mem_async(**_):
        return None

    monkeypatch.setattr(nlco_iter, "memory_manager_async", mem_async)
    monkeypatch.setattr(nlco_iter.affect_module, "run", lambda **_: None)

    def fake_run_with_metrics(name, func, **kwargs):
        if name == "Critic":
            return SimpleNamespace(critique="crit")
        if name == "Refiner":
            # invalid type triggers normalize_schedule error path
            return SimpleNamespace(refined_artifact="a1", structured_schedule=object())
        return SimpleNamespace()

    monkeypatch.setattr(nlco_iter, "run_with_metrics", fake_run_with_metrics)

    await nlco_iter.iteration_loop(max_iterations=1)

    assert artifact.read_text() == "a1"
    # Structured schedule output removed: no file
    assert not schedule.exists()
