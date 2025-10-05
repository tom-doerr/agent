#!/usr/bin/env python3

import datetime
import time
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


class RefineSig(dspy.Signature):
    artifact: str = dspy.InputField()
    constraints: str = dspy.InputField()
    critique: str = dspy.InputField()
    search_replace_errors: list[Edit] = dspy.InputField(desc="Search and replace errors from previous iterations that couldn't be applied because the search block didn't match any part in the artifact")
    context: str = dspy.InputField()
    edits: list[Edit] = dspy.OutputField()

# class Refining(dspySign

refiner = dspy.Predict('artifact, constraints, critique, context -> refined_artifact', instructions="Refine the artifact based on the critique.")
# refiner = dspy.Predict(RefineSig, instructions="Refine the artifact based on the critique and constraints. Return a list of edits with search terms and replacements.")
critic = dspy.Predict('artifact, constraints, context -> critique',
                      instructions="Critique the artifact based on the constraints and common sense.")
is_finished_checker = dspy.Predict('history -> is_finished: bool, reasoning')

CONSTRAINTS_FILE = Path('constraints.md')
ARTIFACT_FILE = Path('artifact.md')


def _now_str() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def iteration_loop():
    history = []
    search_replace_errors = []
    for i in range(10):
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
                artifact=artifact,
                constraints=constraints,
                context=context,
            )

            log_iteration_to_mlflow(i + 1, affect_report, executive_summary=None)

            memory_feedback = memory_manager.run(
                artifact=artifact,
                constraints=constraints,
                context=context,
            )
            if memory_feedback:
                console.print(Panel(memory_feedback, title=f"Memory @ {_now_str()}", border_style="magenta"))

            critique_prediction = run_with_metrics(
                'Critic',
                critic,
                artifact=artifact,
                constraints=constraints,
                context=context,
            )
            critique = critique_prediction.critique
            console.print(Panel(critique, title=f"Critique @ {_now_str()}", border_style="yellow"))

            refined_prediction = run_with_metrics(
                'Refiner',
                refiner,
                artifact=artifact,
                constraints=constraints,
                critique=critique,
                context=context,
            )
            refined = refined_prediction.refined_artifact
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


def main():
    last_mtime = None
    while True:
        mtime = CONSTRAINTS_FILE.stat().st_mtime
        if mtime != last_mtime:
            print(f"Constraints changed at {datetime.datetime.fromtimestamp(mtime)}. Running iterations…")
            last_mtime = mtime
            iteration_loop()
        time.sleep(1)            # don’t spin-lock the CPU


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
    main()
