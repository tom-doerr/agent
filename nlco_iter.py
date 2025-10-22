#!/usr/bin/env python3

import asyncio
import datetime
from pathlib import Path
import re
from typing import Optional

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
from metrics_utils import run_with_metrics
from timewarrior_module import TimewarriorModule
from memory_module import MemoryModule
from executive_module import ExecutiveModule
from planning_module import PlanningModule
from affect_module import AffectModule
from nlco_scheduler import evaluate_run_decision
from refiner_signature import RefineSignature, normalize_schedule, schedule_to_json, render_schedule_timeline

# Print DSPy version at startup
print(f"DSPy version: {dspy.__version__}")

lm=dspy.LM('deepseek/deepseek-reasoner', max_tokens=40_000)
# lm = dspy.LM( 'ollama_chat/deepseek-r1:8b', api_base='http://localhost:11434', api_key='', temperature=0,  # Critical for structured output max_tokens=2000  # Prevent rambling)
dspy.configure(lm=lm)

support_lm = dspy.LM('deepseek/deepseek-chat', max_tokens=4_000, temperature=0)
console = Console()
short_term_path = Path("short_term_memory.md")
timewarrior_tracker = TimewarriorModule(support_lm, console=console, short_term_path=short_term_path)
memory_manager = MemoryModule(support_lm, console=console)
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


class Edit(BaseModel):
    search: str = Field(..., description="Search term to find in the artifact.")
    replace: str = Field(..., description="Replacement text for the search term.")


refiner = dspy.Predict(
    RefineSignature,
    instructions=(
        "Refine the artifact based on the critique while keeping the full schedule written in the artifact text. "
        "Populate structured_schedule with a well-formed list of ScheduleBlock entries that exactly mirrors the schedule in the refined artifact."
    ),
)
critic = dspy.Predict('constraints, artifact, context -> critique',
                      instructions="Critique the artifact based on the constraints and common sense.")
is_finished_checker = dspy.Predict('history -> is_finished: bool, reasoning')

CONSTRAINTS_FILE = Path('constraints.md')
ARTIFACT_FILE = Path('artifact.md')
STRUCTURED_SCHEDULE_FILE = Path('structured_schedule.json')

MAX_ITERATIONS = 3


def _now_str() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


async def iteration_loop(*, max_iterations: Optional[int] = None):
    start_mtime = CONSTRAINTS_FILE.stat().st_mtime
    history = []
    search_replace_errors = []
    iteration_cap = max_iterations if max_iterations is not None else MAX_ITERATIONS
    for i in range(iteration_cap):
        console.rule(f"{_now_str()} · Iteration {i + 1}")

        mlflow_run = None
        if MLFLOW_ENABLED and mlflow is not None:
            mlflow_run = mlflow.start_run(run_name=f"iteration-{i + 1}")

        try:
            artifact = ARTIFACT_FILE.read_text()
            constraints = CONSTRAINTS_FILE.read_text().strip()
            context = create_context_string()
            console.print(Panel(context, title=f"Context @ {_now_str()}", border_style="cyan"))

            affect_report = affect_module.run(
                constraints=constraints,
                context=context,
                artifact=artifact,
            )

            log_iteration_to_mlflow(i + 1, affect_report, executive_summary=None)

            memory_task = asyncio.create_task(
                memory_manager_async(
                    constraints=constraints,
                    context=context,
                    artifact=artifact,
                )
            )

            critique_prediction = run_with_metrics(
                'Critic',
                critic,
                constraints=constraints,
                context=context,
                artifact=artifact,
            )
            critique = critique_prediction.critique
            console.print(Panel(critique, title=f"Critique @ {_now_str()}", border_style="yellow"))

            refined_prediction = run_with_metrics(
                'Refiner',
                refiner,
                constraints=constraints,
                critique=critique,
                context=context,
                artifact=artifact,
            )
            refined = refined_prediction.refined_artifact
            try:
                schedule_blocks = normalize_schedule(getattr(refined_prediction, "structured_schedule", []))
            except ValueError as schedule_error:
                console.print(
                    Panel(
                        f"Structured schedule output was invalid: {schedule_error}",
                        title=f"Structured Schedule @ {_now_str()}",
                        border_style="red",
                    )
                )
                schedule_blocks = []
            schedule_json = schedule_to_json(schedule_blocks)
            STRUCTURED_SCHEDULE_FILE.write_text(schedule_json + "\n")
            if schedule_blocks:
                console.print(
                    Panel(
                        render_schedule_timeline(schedule_blocks),
                        title=f"Schedule Timeline @ {_now_str()}",
                        border_style="green",
                    )
                )
                console.print(
                    Panel(
                        schedule_json,
                        title=f"Structured Schedule @ {_now_str()}",
                        border_style="green",
                    )
                )
            # prediction = refiner(artifact=artifact, constraints=constraints, critique=critique, search_replace_errors=search_replace_errors, context=context)
            # print('edits: ', prediction)
            # edits = prediction.edits  # Extract the edits list from the Prediction object
            # refined, search_replace_errors = editing_utils.apply_edits(artifact, edits)
            console.rule(f"{_now_str()} · Updated Artifact", style="white")
            console.print(refined)

            ARTIFACT_FILE.write_text(refined)
            history += [f'Iteration {i + 1}', artifact, constraints, critique, refined]
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
