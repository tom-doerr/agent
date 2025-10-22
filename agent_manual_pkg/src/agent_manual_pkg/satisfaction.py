from __future__ import annotations

from typing import Any, ClassVar, List

import dspy
from pydantic import BaseModel, Field, conint, field_validator

def _format_chat_history(history: List[dict[str, str]]) -> str:
    if not history:
        return "No prior messages."
    formatted = []
    for item in history:
        role = item.get("role", "unknown")
        content = (item.get("content") or "").strip()
        formatted.append(f"{role}: {content}")
    return "\n".join(formatted)


def _format_memory(memory_slots: List[str]) -> str:
    if not memory_slots:
        return "No memories."
    return "\n".join(f"[{idx}] {slot}" for idx, slot in enumerate(memory_slots))


class InstrumentalGoals(BaseModel):
    goals: List[str] = Field(default_factory=list, description="Instrumental goals to pursue.")

    @field_validator("goals", mode="before")
    @classmethod
    def ensure_list(cls, value: Any) -> List[str]:
        if isinstance(value, str):
            return _ensure_list(value)
        if isinstance(value, list):
            items: List[str] = []
            for entry in value:
                if isinstance(entry, str) and entry.strip():
                    items.append(entry.strip()[:100])
            return items
        return []


def _ensure_list(value: Any) -> List[str]:
    if isinstance(value, str):
        return [item.strip()[:100] for item in value.splitlines() if item.strip()]
    if isinstance(value, list):
        items: List[str] = []
        for entry in value:
            if isinstance(entry, str) and entry.strip():
                items.append(entry.strip()[:100])
        return items
    return []


class SatisfactionResult(BaseModel):
    score: conint(ge=1, le=9) = Field(description="Satisfaction score from 1 (poor) to 9 (excellent).")
    rationale: str | None = Field(default=None, description="Brief rationale for the score.")

    @field_validator("rationale", mode="before")
    @classmethod
    def clean_rationale(cls, value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text[:200] if text else None


class _GoalsSignature(dspy.Signature):
    """Extract instrumental goals for the latest user request."""

    user_message: str = dspy.InputField(desc="Latest user message.")
    chat_history: str = dspy.InputField(desc="Chronological chat history.")
    memory_slots: str = dspy.InputField(desc="Current memory slots.")
    instrumental_goals: str = dspy.OutputField(desc="Newline separated instrumental goals.")
    instructions: ClassVar[str] = (
        "List concrete instrumental goals the assistant should pursue next. "
        "Return 1-5 short goal statements (<=100 chars each)."
    )


class _ScoreSignature(dspy.Signature):
    """Score how well the goals were achieved."""

    instrumental_goals: str = dspy.InputField(desc="Goals generated earlier.")
    chat_history: str = dspy.InputField(desc="Updated chat history including assistant reply.")
    memory_slots: str = dspy.InputField(desc="Current memory slots.")
    score: str = dspy.OutputField(desc="Satisfaction score 1-9.")
    rationale: str = dspy.OutputField(desc="Short explanation of the score.")
    instructions: ClassVar[str] = (
        "Score goal completion from 1 (poor) to 9 (excellent). Keep rationale under 200 characters."
    )


class GoalPlanner(dspy.Module):
    def forward(
        self,
        *,
        user_message: str,
        chat_history: List[dict[str, str]],
        memory_slots: List[str],
    ) -> InstrumentalGoals:
        from . import runtime  # Local import to avoid circular dependency.

        model_key = runtime.get_module_model("satisfaction_goals")
        lm = runtime.build_lm(model_key)
        predictor = dspy.Predict(_GoalsSignature, lm=lm)
        result = predictor(
            user_message=user_message,
            chat_history=_format_chat_history(chat_history),
            memory_slots=_format_memory(memory_slots),
        )
        return InstrumentalGoals(goals=_ensure_list(result.instrumental_goals))


class SatisfactionScorer(dspy.Module):
    def forward(
        self,
        *,
        instrumental_goals: List[str],
        chat_history: List[dict[str, str]],
        memory_slots: List[str],
    ) -> SatisfactionResult:
        from . import runtime  # Local import to avoid circular dependency.

        model_key = runtime.get_module_model("satisfaction_score")
        lm = runtime.build_lm(model_key)
        predictor = dspy.Predict(_ScoreSignature, lm=lm)
        prediction = predictor(
            instrumental_goals="\n".join(instrumental_goals) if instrumental_goals else "No goals provided.",
            chat_history=_format_chat_history(chat_history),
            memory_slots=_format_memory(memory_slots),
        )
        score = int(str(prediction.score).strip())
        return SatisfactionResult(score=score, rationale=prediction.rationale)


GOAL_PLANNER = GoalPlanner()
SATISFACTION_SCORER = SatisfactionScorer()


__all__ = [
    "InstrumentalGoals",
    "SatisfactionResult",
    "GOAL_PLANNER",
    "SATISFACTION_SCORER",
]
