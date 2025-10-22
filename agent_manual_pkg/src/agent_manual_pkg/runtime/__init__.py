from __future__ import annotations

from typing import Any

from . import configuration as _configuration
from .agent import ReadableReAct
from .models import MODEL_PRESETS, MODULE_INFO, MODULE_ORDER
from .safety import SAFETY, SafetyCheck
from .tools import TOOLS, ls, run_shell, send_message
from ..signatures import AgentSignature

SIGNATURE = AgentSignature

build_lm = _configuration.build_lm
configure_model = _configuration.configure_model
configure_memory_model = _configuration.configure_memory_model
configure_satisfaction_goals_model = _configuration.configure_satisfaction_goals_model
configure_satisfaction_score_model = _configuration.configure_satisfaction_score_model
get_module_model = _configuration.get_module_model

__all__ = [
    "AGENT",
    "CURRENT_MODEL",
    "LM",
    "MODEL_PRESETS",
    "MODULE_INFO",
    "MODULE_ORDER",
    "ReadableReAct",
    "SAFETY",
    "SafetyCheck",
    "SIGNATURE",
    "TOOLS",
    "build_lm",
    "configure_memory_model",
    "configure_model",
    "configure_satisfaction_goals_model",
    "configure_satisfaction_score_model",
    "get_module_model",
    "ls",
    "run_shell",
    "send_message",
]


def __getattr__(name: str) -> Any:  # pragma: no cover - simple delegation
    if name in {"AGENT", "CURRENT_MODEL", "LM"}:
        return getattr(_configuration, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:  # pragma: no cover
    return sorted(set(__all__ + [*dir(_configuration)]))
