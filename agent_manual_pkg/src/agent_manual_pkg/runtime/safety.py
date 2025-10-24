from __future__ import annotations

import dspy

from typing import ClassVar
from .models import MODEL_PRESETS


class _ShellSafetySignature(dspy.Signature):
    """Decide if a shell command is safe to execute."""

    command: str = dspy.InputField(desc="Shell command to review.")
    decision: str = dspy.OutputField(desc="Return exactly 'allow' or 'block'.")
    reason: str = dspy.OutputField(desc="Brief reason for the decision.")
    instructions: ClassVar[str] = (
        "Review the shell command. Block destructive, exfiltration, persistence, or network abuse. "
        "Return exactly 'allow' or 'block' in decision."
    )


class SafetyCheck(dspy.Module):
    banned = ("rm -rf /", "shutdown", "reboot")

    def assess(self, command: str) -> tuple[bool, str]:
        for token in self.banned:
            if token in command:
                return False, f"blocked token {token!r}"

        preset = MODEL_PRESETS["reasoner"]
        lm = dspy.LM(
            model=preset["slug"],
            max_tokens=min(256, preset["max_tokens"]),
            temperature=0.0,
            **({"reasoning": preset["reasoning"]} if "reasoning" in preset else {}),
        )
        result = dspy.Predict(_ShellSafetySignature, lm=lm)(command=command)
        decision = str(getattr(result, "decision", "")).strip().lower()
        allowed = decision == "allow"
        reason = str(getattr(result, "reason", "")).strip() or decision
        return allowed, reason or ("allow" if allowed else "block")

    def forward(self, command: str) -> bool:
        ok, _ = self.assess(command)
        return ok


SAFETY = SafetyCheck()
