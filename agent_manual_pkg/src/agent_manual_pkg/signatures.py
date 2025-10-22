from __future__ import annotations

import dspy
from typing import ClassVar


class AgentSignature(dspy.Signature):
    """You are concise. Call tools when useful. Use ls(path) to inspect the filesystem before answering."""

    prompt: str = dspy.InputField(desc="User request or message", prefix="Prompt:")
    answer: str = dspy.OutputField(desc="Concise response", prefix="Answer:")
    instructions: ClassVar[str] = (
        "You are concise. Call tools when useful. Use ls(path) to inspect the filesystem before answering."
    )

