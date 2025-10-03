"""DSPy tool for interacting with Timewarrior."""

from __future__ import annotations

import subprocess
from typing import Literal

import dspy
from pydantic import BaseModel, Field, model_validator


class TimewarriorToolInput(BaseModel):
    """Structured request for the Timewarrior tool."""

    command: Literal["summary", "start", "stop"] = Field(
        description="Choose which Timewarrior subcommand to execute."
    )
    tags: list[str] | None = Field(
        default=None,
        description="Tags to start tracking (only used when command='start').",
        max_length=5,
    )

    @model_validator(mode="after")
    def validate_tags(self) -> "TimewarriorToolInput":
        if self.command == "start":
            if not self.tags:
                raise ValueError("Provide at least one tag when starting a session.")
        else:
            self.tags = []
        return self


class TimewarriorResult(BaseModel):
    """Structured response returned by the Timewarrior tool."""

    command: str = Field(..., description="Executed shell command.")
    returncode: int = Field(..., description="Exit status (0 indicates success).")
    stdout: str = Field(default="", description="Standard output text.")
    stderr: str = Field(default="", description="Standard error text.")
    error: str | None = Field(default=None, description="Fatal error details, if any.")

    def is_success(self) -> bool:
        return self.error is None and self.returncode == 0

    @model_validator(mode="after")
    def strip_outputs(self) -> "TimewarriorResult":
        self.stdout = self.stdout.strip()
        self.stderr = self.stderr.strip()
        if self.error:
            self.error = self.error.strip()
        return self


def _run_timewarrior(args: list[str]) -> TimewarriorResult:
    command = ["timew", *args]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
        return TimewarriorResult(
            command=" ".join(command),
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )
    except FileNotFoundError:
        return TimewarriorResult(
            command=" ".join(command),
            returncode=127,
            stdout="",
            stderr="",
            error="timew executable not found",
        )


def timew_control(command: TimewarriorToolInput) -> TimewarriorResult:
    """Execute a Timewarrior command (summary/start/stop) with validated arguments."""

    if command.command == "summary":
        return _run_timewarrior(["summary"])
    if command.command == "start":
        return _run_timewarrior(["start", *(command.tags or [])])
    if command.command == "stop":
        return _run_timewarrior(["stop"])

    return TimewarriorResult(
        command=f"timew {command.command}",
        returncode=1,
        stdout="",
        stderr="",
        error=f"Unsupported command: {command.command}",
    )


timew_tool = dspy.Tool(
    timew_control,
    name="timew_control",
    desc="Inspect or control Timewarrior. Choose command='summary', 'start', or 'stop'; provide tags only for 'start'.",
)


TIMEWARRIOR_TOOLS = [timew_tool]
