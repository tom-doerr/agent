"""DSPy module that computes diffs for constraints and suggests Taskwarrior commands."""

from __future__ import annotations

import asyncio
import difflib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional, Sequence, Set, Tuple

import dspy
from rich.console import Console
from rich.panel import Panel


class ConstraintsDiffSignature(dspy.Signature):
    diff_text: str = dspy.InputField(desc="Unified diff between previous and current constraints.md")
    previous_constraints: str = dspy.InputField(desc="Snapshot of constraints before latest change")
    current_constraints: str = dspy.InputField(desc="Full text of current constraints after change")
    task_context: str = dspy.InputField(desc="Taskwarrior export (JSON) for tasks tagged +nlco")
    feedback: str = dspy.InputField(desc="Optional issues from prior verification attempts (empty on first pass)")
    notes: str = dspy.OutputField(desc="Optional high-level summary of the change")
    taskwarrior_commands: list[str] = dspy.OutputField(desc="List of Taskwarrior CLI commands to apply")


@dataclass
class ConstraintsDiffResult:
    commands: list[str]
    diff: str
    notes: str


class ConstraintsDiffModule(dspy.Module):
    """Generate Taskwarrior actions from edits to constraints.md."""

    def __init__(
        self,
        lm: dspy.LM,
        *,
        constraints_path: Path | str = "constraints.md",
        snapshot_path: Path | str = ".nlco/cache/constraints_snapshot.md",
        console: Optional[Console] = None,
    ) -> None:
        super().__init__()
        self.lm = lm
        self.constraints_path = Path(constraints_path)
        self.snapshot_path = Path(snapshot_path)
        self.console = console or Console()
        self.predictor = dspy.Predict(
            ConstraintsDiffSignature,
            instructions=(
                "You receive the unified diff of constraints.md between the last run and now. "
                "Produce Taskwarrior CLI commands (e.g. `task add ...`, `task <id> modify ...`, "
                "`task <id> done`, `task <id> delete`) that reconcile Taskwarrior with the changes. "
                "Return only executable commands; omit commentary."
            ),
        )

    async def arun(
        self,
        *,
        constraints_text: Optional[str] = None,
        feedback: str = "",
    ) -> ConstraintsDiffResult:
        """Compute diff and request Taskwarrior commands (async)."""

        current_text = constraints_text if constraints_text is not None else self._read_constraints()
        previous_text = self._read_snapshot()

        if current_text == previous_text:
            return ConstraintsDiffResult(commands=[], diff="", notes="No changes detected.")

        diff_text = self._unified_diff(previous_text, current_text)

        task_context = self._get_task_context()

        def _predict() -> ConstraintsDiffResult:
            with dspy.settings.context(lm=self.lm):
                prediction = self.predictor(
                    diff_text=diff_text,
                    previous_constraints=previous_text,
                    current_constraints=current_text,
                    task_context=task_context,
                    feedback=feedback,
                )

            commands_raw = getattr(prediction, "taskwarrior_commands", [])
            if isinstance(commands_raw, str):
                commands = [cmd.strip() for cmd in commands_raw.splitlines() if cmd.strip()]
            elif isinstance(commands_raw, list):
                commands = [str(cmd).strip() for cmd in commands_raw if str(cmd).strip()]
            else:
                commands = []

            notes = getattr(prediction, "notes", "")
            return ConstraintsDiffResult(commands=commands, diff=diff_text, notes=str(notes).strip())

        result = await asyncio.to_thread(_predict)

        allowed_ids = self._parse_task_context(task_context)
        filtered_commands = []
        for cmd in result.commands:
            tagged = self._ensure_tag(cmd)
            if self._allow_command(tagged, allowed_ids):
                filtered_commands.append(tagged)

        result = ConstraintsDiffResult(
            commands=filtered_commands,
            diff=diff_text,
            notes=result.notes,
        )

        self._write_snapshot(current_text)
        self._log_result(diff_text, result)
        return result

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _read_constraints(self) -> str:
        if not self.constraints_path.exists():
            return ""
        return self.constraints_path.read_text()

    def _read_snapshot(self) -> str:
        if not self.snapshot_path.exists():
            return ""
        try:
            return self.snapshot_path.read_text()
        except Exception:
            return ""

    def _write_snapshot(self, text: str) -> None:
        self.snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        self.snapshot_path.write_text(text)

    def _unified_diff(self, old: str, new: str) -> str:
        old_lines = old.splitlines()
        new_lines = new.splitlines()
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile="constraints.prev",
            tofile="constraints.current",
            lineterm="",
        )
        return "\n".join(diff)

    def _log_result(self, diff_text: str, result: ConstraintsDiffResult) -> None:
        if diff_text:
            self.console.print(Panel(diff_text or "<no diff>", title="Constraints Diff", border_style="cyan"))
        if result.notes:
            self.console.print(Panel(result.notes, title="Reasoning", border_style="blue"))
        if result.commands:
            commands_render = "\n".join(result.commands)
            self.console.print(Panel(commands_render, title="Taskwarrior Commands", border_style="green"))
        elif diff_text:
            self.console.print(Panel("No Taskwarrior actions suggested.", border_style="yellow"))

    def _get_task_context(self) -> str:
        try:
            completed = subprocess.run(
                ["task", "+nlco", "export"],
                capture_output=True,
                text=True,
                check=True,
            )
            return completed.stdout.strip() or "[]"
        except Exception:
            return "[]"

    @staticmethod
    def _parse_task_context(task_context: str) -> Set[int]:
        allowed: Set[int] = set()
        try:
            data = json.loads(task_context) if task_context else []
            if isinstance(data, dict):
                data = [data]
            for item in data:
                if isinstance(item, dict):
                    task_id = item.get("id")
                    if isinstance(task_id, int):
                        allowed.add(task_id)
        except Exception:
            pass
        return allowed

    @staticmethod
    def _ensure_tag(command: str) -> str:
        tag = "+nlco"
        if tag in command:
            return command
        parts = command.split()
        if not parts:
            return command
        if parts[0] == "task":
            if len(parts) >= 2 and parts[1].isdigit():
                return " ".join(parts[:2] + [tag] + parts[2:])
            if len(parts) >= 2 and parts[1] == "add":
                return " ".join(parts[:2] + [tag] + parts[2:])
        return f"{command} {tag}"

    @staticmethod
    def _allow_command(command: str, allowed_ids: Set[int]) -> bool:
        parts = command.split()
        if not parts:
            return False
        if parts[0] != "task":
            return False
        if len(parts) >= 2 and parts[1] == "add":
            return True
        if len(parts) >= 2 and parts[1].isdigit():
            return int(parts[1]) in allowed_ids
        return False


class TaskwarriorVerificationSignature(dspy.Signature):
    diff_text: str = dspy.InputField(desc="Unified diff between previous and current constraints.md")
    previous_tasks: str = dspy.InputField(desc="Taskwarrior export (JSON) before applying commands")
    new_tasks: str = dspy.InputField(desc="Taskwarrior export (JSON) after applying commands")
    commands: list[str] = dspy.InputField(desc="Commands that were executed")
    command_outputs: str = dspy.InputField(desc="Combined stdout/stderr from command execution")
    verification_passed: bool = dspy.OutputField(desc="True if Taskwarrior state matches expectations")
    issues: list[str] = dspy.OutputField(desc="Issues detected that need remediation")
    notes: str = dspy.OutputField(desc="Optional summary or guidance")


@dataclass
class VerificationResult:
    passed: bool
    issues: list[str]
    notes: str


class TaskwarriorVerificationModule(dspy.Module):
    def __init__(self, lm: dspy.LM, *, console: Optional[Console] = None) -> None:
        super().__init__()
        self.lm = lm
        self.console = console or Console()
        self.predictor = dspy.Predict(
            TaskwarriorVerificationSignature,
            instructions=(
                "Using the diff, Taskwarrior state before/after, executed commands, and their outputs, "
                "decide if the updates succeeded. If not, list concrete issues (missing tasks, wrong fields, "
                "errors in outputs)."
            ),
        )

    async def arun(
        self,
        *,
        diff_text: str,
        previous_tasks: str,
        new_tasks: str,
        commands: Sequence[str],
        command_outputs: str,
    ) -> VerificationResult:
        def _predict() -> VerificationResult:
            with dspy.settings.context(lm=self.lm):
                prediction = self.predictor(
                    diff_text=diff_text,
                    previous_tasks=previous_tasks,
                    new_tasks=new_tasks,
                    commands=list(commands),
                    command_outputs=command_outputs,
                )

            passed = bool(getattr(prediction, "verification_passed", False))
            issues_raw = getattr(prediction, "issues", [])
            if isinstance(issues_raw, str):
                issues = [issues_raw.strip()] if issues_raw.strip() else []
            elif isinstance(issues_raw, list):
                issues = [str(issue).strip() for issue in issues_raw if str(issue).strip()]
            else:
                issues = []
            notes = str(getattr(prediction, "notes", "")).strip()
            if notes and not passed:
                self.console.print(Panel(notes, title="Verification Notes", border_style="red"))
            return VerificationResult(passed=passed, issues=issues, notes=notes)

        return await asyncio.to_thread(_predict)


async def reconcile_constraints_with_taskwarrior(
    *,
    diff_module: ConstraintsDiffModule,
    verification_module: TaskwarriorVerificationModule,
    get_task_export: Callable[[], str],
    execute_commands: Callable[[Sequence[str]], Tuple[str, bool]],
    constraints_text: Optional[str] = None,
    max_iters: int = 3,
) -> ConstraintsDiffResult:
    feedback = ""
    last_result = ConstraintsDiffResult(commands=[], diff="", notes="")

    for attempt in range(max_iters):
        diff_result = await diff_module.arun(constraints_text=constraints_text, feedback=feedback)
        last_result = diff_result
        if not diff_result.commands:
            return diff_result

        previous_tasks = get_task_export()
        command_outputs, execution_ok = execute_commands(diff_result.commands)
        new_tasks = get_task_export()

        verification = await verification_module.arun(
            diff_text=diff_result.diff,
            previous_tasks=previous_tasks,
            new_tasks=new_tasks,
            commands=diff_result.commands,
            command_outputs=command_outputs,
        )

        if verification.passed and execution_ok:
            notes = verification.notes or diff_result.notes
            return ConstraintsDiffResult(commands=diff_result.commands, diff=diff_result.diff, notes=notes)

        feedback_lines = verification.issues or []
        if not feedback_lines:
            message = verification.notes or "Verification failed but no issues were provided."
            feedback_lines = [message]
        feedback = "\n".join(feedback_lines)

    return last_result


__all__ = [
    "ConstraintsDiffModule",
    "ConstraintsDiffResult",
    "TaskwarriorVerificationModule",
    "VerificationResult",
    "reconcile_constraints_with_taskwarrior",
]
