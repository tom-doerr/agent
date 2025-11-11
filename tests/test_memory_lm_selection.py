import nlco_iter
import nlco_textual
import pytest


def test_headless_memory_uses_main_lm():
    assert getattr(nlco_iter.memory_manager, "lm", None) is nlco_iter.lm


@pytest.mark.asyncio
async def test_textual_memory_uses_primary_lm(monkeypatch):
    captured = {}

    def fake_setup(self):
        self._primary_lm = object()
        self._support_lm = object()

    def fake_config(self):
        self._mlflow_enabled = False

    class DummyMemoryModule:
        def __init__(self, lm, *, console=None):
            captured["lm"] = lm
        def run(self, **kwargs):
            return "ok"

    # Make heavy deps no-ops
    monkeypatch.setattr(nlco_textual.NLCOTextualApp, "_setup_language_models", fake_setup)
    monkeypatch.setattr(nlco_textual.NLCOTextualApp, "_configure_mlflow", fake_config)
    monkeypatch.setattr(nlco_textual, "TimewarriorModule", lambda *a, **k: type("X", (), {"run": lambda self, **kw: "ok"})())
    monkeypatch.setattr(nlco_textual, "PlanningModule", lambda *a, **k: type("X", (), {"run": lambda self, **kw: "ok"})())
    monkeypatch.setattr(nlco_textual, "AffectModule", lambda *a, **k: type("X", (), {"run": lambda self, **kw: None})())
    monkeypatch.setattr(nlco_textual, "run_with_metrics", lambda *a, **k: type("Y", (), {"critique": "", "refined_artifact": "", "structured_schedule": []})())
    monkeypatch.setattr(nlco_textual, "MemoryModule", DummyMemoryModule)

    app = nlco_textual.NLCOTextualApp()
    async with app.run_test() as pilot:
        app.action_run_iteration()
        for _ in range(200):
            if captured.get("lm") is not None and not app.is_running:
                break
            await pilot.pause()
    assert captured.get("lm") is app._primary_lm
