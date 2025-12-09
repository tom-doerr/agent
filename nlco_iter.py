#!/usr/bin/env python3

import asyncio
import datetime
import difflib
from pathlib import Path
import re
from typing import Optional
import json
import os

from pydantic import BaseModel, Field

import dspy
from rich.console import Console
from rich.panel import Panel

try:
    import mlflow
    from packaging.version import Version
except Exception:  # pragma: no cover - optional dependency
    mlflow = None
    Version = None

from context_provider import create_context_string
from nootropics_log import append_nootropics_section
from metrics_utils import run_with_metrics
from timewarrior_module import TimewarriorModule
from memory_module import MemoryModule
from planning_module import PlanningModule
from affect_module import AffectModule
from nlco_scheduler import evaluate_run_decision
from refiner_signature import RefineSignature, SystemState, ArtifactEdit
import timestamp_app_core as core

# Print DSPy version at startup
print(f"DSPy version: {dspy.__version__}")

lm=dspy.LM('deepseek/deepseek-reasoner', max_tokens=40_000, num_retries=5)
# lm = dspy.LM( 'ollama_chat/deepseek-r1:8b', api_base='http://localhost:11434', api_key='', temperature=0,  # Critical for structured output max_tokens=2000  # Prevent rambling)
dspy.configure(lm=lm)

support_lm = dspy.LM('deepseek/deepseek-chat', max_tokens=4_000, temperature=0, num_retries=5)
console = Console()
# Shared paths for memory files
MEMORY_FILE = core.resolve_memory_path()
SHORT_TERM_FILE = core.resolve_short_term_path()
timewarrior_tracker = TimewarriorModule(support_lm, console=console, short_term_path=SHORT_TERM_FILE)
memory_manager = MemoryModule(lm, console=console, memory_path=MEMORY_FILE)
memory_manager_async = dspy.asyncify(memory_manager.run)
planning_manager = PlanningModule(support_lm, console=console)
affect_module = AffectModule(support_lm, console=console)

MLFLOW_ENABLED = False
if mlflow is not None:
    try:
        mlflow.set_tracking_uri("http://localhost:5010")
        mlflow.set_experiment("nlco_iter")
        if Version is not None and Version(mlflow.__version__) >= Version("2.18.0"):
            try:
                mlflow.dspy.autolog()
            except Exception as autolog_exc:  # pragma: no cover - diagnostic only
                console.print(Panel(f"MLflow autolog not enabled: {autolog_exc}", border_style="yellow"))
        else:  # pragma: no cover - diagnostic only
            console.print(Panel("MLflow < 2.18.0 detected; tracing autolog is unavailable.", border_style="yellow"))
        MLFLOW_ENABLED = True
    except Exception as exc:  # pragma: no cover - logging only
        console.print(Panel(f"MLflow disabled: {exc}", border_style="red"))
else:  # pragma: no cover - logging only
    console.print(Panel("MLflow not available; logging disabled.", border_style="yellow"))


refiner = dspy.Predict(
    RefineSignature,
    instructions=(
        "Output single-line search/replace edits to refine the artifact. Keep edits minimal and targeted."
    ),
)
# Critic module removed; refiner operates without an explicit critique input.
is_finished_checker = dspy.Predict('history -> is_finished: bool, reasoning')

# Use shared resolvers so headless matches the TUI defaults
CONSTRAINTS_FILE = core.resolve_constraints_path()
ARTIFACT_FILE = core.resolve_artifact_path()
STRUCTURED_SCHEDULE_FILE = Path('structured_schedule.json')

MAX_ITERATIONS = int(os.getenv("NLCO_MAX_ITERS", "3"))

_MODEL_LOG_PATH = Path(os.getenv("NLCO_MODEL_LOG", ".nlco/model_log.jsonl"))


def _now_str() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _save_artifact_history(artifact_path: Path, content: str) -> None:
    """Save artifact version with datetime to history dir next to artifact."""
    history_dir = artifact_path.parent / "artifact_history"
    history_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    history_file = history_dir / f"artifact_{ts}.md"
    history_file.write_text(content)


def _extract_reasoning_from_message(msg: dict) -> str | None:
    """Return provider-native reasoning text, if present.
    - DeepSeek API: message["reasoning_content"] (string)
    - OpenRouter: message["reasoning"] may be a dict with "text" or "summary".
    """
    if not isinstance(msg, dict):
        return None
    rc = msg.get("reasoning_content")
    if isinstance(rc, str) and rc.strip():
        return rc.strip()
    r = msg.get("reasoning")
    if isinstance(r, dict):
        text = r.get("text") or r.get("summary")
        if isinstance(text, str) and text.strip():
            return text.strip()
    return None


def _extract_last_reasoning_text() -> str | None:
    try:
        resp = lm.history[-1]["response"]
        msg = resp["choices"][0]["message"]
    except Exception:
        return None
    return _extract_reasoning_from_message(msg)


def _log_model(stage: str, *, output: str | None, reasoning: str | None) -> None:
    _MODEL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        "stage": stage,
        "output": output or "",
        "reasoning": reasoning or "",
    }
    with _MODEL_LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _read_artifact_and_state() -> tuple[str, SystemState]:
    try:
        artifact = ARTIFACT_FILE.read_text()
    except FileNotFoundError:
        artifact = ""
    try:
        prev_mtime = ARTIFACT_FILE.stat().st_mtime
    except FileNotFoundError:
        prev_mtime = datetime.datetime.now().timestamp()
    state = SystemState(
        last_artifact_update=datetime.datetime.fromtimestamp(prev_mtime).isoformat(timespec="seconds")
    )
    return artifact, state


def _read_constraints_and_context() -> tuple[str, str]:
    constraints = CONSTRAINTS_FILE.read_text().strip()
    context = create_context_string()
    context = append_nootropics_section(context)
    return constraints, context


def _log_affect(affect_report, *, iteration_index: int) -> None:
    try:
        summary = (
            f"emotions={affect_report.emotions}, urgency={affect_report.urgency}, "
            f"confidence={affect_report.confidence}"
        ) if affect_report else None
        _log_model("Affect", output=summary, reasoning=_extract_last_reasoning_text())
    except Exception:
        pass
    log_iteration_to_mlflow(iteration_index, affect_report, executive_summary=None)


def _cdiff(a: str, b: str) -> str:
    out = []
    for ln in difflib.ndiff(a.splitlines(keepends=True), b.splitlines(keepends=True)):
        c, txt = ln[0], ln.rstrip()
        if c == "+":
            out.append(f"[green]{txt}[/green]")
        elif c == "-":
            out.append(f"[red]{txt}[/red]")
        elif c == "?":
            out.append(f"[yellow]{txt}[/yellow]")
    return "\n".join(out)


def _apply_artifact_edit(text: str, edit: ArtifactEdit) -> str:
    """Apply a line-number edit. line=0 appends."""
    lines = text.splitlines()
    if edit.line == 0:
        lines.append(edit.content)
    elif 1 <= edit.line <= len(lines):
        lines[edit.line - 1] = edit.content
    return "\n".join(lines)


def _show_artifact_diff(before: str, after: str, summary: str, n_edits: int) -> None:
    diff = _cdiff(before, after)
    if diff.strip():
        console.print(Panel(diff, title="Artifact Delta", border_style="magenta"))
    if summary:
        console.print(Panel(summary, title=f"Refiner ({n_edits} edit(s))", border_style="cyan"))


def _run_refiner_and_print(*, constraints: str, system_state: SystemState, context: str, artifact: str) -> str:
    pred = run_with_metrics(
        'Refiner',
        refiner,
        constraints=constraints,
        system_state=system_state,
        context=context,
        artifact=artifact,
    )
    edits = pred.edits or []
    summary = pred.summary.strip() if pred.summary else ""

    refined = artifact
    for edit in edits:
        refined = _apply_artifact_edit(refined, edit)

    _show_artifact_diff(artifact, refined, summary, len(edits))
    return refined


async def iteration_loop(*, max_iterations: Optional[int] = None):
    start_mtime = CONSTRAINTS_FILE.stat().st_mtime
    history = []
    iteration_cap = max_iterations if max_iterations is not None else MAX_ITERATIONS
    for i in range(iteration_cap):
        console.rule(f"{_now_str()} · Iteration {i + 1}")

        mlflow_run = None
        if MLFLOW_ENABLED and mlflow is not None:
            mlflow_run = mlflow.start_run(run_name=f"iteration-{i + 1}")

        try:
            artifact, system_state = _read_artifact_and_state()
            constraints, context = _read_constraints_and_context()
            console.print(Panel(context, title=f"Context @ {_now_str()}", border_style="cyan"))

            affect_report = affect_module.run(
                constraints=constraints,
                context=context,
                artifact=artifact,
            )
            _log_affect(affect_report, iteration_index=i + 1)

            memory_task = asyncio.create_task(
                memory_manager_async(
                    constraints=constraints,
                    context=context,
                    artifact=artifact,
                )
            )

            refined = _run_refiner_and_print(
                constraints=constraints,
                system_state=system_state,
                context=context,
                artifact=artifact,
            )

            ARTIFACT_FILE.write_text(refined)
            _save_artifact_history(ARTIFACT_FILE, refined)
            history += [f'Iteration {i + 1}', artifact, constraints, refined]
        finally:
            if mlflow_run is not None:
                mlflow.end_run()

        memory_feedback = await memory_task
        if memory_feedback:
            console.print(Panel(memory_feedback, title=f"Memory @ {_now_str()}", border_style="magenta"))

        current_mtime = CONSTRAINTS_FILE.stat().st_mtime
        if current_mtime != start_mtime:
            console.print(Panel("Constraints changed mid-iteration; restarting loop.", border_style="red"))
            break

        # if is_finished_checker(history=history).is_finished:
        if False:
            finished_check_result = is_finished_checker(history=history)
            print(f"Finished check: {finished_check_result.is_finished} | Reasoning: {finished_check_result.reasoning}\n")
            stop_iterating = finished_check_result.is_finished
        # if finished_check_result.is_finished:
        else:
            stop_iterating = False
        if stop_iterating:
            # print("Artifact finished " + '=' * 50)
            print("Artifact finished after iteration", i + 1, "|" * 50)
            break


HOURLY_INTERVAL = datetime.timedelta(hours=1)
STALE_CONSTRAINTS_AGE = datetime.timedelta(days=3)


async def main_loop():
    last_mtime: Optional[float] = None
    last_run_time: Optional[datetime.datetime] = None
    while True:
        try:
            mtime = CONSTRAINTS_FILE.stat().st_mtime
        except FileNotFoundError:
            console.print(Panel("constraints.md not found; waiting for file to appear.", border_style="red"))
            await asyncio.sleep(5)
            continue

        now = datetime.datetime.now()
        decision = evaluate_run_decision(
            last_mtime=last_mtime,
            last_run_time=last_run_time,
            current_mtime=mtime,
            now=now,
            run_interval=HOURLY_INTERVAL,
            stale_interval=STALE_CONSTRAINTS_AGE,
        )

        if decision.message:
            print(decision.message)

        if decision.should_run:
            last_mtime = decision.next_last_mtime
            last_run_time = decision.next_last_run_time
            scheduled_iteration_cap = 1 if decision.trigger == "scheduled" else None
            await iteration_loop(max_iterations=scheduled_iteration_cap)
        elif decision.is_stale_skip:
            last_mtime = decision.next_last_mtime
            last_run_time = decision.next_last_run_time
        await asyncio.sleep(1)


def log_iteration_to_mlflow(iteration: int, affect_report, executive_summary: Optional[str]) -> None:
    if not MLFLOW_ENABLED or mlflow is None:
        return
    try:
        active_run = mlflow.active_run()
        if active_run is None:
            with mlflow.start_run(run_name=f"iteration-{iteration}"):
                _log_iteration_payload(iteration, affect_report, executive_summary)
        else:
            _log_iteration_payload(iteration, affect_report, executive_summary)
    except Exception as exc:  # pragma: no cover - diagnostic only
        console.print(Panel(f"Failed to log to MLflow: {exc}", border_style="red"))


def _sanitize_metric_name(name: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", name.lower())


def _log_iteration_payload(iteration: int, affect_report, executive_summary: Optional[str]) -> None:
    mlflow.log_metric("iteration", iteration)
    if affect_report:
        if affect_report.urgency:
            mlflow.log_param("affect_urgency", affect_report.urgency)
        if affect_report.emotions:
            mlflow.log_param("affect_emotions", ", ".join(affect_report.emotions))
        if affect_report.goal_scores:
            for goal, score in affect_report.goal_scores.items():
                metric_name = _sanitize_metric_name(f"goal_{goal}")
                mlflow.log_metric(metric_name, int(score), step=iteration)
    if executive_summary:
        mlflow.log_param("executive_summary", executive_summary[:250])


if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        pass
