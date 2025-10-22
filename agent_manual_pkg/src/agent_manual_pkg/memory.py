from __future__ import annotations

import json
from pathlib import Path
from typing import Any, ClassVar, List, Literal

import dspy
from pydantic import BaseModel, ValidationInfo, field_validator, model_validator

from .config import get_config_path

MAX_SLOT_LENGTH = 100


def memory_path() -> Path:
    return get_config_path().with_name("memory.json")


def load_memory_slots() -> List[str]:
    path = memory_path()
    if path.exists():
        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            data = []
        if isinstance(data, list):
            return [str(item)[:MAX_SLOT_LENGTH] for item in data if isinstance(item, str)]
    return []


def save_memory_slots(slots: List[str]) -> Path:
    clipped = [slot[:MAX_SLOT_LENGTH] for slot in slots]
    path = memory_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clipped, indent=2))
    return path


class MemorySlotUpdate(BaseModel):
    action: Literal["create", "update", "delete"]
    slot: int | None = None
    content: str | None = None

    @field_validator("slot")
    def validate_slot(cls, value: int | None, info: ValidationInfo) -> int | None:
        # Validator ensures slot indices are only required for update/delete operations.
        action = info.data.get("action")
        if action in {"update", "delete"} and (value is None or value < 0):
            raise ValueError("slot must be provided and non-negative for update/delete")
        return value

    @field_validator("content")
    def validate_content(cls, value: str | None, info: ValidationInfo) -> str | None:
        # Validator enforces non-empty content for create/update and clips to MAX_SLOT_LENGTH.
        action = info.data.get("action")
        if action == "delete":
            return None
        if action in {"create", "update"}:
            if value is None or not value.strip():
                raise ValueError("content required")
            return value.strip()[:MAX_SLOT_LENGTH]
        return value

    @model_validator(mode="after")
    def normalize(self) -> "MemorySlotUpdate":
        if self.action == "delete":
            self.content = None
        return self


class MemoryModule(dspy.Module):
    class SummarySignature(dspy.Signature):
        """Summarize tool interactions into memory slot updates."""

        prompt: str = dspy.InputField(desc="Original user message", prefix="Prompt:")
        context: str = dspy.InputField(desc="Recent actions and observations", prefix="Context:")
        updates: str = dspy.OutputField(desc="JSON list of memory slot updates", prefix="Updates:")
        instructions: ClassVar[str] = (
            "Summarize the conversation into memory updates. Respond with JSON array of objects with keys"
            " 'action' ('create'|'update'|'delete'), optional 'slot' (integer), and optional 'content'."
            " Keep each content <= 100 characters."
        )

    def forward(self, prompt: str, steps: List[dict[str, Any]]) -> List[MemorySlotUpdate]:
        if not steps:
            return []
        descriptions: List[str] = []
        for step in steps:
            tool = step.get("tool")
            if tool and tool != "finish":
                args = step.get("args") or {}
                status = ""
                observation = step.get("observation")
                if isinstance(observation, dict):
                    status = observation.get("status", "")
                snippet = f"{tool}: {args} {status}".strip()
            else:
                snippet = (step.get("thought") or "").strip()
            if snippet:
                descriptions.append(snippet)
        history = "\n".join(descriptions)

        from . import runtime  # Local import to avoid circular dependency.

        model_key = runtime.get_module_model("memory")
        lm = runtime.build_lm(model_key)
        predictor = dspy.Predict(self.SummarySignature, lm=lm)

        try:
            result = predictor(prompt=prompt, context=history)
            raw_updates = json.loads(result.updates)
        except Exception:
            fallback = descriptions[-1] if descriptions else prompt
            message = f"{prompt.strip()[:40]} | {fallback[:60]}".strip(" |")
            return [MemorySlotUpdate(action="create", content=message)] if message else []

        processed: List[MemorySlotUpdate] = []
        for item in raw_updates if isinstance(raw_updates, list) else []:
            try:
                processed.append(MemorySlotUpdate(**item))
            except Exception:
                continue
        return processed


MEMORY_MODULE = MemoryModule()
