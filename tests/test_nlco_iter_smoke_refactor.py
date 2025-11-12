from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import pytest
import nlco_iter as mod


@pytest.mark.asyncio
async def test_nlco_iter_smoke_refactor(monkeypatch, tmp_path: Path):
    c = tmp_path / "constraints.md"
    a = tmp_path / "artifact.md"
    c.write_text("x")
    a.write_text("y")

    monkeypatch.setattr(mod, "CONSTRAINTS_FILE", c)
    monkeypatch.setattr(mod, "ARTIFACT_FILE", a)
    monkeypatch.setattr(mod, "MLFLOW_ENABLED", False)
    monkeypatch.setattr(mod, "MAX_ITERATIONS", 1)
    monkeypatch.setattr(mod, "create_context_string", lambda: "ctx")
    monkeypatch.setattr(mod.affect_module, "run", lambda **_: None)

    class P:
        refined_artifact = "z"

    monkeypatch.setattr(mod, "run_with_metrics", lambda *args, **kwargs: P())
    async def mem(**_):
        return None
    monkeypatch.setattr(mod, "memory_manager_async", mem)

    await mod.iteration_loop()
    assert a.read_text() == "z"

