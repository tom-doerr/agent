import datetime as dt
from types import SimpleNamespace
from pathlib import Path

import pytest

import nlco_iter


@pytest.mark.asyncio
async def test_system_state_passed_to_refiner(monkeypatch, tmp_path: Path):
    constraints = tmp_path / "constraints.md"
    artifact = tmp_path / "artifact.md"
    constraints.write_text("c1")
    artifact.write_text("a0")

    # Set a known previous mtime
    known = dt.datetime(2025, 11, 10, 12, 34, 56)
    ts = known.timestamp()
    import os
    os.utime(artifact, (ts, ts))

    monkeypatch.setattr(nlco_iter, "CONSTRAINTS_FILE", constraints)
    monkeypatch.setattr(nlco_iter, "ARTIFACT_FILE", artifact)
    monkeypatch.setattr(nlco_iter, "MLFLOW_ENABLED", False)
    monkeypatch.setattr(nlco_iter, "create_context_string", lambda: "CTX")
    monkeypatch.setattr(nlco_iter, "_extract_last_reasoning_text", lambda: None)

    async def mem_async(**_):
        return None

    monkeypatch.setattr(nlco_iter, "memory_manager_async", mem_async)
    monkeypatch.setattr(nlco_iter.affect_module, "run", lambda **_: None)

    seen = {}

    def fake_run_with_metrics(name, func, **kwargs):
        if name == "Refiner":
            seen["system_state"] = kwargs.get("system_state")
            return SimpleNamespace(refined_artifact="a1")
        return SimpleNamespace()

    monkeypatch.setattr(nlco_iter, "run_with_metrics", fake_run_with_metrics)

    await nlco_iter.iteration_loop(max_iterations=1)

    state = seen.get("system_state")
    assert state is not None
    assert isinstance(getattr(state, "last_artifact_update", None), str)
    assert state.last_artifact_update.startswith("2025-11-10T12:34:56")

