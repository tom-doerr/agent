import asyncio
from pathlib import Path

import pytest

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from constraints_diff_module import (
    ConstraintsDiffModule,
    ConstraintsDiffResult,
    TaskwarriorVerificationModule,
    VerificationResult,
    reconcile_constraints_with_taskwarrior,
)


@pytest.mark.asyncio
async def test_diff_module_generates_commands(tmp_path, monkeypatch):
    constraints_path = tmp_path / "constraints.md"
    snapshot_path = tmp_path / "snapshot.md"

    previous_text = "line a\nline b"
    current_text = "line a\nline b\nline c"

    constraints_path.write_text(current_text)
    snapshot_path.write_text(previous_text)

    module = ConstraintsDiffModule(
        lm=None,
        constraints_path=constraints_path,
        snapshot_path=snapshot_path,
    )

    monkeypatch.setattr(module, "_get_task_context", lambda: "[{\"id\": 3}]")

    called = {}

    def fake_predictor(*, diff_text, previous_constraints, current_constraints, task_context, feedback):
        called["diff"] = diff_text
        called["prev"] = previous_constraints
        called["cur"] = current_constraints
        called["tasks"] = task_context
        called["feedback"] = feedback

        class Prediction:
            taskwarrior_commands = ["task add Review new constraint"]
            notes = "Add review task"

        return Prediction()

    monkeypatch.setattr(module, "predictor", fake_predictor)

    result = await module.arun(constraints_text=current_text)

    assert isinstance(result, ConstraintsDiffResult)
    assert result.commands == ["task add +nlco Review new constraint"]
    assert "line c" in called["cur"]
    assert called["tasks"] == '[{"id": 3}]'
    assert called["feedback"] == ""
    assert snapshot_path.read_text() == current_text


@pytest.mark.asyncio
async def test_diff_module_no_changes_skips_predictor(tmp_path, monkeypatch):
    constraints_path = tmp_path / "constraints.md"
    snapshot_path = tmp_path / "snapshot.md"

    text = "same text"
    constraints_path.write_text(text)
    snapshot_path.write_text(text)

    module = ConstraintsDiffModule(
        lm=None,
        constraints_path=constraints_path,
        snapshot_path=snapshot_path,
    )

    monkeypatch.setattr(module, "_get_task_context", lambda: "[{\"id\": 5}]")

    called = False

    def fake_predictor(**kwargs):
        nonlocal called
        called = True

    monkeypatch.setattr(module, "predictor", fake_predictor)

    result = await module.arun(constraints_text=text)

    assert result.commands == []
    assert not called


@pytest.mark.asyncio
async def test_diff_module_filters_commands_for_other_ids(tmp_path, monkeypatch):
    constraints_path = tmp_path / "constraints.md"
    snapshot_path = tmp_path / "snapshot.md"

    constraints_path.write_text("line1")
    snapshot_path.write_text("old")

    module = ConstraintsDiffModule(
        lm=None,
        constraints_path=constraints_path,
        snapshot_path=snapshot_path,
    )

    monkeypatch.setattr(module, "_get_task_context", lambda: "[{\"id\": 7}]")

    class Prediction:
        taskwarrior_commands = ["task 3 modify note"]
        notes = "modify" 

    def fake_predictor_other(**kwargs):
        return Prediction()

    monkeypatch.setattr(module, "predictor", fake_predictor_other)

    result = await module.arun(constraints_text="line1")

    assert result.commands == []


@pytest.mark.asyncio
async def test_verification_module_returns_result(monkeypatch):
    module = TaskwarriorVerificationModule(lm=None)

    def fake_predictor(*, diff_text, previous_tasks, new_tasks, commands, command_outputs):
        class Prediction:
            verification_passed = True
            issues = []
            notes = "All good"

        return Prediction()

    monkeypatch.setattr(module, "predictor", fake_predictor)

    result = await module.arun(
        diff_text="diff",
        previous_tasks="[]",
        new_tasks="[]",
        commands=["task add +nlco foo"],
        command_outputs="OK",
    )

    assert isinstance(result, VerificationResult)
    assert result.passed is True
    assert result.issues == []
    assert result.notes == "All good"


@pytest.mark.asyncio
async def test_reconcile_constraints_with_taskwarrior_retries(monkeypatch):
    class StubDiff:
        def __init__(self):
            self.calls = []

        async def arun(self, *, constraints_text=None, feedback=""):
            self.calls.append(feedback)
            return ConstraintsDiffResult(commands=["task add Review"], diff="@@ diff", notes="")

    stub_diff = StubDiff()

    verification_module = TaskwarriorVerificationModule(lm=None)

    outcomes = [
        VerificationResult(passed=False, issues=["Task missing"], notes="Mismatch"),
        VerificationResult(passed=True, issues=[], notes="Now aligned"),
    ]

    call_index = {"value": 0}

    def selector(*args, **kwargs):
        idx = call_index["value"]
        call_index["value"] += 1
        outcome = outcomes[idx]
        return type("P", (), {
            "verification_passed": outcome.passed,
            "issues": outcome.issues,
            "notes": outcome.notes,
        })()

    monkeypatch.setattr(verification_module, "predictor", selector)

    exports = iter(["[]", "[]", "[]", "[]"])

    def get_task_export():
        return next(exports)

    command_runs = []

    def execute_commands(cmds):
        command_runs.append(list(cmds))
        return ("ok", True)

    result = await reconcile_constraints_with_taskwarrior(
        diff_module=stub_diff,
        verification_module=verification_module,
        get_task_export=get_task_export,
        execute_commands=execute_commands,
        constraints_text="new",
        max_iters=3,
    )

    assert len(command_runs) == 2
    assert stub_diff.calls == ["", "Task missing"]
    assert result.notes == "Now aligned"
