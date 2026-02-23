"""Router module that classifies user input."""

from __future__ import annotations

import dspy

from .state import SystemState


class RouterSignature(dspy.Signature):
    """Decide whether input needs file access or a conversational reply."""

    user_message: str = dspy.InputField(desc="The user's latest message")
    memory: str = dspy.InputField(desc="Current memory.md contents")
    chat_history: str = dspy.InputField(desc="Prior conversation turns")
    reasoning: str = dspy.OutputField(desc="Brief reason for routing decision")
    route: str = dspy.OutputField(
        desc="Exactly 'interaction' or 'tool'."
    )


class Router(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(RouterSignature)

    def forward(self, state: SystemState) -> dspy.Prediction:
        return self.predict(
            user_message=state.user_message,
            memory=state.memory,
            chat_history=state.chat_history,
        )
