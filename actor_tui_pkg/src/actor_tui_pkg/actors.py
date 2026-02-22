"""DSPy actor modules: Interaction and Memory."""

from __future__ import annotations

from typing import List

import dspy
from pydantic import BaseModel, Field


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

    def forward(
        self,
        *,
        user_message: str,
        memory: str,
        chat_history: str,
        feedback: str = "",
    ) -> dspy.Prediction:
        return self.predict(
            user_message=user_message,
            memory=memory,
            chat_history=chat_history,
            feedback=feedback,
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

    def forward(
        self,
        *,
        user_message: str,
        assistant_reply: str,
        memory: str,
        feedback: str = "",
    ) -> dspy.Prediction:
        return self.predict(
            user_message=user_message,
            assistant_reply=assistant_reply,
            memory=memory,
            feedback=feedback,
        )
