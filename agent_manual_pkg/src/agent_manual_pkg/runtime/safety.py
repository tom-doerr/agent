from __future__ import annotations

import dspy


class SafetyCheck(dspy.Module):
    """Simple token-based shell safety checker."""

    banned = ("rm -rf /", "shutdown", "reboot")

    def assess(self, command: str) -> tuple[bool, str]:
        for token in self.banned:
            if token in command:
                return False, f"blocked token {token!r}"
        return True, "passed"

    def forward(self, command: str) -> bool:
        ok, _ = self.assess(command)
        return ok


SAFETY = SafetyCheck()

