#!/usr/bin/env python3

import datetime
import time
from pathlib import Path

from pydantic import BaseModel, Field

import dspy
from rich.console import Console
from rich.panel import Panel

from context_provider import create_context_string
from metrics_utils import run_with_metrics
from timewarrior_module import TimewarriorModule
from memory_module import MemoryModule

# Print DSPy version at startup
print(f"DSPy version: {dspy.__version__}")

lm=dspy.LM('deepseek/deepseek-reasoner', max_tokens=40_000)
# lm = dspy.LM( 'ollama_chat/deepseek-r1:8b', api_base='http://localhost:11434', api_key='', temperature=0,  # Critical for structured output max_tokens=2000  # Prevent rambling)
dspy.configure(lm=lm)

timew_lm = dspy.LM('deepseek/deepseek-chat', max_tokens=4_000, temperature=0)
console = Console()
timewarrior_tracker = TimewarriorModule(timew_lm, console=console)
memory_manager = MemoryModule(timew_lm, console=console)


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


def iteration_loop():
    history = []
    search_replace_errors = []
    for i in range(10):
        console.rule(f"Iteration {i + 1}")

        # artifact = ARTIFACT_FILE.read_text().strip()
        artifact = ARTIFACT_FILE.read_text()
        constraints = CONSTRAINTS_FILE.read_text().strip()
        context = create_context_string()
        console.print(Panel(context, title="Context", border_style="cyan"))

        timew_feedback = timewarrior_tracker.run(
            artifact=artifact,
            constraints=constraints,
            context=context,
        )
        if timew_feedback:
            console.print(Panel(timew_feedback, title="Timewarrior", border_style="green"))

        memory_feedback = memory_manager.run(
            artifact=artifact,
            constraints=constraints,
            context=context,
        )
        if memory_feedback:
            console.print(Panel(memory_feedback, title="Memory", border_style="magenta"))

        critique_prediction = run_with_metrics(
            'Critic',
            critic,
            artifact=artifact,
            constraints=constraints,
            context=context,
        )
        critique = critique_prediction.critique
        console.print(Panel(critique, title="Critique", border_style="yellow"))

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
        console.rule("Updated Artifact", style="white")
        console.print(refined)

        ARTIFACT_FILE.write_text(refined)
        history += [f'Iteration {i + 1}', artifact, constraints, critique, refined]

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


if __name__ == "__main__":
    main()
