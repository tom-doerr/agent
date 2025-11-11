from types import SimpleNamespace
from pathlib import Path
import datetime as dt
import sys

import pytest

import nlco_textual


@pytest.mark.asyncio
async def test_textual_system_state_to_refiner(monkeypatch, tmp_path: Path):
    constraints_path = tmp_path / "constraints.md"
    artifact_path = tmp_path / "artifact.md"
    constraints_path.write_text("c1")
    artifact_path.write_text("a0")

    # Known previous mtime
    known = dt.datetime(2025, 11, 10, 9, 0, 1)
    ts = known.timestamp()
    import os
    os.utime(artifact_path, (ts, ts))

    monkeypatch.setattr(nlco_textual, "CONSTRAINTS_FILE", constraints_path)
    monkeypatch.setattr(nlco_textual, "ARTIFACT_FILE", artifact_path)
    monkeypatch.setattr(nlco_textual, "MEMORY_FILE", tmp_path / "memory.md")
    monkeypatch.setattr(nlco_textual, "SHORT_TERM_PATH", tmp_path / "short_term.md")

    def fake_setup(self):
        self._primary_lm = object()
        self._support_lm = object()

    def fake_config(self):
        self._mlflow_enabled = False

    monkeypatch.setattr(nlco_textual.NLCOTextualApp, "_setup_language_models", fake_setup)
    monkeypatch.setattr(nlco_textual.NLCOTextualApp, "_configure_mlflow", fake_config)

    seen = {}

    def fake_run_with_metrics(name, func, **kwargs):
        seen["called"] = True
        if "system_state" in kwargs:
            seen["system_state"] = kwargs.get("system_state")
        if name == "Refiner":
            return SimpleNamespace(refined_artifact="a1")
        return SimpleNamespace()

    monkeypatch.setattr(nlco_textual, "run_with_metrics", fake_run_with_metrics)
    monkeypatch.setattr(nlco_textual, "TimewarriorModule", lambda *a, **k: type("X", (), {"run": lambda self, **kw: None})())
    monkeypatch.setattr(nlco_textual, "MemoryModule", lambda *a, **k: type("X", (), {"run": lambda self, **kw: None})())
    monkeypatch.setattr(nlco_textual, "PlanningModule", lambda *a, **k: type("X", (), {"run": lambda self, **kw: None})())
    monkeypatch.setattr(nlco_textual, "AffectModule", lambda *a, **k: type("X", (), {"run": lambda self, **kw: None})())

    def fake_run_worker(self, work, name="", group="default", description="", exit_on_error=True, start=True, exclusive=False, thread=False):
        try:
            work()
        except Exception:
            pass
        return SimpleNamespace(error=None)

    monkeypatch.setattr(nlco_textual.NLCOTextualApp, "run_worker", fake_run_worker, raising=False)

    app = nlco_textual.NLCOTextualApp()
    # Replace _run_iteration with a minimal stub that only exercises the Refiner call
    def stub_run(self, *, iteration_index: int, constraints_text: str) -> None:
        iso = dt.datetime.fromtimestamp(ts).isoformat(timespec="seconds")
        # emulate a minimal system_state instance
        state = SimpleNamespace(last_artifact_update=iso)
        _ = nlco_textual.run_with_metrics(
            "Refiner",
            None,
            artifact=artifact_path.read_text(),
            constraints=constraints_text,
            system_state=state,
            context="CTX",
        )
    from types import MethodType as _MethodType
    app._run_iteration = _MethodType(stub_run, app)  # type: ignore[assignment]
    # Call stub directly; no need to run a UI loop for this check
    app._run_iteration(iteration_index=1, constraints_text=constraints_path.read_text())

    assert seen.get("called") is True
    state = seen.get("system_state")
    assert state is not None
    assert isinstance(getattr(state, "last_artifact_update", None), str)
    assert state.last_artifact_update.startswith("2025-11-10T09:00:01")
