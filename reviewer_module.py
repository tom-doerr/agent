"""Reviewer module that validates proposed Timewarrior actions."""

from __future__ import annotations

from typing import Literal, Optional

import dspy
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel


class ReviewSignature(dspy.Signature):
    artifact: str = dspy.InputField(desc="Current artifact text (tasks and schedule).")
    constraints: str = dspy.InputField(desc="User constraints / notes.")
    context: str = dspy.InputField(desc="Runtime context string (datetime, system info, etc.).")
    summary: str = dspy.InputField(desc="Raw output of `timew summary`.")
    proposed_action: Literal["start", "stop", "none"] = dspy.InputField(desc="Action the planner intends to take.")
    proposed_tags: list[str] = dspy.InputField(desc="Tags that would be used when starting tracking.")
    decision: Literal["allow", "deny"] = dspy.OutputField(desc="Allow or deny the action.")
    explanation: str = dspy.OutputField(desc="Short rationale for the decision.")


class TimewarriorReviewer(dspy.Module):
    """Checks whether a proposed Timewarrior action is justified."""

    def __init__(self, lm: dspy.LM, *, console: Optional[Console] = None) -> None:
        super().__init__()
        self.lm = lm
        self.predictor = dspy.Predict(
            ReviewSignature,
            instructions=(
                "Approve start only if there is direct evidence the user is actively performing the activity now."
                " Approve stop only if tracking is active and there is a good reason to end it. Otherwise deny."
            ),
        )
        self.console = console or Console()

    def run(
        self,
        *,
        artifact: str,
        constraints: str,
        context: str,
        summary: str,
        proposed_action: Literal["start", "stop", "none"],
        proposed_tags: list[str],
    ) -> tuple[bool, str]:
        with dspy.settings.context(lm=self.lm):
            prediction = self.predictor(
                artifact=artifact,
                constraints=constraints,
                context=context,
                summary=summary,
                proposed_action=proposed_action,
                proposed_tags=proposed_tags,
            )

        allow = prediction.decision == "allow"
        explanation = prediction.explanation.strip()
        border = "green" if allow else "red"
        self.console.print(
            Panel(
                f"Decision: {prediction.decision}\nReason: {explanation or 'n/a'}",
                title="Timewarrior Reviewer",
                border_style=border,
            )
        )
        return allow, explanation
