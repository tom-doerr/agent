"""DSPy actor modules: Interaction and Memory."""

from __future__ import annotations

from typing import List

import dspy
from pydantic import BaseModel, Field

from .state import SystemState


class MemoryEditBlock(BaseModel):
    """A search/replace edit for memory.md."""

    search: str = Field(description="Exact text to find (empty to append)")
    replace: str = Field(description="Replacement text")


class InteractionSignature(dspy.Signature):
    """Generate a helpful reply to the user's message."""

    user_message: str = dspy.InputField(desc="The user's latest message")
    memory: str = dspy.InputField(desc="Current contents of memory.md")
    chat_history: str = dspy.InputField(desc="Prior conversation turns")
    feedback: str = dspy.InputField(desc="Reviewer feedback from previous attempt, or empty")
    reply: str = dspy.OutputField(desc="The reply to send to the user")


class InteractionActor(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(InteractionSignature)

    def forward(self, state: SystemState) -> dspy.Prediction:
        return self.predict(
            user_message=state.user_message,
            memory=state.memory,
            chat_history=state.chat_history,
            feedback=state.feedback,
        )


class MemorySignature(dspy.Signature):
    """Update persistent memory based on the conversation."""

    user_message: str = dspy.InputField(desc="The user's latest message")
    assistant_reply: str = dspy.InputField(desc="The assistant's reply")
    memory: str = dspy.InputField(desc="Current contents of memory.md")
    feedback: str = dspy.InputField(desc="Reviewer feedback, or empty")
    edits: List[MemoryEditBlock] = dspy.OutputField(
        desc="Search/replace edits to apply to memory.md"
    )
    summary: str = dspy.OutputField(desc="Brief summary of changes")


class MemoryActor(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(MemorySignature)

    def forward(self, state: SystemState) -> dspy.Prediction:
        return self.predict(
            user_message=state.user_message,
            assistant_reply=state.assistant_reply or "",
            memory=state.memory,
            feedback=state.feedback,
        )
