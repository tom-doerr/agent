"""Reviewer module with few-shot compilation."""

from __future__ import annotations

from pathlib import Path

import dspy
from pydantic import BaseModel

from .dataset import load_examples


class ReviewResult(BaseModel):
    """Structured result from a review."""

    reasoning: str
    passed: bool
    actor_inputs: dict
    actor_output: str


class ReviewSignature(dspy.Signature):
    """Review an actor's output. Reason first, then decide."""

    actor_inputs: str = dspy.InputField(desc="JSON-encoded inputs the actor received")
    actor_output: str = dspy.InputField(desc="The output the actor produced")
    reasoning: str = dspy.OutputField(desc="Chain-of-thought about output quality")
    passed: bool = dspy.OutputField(desc="True if acceptable, False to retry")


class Reviewer(dspy.Module):
    """Generic reviewer compiled with few-shot examples."""

    def __init__(self, name: str = "reviewer") -> None:
        super().__init__()
        self.name = name
        self.predict = dspy.Predict(ReviewSignature)

    def forward(self, *, actor_inputs: str, actor_output: str) -> dspy.Prediction:
        return self.predict(actor_inputs=actor_inputs, actor_output=actor_output)


def build_reviewer(name: str, dataset_path: Path) -> Reviewer:
    """Build a reviewer, optionally compiled with few-shot examples."""
    reviewer = Reviewer(name=name)
    examples = load_examples(dataset_path)
    if examples:
        optimizer = dspy.LabeledFewShot(k=64)
        reviewer = optimizer.compile(reviewer, trainset=examples)
    return reviewer
