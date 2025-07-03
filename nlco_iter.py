#!/usr/bin/env python3

import datetime
import time
from pathlib import Path
from pydantic import BaseModel, Field
import dspy
from context_provider import create_context_string


lm = dspy.configure(lm=dspy.LM('deepseek/deepseek-reasoner', max_tokens=20_000))


class Edit(BaseModel):
    search: str = Field(..., description="Search term to find in the artifact.")
    replace: str = Field(..., description="Replacement text for the search term.")


class RefineSig(dspy.Signature):
    artifact: str = dspy.InputField()
    constraints: str = dspy.InputField()
    critique: str = dspy.InputField()
    context: str = dspy.InputField()
    edits: list[Edit] = dspy.OutputField()

# class Refining(dspySign

# refiner = dspy.Predict('artifact, constraints, critique, context -> refined_artifact', instructions="Refine the artifact based on the critique.")
refiner = dspy.Predict(RefineSig,
                      instructions="Refine the artifact based on the critique and constraints. Return a list of edits with search terms and replacements.")
critic = dspy.Predict('artifact, constraints, context -> critique',
                      instructions="Critique the artifact based on the constraints and common sense.")
is_finished_checker = dspy.Predict('history -> is_finished: bool, reasoning')

CONSTRAINTS_FILE = Path('constraints.md')
ARTIFACT_FILE = Path('artifact.md')


def apply_edits(artifact: str, edits: list[Edit]) -> str:
    """
    Apply a list of edits to the artifact text.
    Each edit contains a search term and a replacement text.
    """
    error_message = ''
    for edit in edits:
        if edit.search not in artifact:
            error_message += f"Search term '{edit.search}' not found in artifact.\n"
            print('error:', error_message)
            continue
        artifact = artifact.replace(edit.search, edit.replace)
    return artifact


def iteration_loop():
    history = []
    for i in range(10):
        print(f"Iteration {i + 1} {'=' * 50}")

        artifact = ARTIFACT_FILE.read_text().strip()
        constraints = CONSTRAINTS_FILE.read_text().strip()
        context = create_context_string()
        print(context)

        critique = critic(artifact=artifact, constraints=constraints, context=context).critique
        print(f"Critique:\n{critique}\n")

        # refined = refiner(artifact=artifact, constraints=constraints, critique=critique, context=context).refined_artifact
        prediction = refiner(artifact=artifact, constraints=constraints, critique=critique, context=context)
        print('edits: ', prediction)
        edits = prediction.edits  # Extract the edits list from the Prediction object
        refined = apply_edits(artifact, edits)
        print('-' * 80)
        print(f"Artifact:\n{refined}")

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

