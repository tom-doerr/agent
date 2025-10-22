"""Affect assessment module that emits qualitative emotional states."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import dspy
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel


class AffectReport(BaseModel):
    emotions: list[str] = Field(default_factory=list, description="Primary emotional states (e.g., urgency, confusion).")
    urgency: str = Field(default="low", description="Overall urgency level: low, medium, or high.")
    confidence: str = Field(default="medium", description="Confidence in the assessment.")
    rationale: str = Field(default="", description="Why these emotions/urgency levels apply.")
    suggested_focus: str = Field(default="", description="Recommended focus for next iteration.")
    goal_scores: dict[str, int] = Field(default_factory=dict, description="Instrumental goal scores (0-9).")


class AffectSignature(dspy.Signature):
    constraints: str = dspy.InputField(desc="User-defined constraints and context notes.")
    artifact: str = dspy.InputField(desc="Latest artifact content, including priorities and schedule.")
    context: str = dspy.InputField(desc="Runtime context string (datetime, system info, etc.).")
    memory: str = dspy.InputField(desc="Long-term memory markdown contents.")
    plan: str = dspy.InputField(desc="Persistent planning TOML text.")
    goals: list[str] = dspy.InputField(desc="Instrumental goals to score (e.g., keep schedule updated).")
    emotions: List[str] = dspy.OutputField(desc="List of emotional states relevant right now.")
    urgency: str = dspy.OutputField(desc="Overall urgency level: low, medium, high.")
    confidence: str = dspy.OutputField(desc="Confidence level in this assessment (e.g., low/medium/high).")
    rationale: str = dspy.OutputField(desc="Brief reasoning for the emotions/urgency.")
    suggested_focus: str = dspy.OutputField(desc="Short recommendation for where to focus next.")
    goal_scores: list[int] = dspy.OutputField(desc="Scores (0-9) corresponding to the provided goals list.")


class AffectModule(dspy.Module):
    """Generates a qualitative affect report to color the planning loop."""

    def __init__(
        self,
        lm: dspy.LM,
        *,
        memory_path: Path | str = "memory.md",
        plan_path: Path | str = "plan.toml",
        console: Optional[Console] = None,
    ) -> None:
        super().__init__()
        self.lm = lm
        self.memory_path = Path(memory_path)
        self.plan_path = Path(plan_path)
        self.console = console or Console()
        self.predictor = dspy.Predict(
            AffectSignature,
            instructions=(
                "Summarize the emotional climate around the artifact. Consider whether tasks are overdue, conflicting, "
                "or unclear. Only flag high urgency when evidence shows immediate attention is needed. Use concise "
                "phrasing and keep emotions grounded in the provided texts."
            ),
        )

    def run(self, *, artifact: str, constraints: str, context: str) -> Optional[AffectReport]:
        memory_text = self._safe_read(self.memory_path)
        plan_text = self._safe_read(self.plan_path)

        goals = [
            "Keep schedule updated",
            "Track all tasks in artifact",
            "Schedule quality",
            "Task answer quality",
        ]

        with dspy.settings.context(lm=self.lm):
            prediction = self.predictor(
                artifact=artifact,
                constraints=constraints,
                context=context,
                memory=memory_text,
                plan=plan_text,
                goals=goals,
            )

        report = self._build_report(prediction, goals)
        if report:
            self._render_report(report)
        return report

    def _safe_read(self, path: Path) -> str:
        if not path.exists():
            return ""
        try:
            return path.read_text()
        except Exception as exc:
            self.console.print(Panel(f"Failed to read {path}: {exc}", border_style="red"))
            return ""

    def _build_report(self, prediction, goals: list[str]) -> Optional[AffectReport]:
        if prediction is None:
            return None
        emotions = prediction.emotions if isinstance(prediction.emotions, list) else []
        emotions = [str(e).strip() for e in emotions if str(e).strip()]
        urgency = str(getattr(prediction, "urgency", "")).strip() or "medium"
        confidence = str(getattr(prediction, "confidence", "")).strip() or "medium"
        rationale = str(getattr(prediction, "rationale", "")).strip()
        suggested_focus = str(getattr(prediction, "suggested_focus", "")).strip()
        scores_list = prediction.goal_scores if isinstance(prediction.goal_scores, list) else []
        goal_scores = {}
        for goal, score in zip(goals, scores_list):
            try:
                score_int = max(0, min(9, int(score)))
            except Exception:
                score_int = 0
            goal_scores[goal] = score_int
        try:
            return AffectReport(
                emotions=emotions,
                urgency=urgency,
                confidence=confidence,
                rationale=rationale,
                suggested_focus=suggested_focus,
                goal_scores=goal_scores,
            )
        except Exception:
            return None

    def _render_report(self, report: AffectReport) -> None:
        emotions = ", ".join(report.emotions) if report.emotions else "neutral"
        body = (
            f"[bold]Emotions:[/bold] {emotions}\n"
            f"[bold]Urgency:[/bold] {report.urgency}\n"
            f"[bold]Confidence:[/bold] {report.confidence}\n"
            f"[bold]Suggested focus:[/bold] {report.suggested_focus or 'None'}\n"
            f"[bold]Rationale:[/bold] {report.rationale or 'n/a'}\n"
            f"[bold]Goal scores:[/bold] {report.goal_scores}"
        )
        self.console.print(Panel(body, title="Affect Assessment", border_style="magenta"))
