"""JSONL dataset management for reviewer few-shot examples."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import dspy
from pydantic import BaseModel


class ReviewExample(BaseModel):
    """A single reviewer training example."""

    actor_name: str
    actor_inputs: dict
    actor_output: str
    reasoning: str
    passed: bool


def load_examples(path: Path) -> list[dspy.Example]:
    """Load JSONL as dspy.Example list for LabeledFewShot."""
    if not path.exists():
        return []
    examples = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        data = json.loads(line)
        ex = dspy.Example(
            actor_inputs=json.dumps(data["actor_inputs"]),
            actor_output=data["actor_output"],
            reasoning=data["reasoning"],
            passed=data["passed"],
        ).with_inputs("actor_inputs", "actor_output")
        examples.append(ex)
    return examples


def save_example(path: Path, example: ReviewExample) -> None:
    """Append one example to the JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(example.model_dump()) + "\n")


def list_examples(path: Path) -> list[ReviewExample]:
    """Load all examples as ReviewExample objects for display."""
    if not path.exists():
        return []
    results = []
    for line in path.read_text().splitlines():
        if line.strip():
            results.append(ReviewExample.model_validate_json(line))
    return results


def update_example(
    path: Path,
    index: int,
    reasoning: Optional[str] = None,
    passed: Optional[bool] = None,
) -> None:
    """Update an existing example at a given line index."""
    lines = path.read_text().splitlines()
    if index < 0 or index >= len(lines):
        raise IndexError(f"Review index {index} out of range")
    data = json.loads(lines[index])
    if reasoning is not None:
        data["reasoning"] = reasoning
    if passed is not None:
        data["passed"] = passed
    lines[index] = json.dumps(data)
    path.write_text("\n".join(lines) + "\n")


def delete_example(path: Path, index: int) -> None:
    """Remove an example at a given line index."""
    lines = path.read_text().splitlines()
    if index < 0 or index >= len(lines):
        raise IndexError(f"Review index {index} out of range")
    del lines[index]
    path.write_text("\n".join(lines) + "\n" if lines else "")
