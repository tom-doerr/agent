"""Tool-calling actor with command whitelist."""

from __future__ import annotations

import shlex
import subprocess
from typing import List

import dspy
from pydantic import BaseModel, Field, field_validator

ALLOWED_COMMANDS = frozenset({"ls", "head", "tail"})
MAX_OUTPUT_BYTES = 8192
FORBIDDEN_CHARS = frozenset("|;&`$()\n")


class ToolCommand(BaseModel):
    """A single command to execute."""

    command: str = Field(description="Full shell command, e.g. 'ls -la /tmp'")

    @field_validator("command")
    @classmethod
    def validate_allowed(cls, v: str) -> str:
        parts = v.strip().split()
        if not parts:
            raise ValueError("Empty command")
        binary = parts[0].rsplit("/", 1)[-1]
        if binary not in ALLOWED_COMMANDS:
            raise ValueError(f"Command '{binary}' not allowed")
        return v


def validate_command(raw: str) -> tuple[bool, str]:
    """Validate a command string. Returns (is_valid, error_or_empty)."""
    try:
        parts = shlex.split(raw)
    except ValueError as e:
        return False, f"Failed to parse: {e}"
    if not parts:
        return False, "Empty command"
    binary = parts[0].rsplit("/", 1)[-1]
    if binary not in ALLOWED_COMMANDS:
        return False, f"'{binary}' not in {sorted(ALLOWED_COMMANDS)}"
    for char in FORBIDDEN_CHARS:
        if char in raw:
            return False, f"Forbidden character '{char}'"
    return True, ""


def execute_safe_command(raw: str) -> str:
    """Validate and execute a command. Returns output or error."""
    is_valid, error = validate_command(raw)
    if not is_valid:
        return f"BLOCKED: {error}"
    try:
        parts = shlex.split(raw)
        proc = subprocess.run(
            parts, capture_output=True, text=True, timeout=10,
        )
        out = proc.stdout if proc.returncode == 0 else (proc.stderr or f"exit {proc.returncode}")
        if len(out) > MAX_OUTPUT_BYTES:
            out = out[:MAX_OUTPUT_BYTES] + "\n... (truncated)"
        return out
    except subprocess.TimeoutExpired:
        return "ERROR: Command timed out (10s)"
    except Exception as e:
        return f"ERROR: {e}"


class ToolSignature(dspy.Signature):
    """Generate file system commands to answer the user's request."""

    user_message: str = dspy.InputField(desc="The user's request")
    memory: str = dspy.InputField(desc="Current memory.md contents")
    chat_history: str = dspy.InputField(desc="Prior conversation turns")
    feedback: str = dspy.InputField(desc="Reviewer feedback, or empty")
    commands: List[ToolCommand] = dspy.OutputField(
        desc="Commands to execute. Only ls, head, tail allowed."
    )
    summary: str = dspy.OutputField(desc="Brief explanation of what the commands do")


class ToolResultSignature(dspy.Signature):
    """Summarize command outputs for the user."""

    user_message: str = dspy.InputField(desc="Original user request")
    command_results: str = dspy.InputField(desc="Executed commands and outputs")
    reply: str = dspy.OutputField(desc="User-facing summary of results")


class ToolCallingActor(dspy.Module):
    """Actor that plans commands, executes them safely, and summarizes."""

    def __init__(self) -> None:
        super().__init__()
        self.plan = dspy.Predict(ToolSignature)
        self.summarize = dspy.Predict(ToolResultSignature)

    def forward(
        self,
        *,
        user_message: str,
        memory: str,
        chat_history: str,
        feedback: str = "",
    ) -> dspy.Prediction:
        plan_result = self.plan(
            user_message=user_message,
            memory=memory,
            chat_history=chat_history,
            feedback=feedback,
        )
        results = []
        for cmd in plan_result.commands:
            output = execute_safe_command(cmd.command)
            results.append(f"$ {cmd.command}\n{output}")
        cmd_text = "\n---\n".join(results) if results else "(no commands)"
        summary_result = self.summarize(
            user_message=user_message,
            command_results=cmd_text,
        )
        return dspy.Prediction(
            commands=plan_result.commands,
            command_results=cmd_text,
            reply=summary_result.reply,
            summary=plan_result.summary,
        )
