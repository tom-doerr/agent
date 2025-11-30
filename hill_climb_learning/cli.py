#!/usr/bin/env python
"""Hill climb learning CLI with Rich interface."""
import argparse
import difflib
import json
from pathlib import Path

import dspy
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.text import Text

from modules import TextModifier, TextEvaluator, EvaluateText

EXAMPLES_FILE = Path(__file__).parent / "examples.jsonl"
console = Console()


def load_examples() -> list[dspy.Example]:
    """Load few-shot examples from JSONL file."""
    if not EXAMPLES_FILE.exists():
        return []
    examples = []
    for line in EXAMPLES_FILE.read_text().splitlines():
        if line.strip():
            data = json.loads(line)
            ex = dspy.Example(**data).with_inputs("original", "modified")
            examples.append(ex)
    return examples


def save_example(original: str, modified: str, is_better: bool) -> None:
    """Append a new example to the JSONL file."""
    data = {"original": original, "modified": modified, "is_better": is_better}
    with EXAMPLES_FILE.open("a") as f:
        f.write(json.dumps(data) + "\n")


def show_diff(original: str, modified: str) -> None:
    """Display diff with red for removed, green for added."""
    diff = Text()
    matcher = difflib.SequenceMatcher(None, original, modified)
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == "equal":
            diff.append(original[i1:i2])
        elif op == "delete":
            diff.append(original[i1:i2], style="red strike")
        elif op == "insert":
            diff.append(modified[j1:j2], style="green bold")
        elif op == "replace":
            diff.append(original[i1:i2], style="red strike")
            diff.append(modified[j1:j2], style="green bold")
    console.print(Panel(diff, title="Diff", border_style="magenta"))


def build_evaluator(examples: list[dspy.Example]) -> TextEvaluator:
    """Build evaluator with few-shot examples using LabeledFewShot."""
    evaluator = TextEvaluator()
    if examples:
        optimizer = dspy.LabeledFewShot(k=64)
        evaluator = optimizer.compile(evaluator, trainset=examples)
    return evaluator


def hill_climb(initial_text: str) -> str:
    """Run the hill climb loop until evaluator predicts improvement."""
    modifier = TextModifier()
    examples = load_examples()
    current = initial_text
    iteration = 0

    while True:
        iteration += 1
        console.print(f"\n[bold blue]Iteration {iteration}[/bold blue]")
        console.print(Panel(current, title="Current Text", border_style="cyan"))

        # Generate modification
        result = modifier(original=current)
        modified = result.modified
        console.print(Panel(modified, title="Modified Text", border_style="yellow"))
        show_diff(current, modified)

        # Evaluator prediction
        evaluator = build_evaluator(examples)
        eval_result = evaluator(original=current, modified=modified)
        predicted = eval_result.is_better
        console.print(f"Evaluator predicts: [bold]{'Better' if predicted else 'Worse'}[/bold]")

        # Human feedback
        is_better = Confirm.ask("Is the modified text better?")
        save_example(current, modified, is_better)
        examples = load_examples()  # Reload with new example

        if is_better:
            console.print("[bold green]Accepted improvement![/bold green]")
            current = modified
        else:
            console.print("[dim]Rejected, trying again...[/dim]")


def main():
    parser = argparse.ArgumentParser(description="Hill climb text improvement")
    parser.add_argument("text", help="Initial text to improve")
    args = parser.parse_args()

    lm = dspy.LM("deepseek/deepseek-reasoner")
    dspy.configure(lm=lm)

    result = hill_climb(args.text)
    console.print(Panel(result, title="Final Result", border_style="green"))


if __name__ == "__main__":
    main()
