"""Timewarrior controller module for nlco_iter."""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional

import dspy
from pydantic import BaseModel, Field, ValidationError, model_validator
from rich.console import Console
from rich.panel import Panel

from timewarrior_tools import TimewarriorResult, TimewarriorToolInput, timew_tool


class TimewarriorAction(str, Enum):
    """Enumerated actions for Timewarrior control."""

    START = "start"
    STOP = "stop"
    NONE = "none"


class TimewarriorDecisionModel(BaseModel):
    """Pydantic decision schema enforcing action-specific tag requirements."""

    action: TimewarriorAction = Field(description="Select start, stop, or none.")
    tags: Optional[List[str]] = Field(
        default=None,
        description="Up to three tags to track when action=start; omit otherwise.",
        max_length=3,
    )
    reason: str = Field(
        default="",
        description="Brief explanation for the chosen action.",
    )

    @model_validator(mode="before")
    def coerce_tags(cls, data):
        if isinstance(data, dict):
            tags_value = data.get("tags")
            if isinstance(tags_value, str):
                pieces = [segment.strip() for segment in tags_value.replace("|", ",").split(",")]
                data["tags"] = [p for p in pieces if p]
        return data

    @model_validator(mode="after")
    def validate_tags(cls, data):
        action = data.action
        tags = data.tags or []
        if action is TimewarriorAction.START:
            if not tags:
                raise ValueError("Provide tags when starting tracking.")
            data.tags = tags
        else:
            data.tags = []
        return data


class TimewarriorDecisionSignature(dspy.Signature):
    """Fast action selector for Timewarrior.

    Review the artifact, constraints, and current tracking state. If the existing
    session already fits the upcoming block, choose action ``none``. Start new
    tracking with up to three concise kebab- or snake-case tags when appropriate,
    or stop tracking if the session should end. Always justify the decision.
    """

    artifact: str = dspy.InputField(desc="Current artifact content with schedule and tasks.")
    constraints: str = dspy.InputField(desc="Constraint notes provided by the user.")
    context: str = dspy.InputField(desc="Live context string (datetime, weather, system info) for situational awareness.")
    summary: str = dspy.InputField(desc="Raw output of `timew summary` for reference.")
    is_tracking: bool = dspy.InputField(desc="True if Timewarrior currently tracks any tags.")
    active_tags: list[str] = dspy.InputField(desc="Tags currently being tracked; leave unchanged unless a better set exists.")
    active_summary: str = dspy.InputField(desc="Concise summary of the active session (e.g. start time, total duration).")
    clock: str = dspy.InputField(desc="ISO timestamp for this iteration.")
    decision: TimewarriorDecisionModel = dspy.OutputField(
        desc="Structured decision including action, optional tags, and reason."
    )


@dataclass
class TimewarriorDecision:
    action: TimewarriorAction
    tags: List[str]
    reason: str


class TimewarriorModule(dspy.Module):
    """Fast module that keeps Timewarrior start/stop in sync with the plan."""

    def __init__(
        self,
        fast_lm: dspy.LM,
        *,
        max_tags: int = 3,
        console: Optional[Console] = None,
    ) -> None:
        super().__init__()
        self.fast_lm = fast_lm
        self.max_tags = max_tags
        self.available = True
        self.predictor = dspy.Predict(
            TimewarriorDecisionSignature,
            instructions=(
                "Only start tracking when the available evidence shows the user is actively doing the activity now. "
                "If the plan merely schedules something but there is no confirmation in context or artifact, choose action=none."
            ),
        )
        self.console = console or Console()

    def run(self, *, artifact: str, constraints: str, context: str) -> Optional[str]:
        """Run the time tracking step once and return a status line for logging."""

        if not self.available:
            return None

        summary_result = timew_tool(command=TimewarriorToolInput(command="summary"))
        if summary_result.error:
            self.available = False
            message = f"timew unavailable ({summary_result.error})"
            self.console.print(Panel(message, title="Timewarrior", border_style="red"))
            return message
        if not summary_result.is_success():
            message = f"timew summary error: {summary_result.stderr or summary_result.stdout}"
            self.console.print(Panel(message, title="Timewarrior", border_style="red"))
            return message

        summary_text = summary_result.stdout or summary_result.stderr
        self.console.print(Panel(summary_text, title="timew summary", border_style="blue", expand=False))
        raw_active_tags = self._parse_active_tags(summary_text)
        active_tags = self._normalize_active_tags(raw_active_tags)
        is_tracking = bool(active_tags) or self._detect_tracking(summary_text)
        active_summary = self._summarize(summary_text)

        with dspy.settings.context(lm=self.fast_lm):
            prediction = self.predictor(
                artifact=artifact,
                constraints=constraints,
                context=self._truncate_context(context),
                summary=summary_text,
                is_tracking=is_tracking,
                active_tags=active_tags,
                active_summary=active_summary,
                clock=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            )

        decision = self._decision_from_prediction(prediction)
        if decision is None:
            message = "timew: invalid decision output"
            self.console.print(Panel(message, title="Timewarrior", border_style="red"))
            return message

        message = self._apply_decision(decision, active_tags)
        if message and decision.reason:
            return f"{message} | {decision.reason}"
        return message

    def _apply_decision(
        self,
        decision: TimewarriorDecision,
        active_tags: List[str],
    ) -> Optional[str]:
        action = decision.action

        if action is TimewarriorAction.NONE:
            return None

        if action is TimewarriorAction.START:
            cleaned = self._prepare_tags(decision.tags)
            if not cleaned:
                return "timew: start requested but no valid tags"
            sanitized_active = [self._sanitize_tag(tag) for tag in active_tags]
            sanitized_active = [tag for tag in sanitized_active if tag]
            if sanitized_active and set(cleaned) == set(sanitized_active):
                return "timew: already tracking desired tags"
            result = timew_tool(command=TimewarriorToolInput(command="start", tags=cleaned))
            return self._format_result_message(result)

        if action is TimewarriorAction.STOP:
            if not active_tags:
                return "timew: nothing is currently tracked"
            result = timew_tool(command=TimewarriorToolInput(command="stop"))
            return self._format_result_message(result)

        return f"timew: unsupported action '{action.value}'"

    def _format_result_message(self, result: TimewarriorResult) -> str:
        if result.error:
            self.available = False
            message = f"timew unavailable ({result.error})"
            self.console.print(Panel(message, title="Timewarrior", border_style="red"))
            return message
        if not result.is_success():
            message = f"timew error: {result.stderr or result.stdout}"
            self.console.print(Panel(message, title="Timewarrior", border_style="red"))
            return message
        message = result.stdout or "timew command executed"
        self.console.print(Panel(message, title="Timewarrior", border_style="green", expand=False))
        return message

    def _parse_active_tags(self, summary_text: str) -> List[str]:
        tags_line_prefix = "Tags"
        for line in summary_text.splitlines():
            stripped = line.strip()
            if stripped.startswith(tags_line_prefix):
                parts = stripped[len(tags_line_prefix) :].strip()
                if not parts:
                    return []
                return parts.split()
        return []

    def _normalize_active_tags(self, tags: List[str]) -> List[str]:
        normalized: List[str] = []
        for tag in tags:
            sanitized = self._sanitize_tag(tag)
            if sanitized:
                normalized.append(sanitized)
            else:
                stripped = tag.strip().lower()
                if stripped:
                    normalized.append(stripped)
        return normalized

    def _detect_tracking(self, summary_text: str) -> bool:
        normalized = summary_text.lower()
        if "there is currently no active time tracking" in normalized:
            return False
        return "tracking" in normalized

    def _summarize(self, summary_text: str) -> str:
        lines = [line.strip() for line in summary_text.splitlines() if line.strip()]
        if not lines:
            return "No summary output"

        if "there is currently no active time tracking" in lines[0].lower():
            return lines[0]

        summary_parts: List[str] = [lines[0]]
        for prefix in ("Started", "Total", "Current"):
            match = next((line for line in lines if line.startswith(prefix)), None)
            if match:
                summary_parts.append(match)
        return " | ".join(summary_parts)

    def _decision_from_prediction(self, prediction: Any) -> Optional[TimewarriorDecision]:
        raw = getattr(prediction, "decision", None)
        if raw is None:
            return None

        if isinstance(raw, TimewarriorDecisionModel):
            model = raw
        elif isinstance(raw, dict):
            try:
                model = TimewarriorDecisionModel.model_validate(raw)
            except ValidationError:
                return None
        else:
            try:
                model = TimewarriorDecisionModel.model_validate(raw)
            except ValidationError:
                return None

        return TimewarriorDecision(
            action=model.action,
            tags=model.tags or [],
            reason=model.reason.strip(),
        )

    def _prepare_tags(self, tags: List[str]) -> List[str]:
        cleaned: List[str] = []
        for tag in tags:
            sanitized = self._sanitize_tag(tag)
            if sanitized:
                cleaned.append(sanitized)
            if len(cleaned) >= self.max_tags:
                break
        return cleaned

    def _sanitize_tag(self, tag: str) -> str:
        alnum = []
        for char in tag.strip().lower():
            if char.isalnum() or char in {"-", "_"}:
                alnum.append(char)
            elif char.isspace():
                alnum.append("-")
        sanitized = "".join(alnum).strip("-_")
        return sanitized

    def _truncate_context(self, context: str, limit: int = 4000) -> str:
        if len(context) <= limit:
            return context
        head = context[: limit // 2]
        tail = context[-(limit // 2) :]
        return f"{head}\n...\n{tail}"
