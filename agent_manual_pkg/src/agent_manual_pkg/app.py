from __future__ import annotations

"""Compatibility shim re-exporting key runtime, memory, and CLI objects."""

from typing import Any

from . import cli, config, memory, runtime, satisfaction, tui

__all__ = sorted(
    set(
        [
            "main",
            "update_config",
            "set_config_path",
            "get_config",
            "get_config_path",
            "load_config",
            "CURRENT_MODEL",
            "LM",
            "MODEL_PRESETS",
            "MODULE_INFO",
            "MODULE_ORDER",
            "SAFETY",
            "SIGNATURE",
            "TOOLS",
            "ReadableReAct",
            "configure_model",
            "configure_memory_model",
            "configure_satisfaction_goals_model",
            "configure_satisfaction_score_model",
            "get_agent",
            "get_module_model",
            "ls",
            "run_shell",
            "MEMORY_MODULE",
            "MemorySlotUpdate",
            "load_memory_slots",
            "save_memory_slots",
            "InstrumentalGoals",
            "SatisfactionResult",
            "GOAL_PLANNER",
            "SATISFACTION_SCORER",
            "build_lm",
            "TUI",
            "Job",
            "HelpScreen",
        ]
    )
)


def __getattr__(name: str) -> Any:  # pragma: no cover - simple delegation
    for module in (runtime, memory, config, cli, satisfaction, tui):
        if hasattr(module, name):
            return getattr(module, name)
    raise AttributeError(f"module 'agent_manual_pkg.app' has no attribute {name!r}")


def __dir__() -> list[str]:  # pragma: no cover
    return sorted(set(__all__ + dir(runtime) + dir(memory) + dir(config) + dir(cli) + dir(tui)))
