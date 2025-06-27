#!/usr/bin/env python3

import dspy

lm = dspy.configure(lm=dspy.LM('deepseek/deepseek-reasoner', max_tokens=20000))


refiner = dspy.Predict('artifact, constraints, critique -> refined_artifact', instructions="Refine the artifact based on the critique.")
critic = dspy.Predict('artifact, constraints -> critique', instructions="Critique the artifact the critique should be in depth")

CONSTRAINTS_FILE = 'constraints.txt'
ARTIFACT_FILE = 'artifact.txt'

for i in range(10):
    print(f"Iteration {i + 1} " + "=" * 50)
    with open(ARTIFACT_FILE, 'r') as f:
        artifact = f.read().strip()

    with open(CONSTRAINTS_FILE, 'r') as f:
        constraints = f.read().strip()

    # Critique the artifact
    critique = critic(artifact=artifact, constraints=constraints)

    print(f"Critique: {critique}\n")
    # Refine the artifact based on the critique
    refined_artifact = refiner(artifact=artifact, constraints=constraints, critique=critique)

    print(80 * "-")
    print(f"Artifact: {refined_artifact}")

    # Save the refined artifact
    with open(ARTIFACT_FILE, 'w') as f:
        f.write(refined_artifact)


