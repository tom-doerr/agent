from __future__ import annotations

import os
import subprocess
from typing import Any, Dict

import dspy

from .safety import SAFETY


def ls(path: str = ".") -> str:
    entries = []
    for name in sorted(os.listdir(path)):
        full = os.path.join(path, name)
        entries.append(name + ("/" if os.path.isdir(full) else ""))
    return "\n".join(entries)


def run_shell(command: str) -> Dict[str, Any]:
    safe, detail = SAFETY.assess(command)
    if not safe:
        return {
            "status": "blocked",
            "command": command,
            "output": "command blocked",
            "safety": {"passed": False, "detail": detail},
        }
    proc = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = proc.stdout if proc.returncode == 0 else proc.stderr or f"exit {proc.returncode}"
    return {
        "status": "ok" if proc.returncode == 0 else f"error({proc.returncode})",
        "command": command,
        "output": output.strip(),
        "safety": {"passed": True, "detail": detail},
    }


def send_message(message: str) -> str:
    """Return a message that the agent can relay directly to the user."""
    return message


TOOLS = [
    dspy.Tool(ls, name="ls", desc="List directory entries.", args={"path": "Directory to list (default '.')"}),
    dspy.Tool(run_shell, name="run_shell", desc="Execute a shell command after safety review.", args={"command": "Command to execute"}),
    dspy.Tool(send_message, name="send_message", desc="Reply directly to the user.", args={"message": "Message text"}),
]
