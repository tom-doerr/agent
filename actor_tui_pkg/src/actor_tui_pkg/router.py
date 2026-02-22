"""Router module that classifies user input."""

from __future__ import annotations

import dspy


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

    def forward(
        self, *, user_message: str, memory: str, chat_history: str,
    ) -> dspy.Prediction:
        return self.predict(
            user_message=user_message,
            memory=memory,
            chat_history=chat_history,
        )
