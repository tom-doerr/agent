import os
import sys
import types
from pathlib import Path

import pytest

# ensure project root on path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

cache_dir = Path("/tmp/dspy_cache_test")
cache_dir.mkdir(exist_ok=True)

os.environ.setdefault("DSPY_DISABLE_CACHE", "1")
os.environ.setdefault("DSPY_CACHE_DIR", str(cache_dir))

if "dspy" not in sys.modules:
    import types
    from contextlib import contextmanager

    fake_dspy = types.ModuleType("dspy")

    class _Field:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    class _Signature:
        def __init__(self, fields=None, instructions=""):
            self.input_fields = fields or {}
            self.instructions = instructions

        def append(self, *args, **kwargs):
            return self

    class _Predict:
        def __init__(self, *args, **kwargs):
            pass

        def __call__(self, *args, **kwargs):
            raise NotImplementedError

    class _LM:
        def __init__(self, *args, **kwargs):
            pass

    class _Module:
        def __init__(self, *args, **kwargs):
            pass

    class _Settings:
        @contextmanager
        def context(self, **kwargs):
            yield

    fake_dspy.InputField = _Field
    fake_dspy.OutputField = _Field
    fake_dspy.Signature = _Signature
    fake_dspy.Predict = _Predict
    fake_dspy.LM = _LM
    fake_dspy.Module = _Module
    fake_dspy.settings = _Settings()

    sys.modules["dspy"] = fake_dspy

from executive_module import ExecutiveModule
from affect_module import AffectReport


class StubModule:
    def __init__(self, label):
        self.label = label
        self.calls = 0
        self.last_kwargs = None

    def run(self, **kwargs):
        self.calls += 1
        self.last_kwargs = kwargs
        return f"{self.label} run"


def make_predictions(sequence):
    predictions = iter(sequence)

    def _predict(*, artifact, constraints, context, affect_summary, history_text):
        # record history and affect for later introspection
        _predict.history_calls.append(history_text)
        _predict.affect_calls.append(affect_summary)
        return next(predictions)

    _predict.history_calls = []
    _predict.affect_calls = []
    return _predict


def test_executive_invokes_tools_and_writes_short_term(tmp_path):
    time_mod = StubModule("time")
    memory_mod = StubModule("memory")

    exec_module = ExecutiveModule(
        lm=object(),
        timewarrior_module=time_mod,
        memory_module=memory_mod,
        console=None,
        short_term_path=tmp_path / "short.md",
    )

    predictions = [
        types.SimpleNamespace(
            thought="Check tracking",
            selected_tool="timewarrior_control",
            justification="Need to sync",
            summary="",
        ),
        types.SimpleNamespace(
            thought="Refresh memory",
            selected_tool="memory_update",
            justification="Store long-term context",
            summary="",
        ),
        types.SimpleNamespace(
            thought="All good",
            selected_tool="finish",
            justification="Done",
            summary="Executive summary",
        ),
    ]

    fake_predict = make_predictions(predictions)
    exec_module._predict_next_step = fake_predict

    affect = AffectReport(
        emotions=["focused"],
        urgency="medium",
        confidence="high",
        rationale="Schedule aligned",
        suggested_focus="Continue tasks",
        goal_scores={"Keep schedule updated": 7},
    )

    summary = exec_module.run(
        artifact="Artifact text",
        constraints="Constraints",
        context="Context info",
        affect_report=affect,
    )

    assert summary == "Executive summary"
    assert time_mod.calls == 1
    assert memory_mod.calls == 1

    # short-term memory file should include both tool executions
    content = (tmp_path / "short.md").read_text()
    assert "timewarrior_control" in content
    assert "memory_update" in content

    # history passed into the second prediction should include justification
    assert any("Reason: Need to sync" in chunk for chunk in fake_predict.history_calls)
    # affect summary should include goal score mention
    assert any("Goal scores" in chunk for chunk in fake_predict.affect_calls)


def test_executive_handles_no_action_without_writing_short_term(tmp_path):
    time_mod = StubModule("time")
    memory_mod = StubModule("memory")

    exec_module = ExecutiveModule(
        lm=object(),
        timewarrior_module=time_mod,
        memory_module=memory_mod,
        console=None,
        short_term_path=tmp_path / "short.md",
        max_iters=2,
    )

    predictions = [
        types.SimpleNamespace(
            thought="Waiting",
            selected_tool="none",
            justification="No evidence yet",
            summary="",
        ),
        types.SimpleNamespace(
            thought="Finish",
            selected_tool="finish",
            justification="Still nothing",
            summary="",
        ),
    ]

    fake_predict = make_predictions(predictions)
    exec_module._predict_next_step = fake_predict

    summary = exec_module.run(
        artifact="Artifact",
        constraints="Constraints",
        context="Context",
        affect_report=None,
    )

    assert summary == "Still nothing"
    assert time_mod.calls == 0
    assert memory_mod.calls == 0
    # short-term memory file should remain empty
    assert not (tmp_path / "short.md").exists() or (tmp_path / "short.md").read_text() == ""
    # ensure history recorded the "no action" observation
    assert any("No action taken." in chunk for chunk in fake_predict.history_calls)
