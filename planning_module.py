"""Planning module that maintains a TOML plan via DSPy ReAct."""

from __future__ import annotations

import textwrap
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Literal, Optional

import dspy
import toml
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel


class PlanningState(BaseModel):
    original_plan: Dict[str, Any]
    working_plan: Dict[str, Any]
    edits_applied: int = 0
    notes: list[str] = Field(default_factory=list)


class PlanningModule(dspy.Module):
    """Uses a ReAct loop to keep `plan.toml` aligned with long-term goals."""

    def __init__(
        self,
        lm: dspy.LM,
        *,
        plan_path: Path | str = "plan.toml",
        max_iters: int = 4,
        console: Optional[Console] = None,
    ) -> None:
        super().__init__()
        self.lm = lm
        self.plan_path = Path(plan_path)
        self.max_iters = max_iters
        self.console = console or Console()

    def run(self, *, artifact: str, constraints: str, context: str) -> Optional[str]:
        plan_dict = self._read_plan()
        state = PlanningState(original_plan=plan_dict, working_plan=deepcopy(plan_dict))

        tools = self._build_tools(state)
        signature = (
            dspy.Signature(
                {
                    "constraints": dspy.InputField(desc="User constraints to respect."),
                    "plan": dspy.InputField(desc="Current planning TOML contents."),
                    "artifact": dspy.InputField(desc="Latest artifact (schedule, tasks, etc.)."),
                    "context": dspy.InputField(desc="Runtime context string."),
                },
                instructions=textwrap.dedent(
                    """
                    Maintain a concise planning TOML. Only record durable objectives, sub-goals, and parameters that
                    help future iterations. Avoid copying transient tasks already present in the artifact. Use the
                    available tools to inspect or edit sections, then call `finish` once no further adjustments are
                    needed. Prefer incremental updates over wholesale rewrites.
                    """
                ).strip(),
            )
            .append("summary", dspy.OutputField(), type_=str)
        )

        agent = dspy.ReAct(signature=signature, tools=list(tools.values()), max_iters=self.max_iters)

        with dspy.settings.context(lm=self.lm):
            prediction = agent(
                plan=self._dump_plan(plan_dict),
                artifact=artifact,
                constraints=constraints,
                context=context,
            )

        self._log_trajectory(prediction.trajectory)

        if state.working_plan == state.original_plan:
            return None

        self._write_plan(state.working_plan)
        summary = prediction.summary.strip() if prediction.summary else "Planning updated."
        detail = f"{state.edits_applied} change(s)."
        return f"{summary} ({detail})"

    # ------------------------------------------------------------------
    # Tool construction
    # ------------------------------------------------------------------
    def _build_tools(self, state: PlanningState) -> Dict[str, dspy.Tool]:
        console = self.console

        def show_plan(path: str = "") -> str:
            section = self._resolve_path(state.working_plan, path)
            rendered = toml.dumps(section) if isinstance(section, dict) else str(section)
            title = f"show_plan({path or 'root'})"
            console.print(Panel(rendered or "<empty>", title=title, border_style="blue", expand=False))
            return rendered

        def set_value(path: str, value: str, value_type: Literal["str", "int", "float", "bool"] = "str") -> str:
            if not path:
                return "Path cannot be empty."
            converted = self._convert_value(value, value_type)
            parent, key = self._ensure_parent(state.working_plan, path)
            parent[key] = converted
            state.edits_applied += 1
            state.notes.append(f"set {path} -> {converted!r}")
            message = f"Set {path} = {converted!r}"
            console.print(Panel(message, title="set_plan", border_style="green", expand=False))
            return message

        def remove_key(path: str) -> str:
            if not path:
                return "Path cannot be empty."
            parent, key = self._resolve_parent(state.working_plan, path)
            if parent is None or key not in parent:
                message = f"Path `{path}` not found."
                console.print(Panel(message, title="remove_plan", border_style="red", expand=False))
                return message
            del parent[key]
            state.edits_applied += 1
            state.notes.append(f"removed {path}")
            message = f"Removed `{path}`."
            console.print(Panel(message, title="remove_plan", border_style="yellow", expand=False))
            return message

        def reset_plan() -> str:
            state.working_plan = deepcopy(state.original_plan)
            state.edits_applied = 0
            state.notes.append("Plan reverted to original.")
            message = "Plan reverted to original contents."
            console.print(Panel(message, title="reset_plan", border_style="yellow", expand=False))
            return message

        return {
            "show_plan": dspy.Tool(show_plan, name="show_plan", desc=show_plan.__doc__ or ""),
            "set_plan": dspy.Tool(set_value, name="set_plan", desc=set_value.__doc__ or ""),
            "remove_plan": dspy.Tool(remove_key, name="remove_plan", desc=remove_key.__doc__ or ""),
            "reset_plan": dspy.Tool(reset_plan, name="reset_plan", desc=reset_plan.__doc__ or ""),
        }

    # ------------------------------------------------------------------
    # IO helpers
    # ------------------------------------------------------------------
    def _read_plan(self) -> Dict[str, Any]:
        if not self.plan_path.exists():
            return {}
        text = self.plan_path.read_text()
        try:
            return toml.loads(text) if text.strip() else {}
        except toml.TomlDecodeError:
            self.console.print(Panel("plan.toml is invalid; starting from empty.", border_style="red"))
            return {}

    def _write_plan(self, plan: Dict[str, Any]) -> None:
        self.plan_path.write_text(toml.dumps(plan))

    def _dump_plan(self, plan: Dict[str, Any]) -> str:
        return toml.dumps(plan) if plan else ""

    # ------------------------------------------------------------------
    # Trajectory logging and utilities
    # ------------------------------------------------------------------
    def _log_trajectory(self, trajectory: Dict[str, Any]) -> None:
        if not trajectory:
            return
        self.console.rule("Planning ReAct Steps", style="cyan")
        idx = 0
        while f"thought_{idx}" in trajectory:
            thought = trajectory.get(f"thought_{idx}", "").strip()
            tool_name = trajectory.get(f"tool_name_{idx}", "")
            tool_args = trajectory.get(f"tool_args_{idx}", {})
            observation = trajectory.get(f"observation_{idx}", "")

            if thought:
                self.console.print(f"[bold]{idx}[/bold] 🤔 {thought}")
            if tool_name:
                self.console.print(f"   🔧 [cyan]{tool_name}[/cyan] args={tool_args!r}")
            if observation:
                obs = observation if isinstance(observation, str) else repr(observation)
                self.console.print(Panel(obs, title="Observation", border_style="blue", expand=False))
            idx += 1

    def _convert_value(self, value: str, value_type: Literal["str", "int", "float", "bool"]) -> Any:
        converters = {
            "str": lambda v: v,
            "int": lambda v: int(v),
            "float": lambda v: float(v),
            "bool": lambda v: v.lower() in {"true", "1", "yes", "y"},
        }
        try:
            return converters[value_type](value)
        except Exception as exc:
            raise ValueError(f"Unable to convert `{value}` to {value_type}: {exc}") from exc

    def _resolve_path(self, plan: Dict[str, Any], path: str) -> Any:
        if not path:
            return plan
        node: Any = plan
        for part in path.split('.'):
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                return f"<path `{path}` not found>"
        return node

    def _resolve_parent(self, plan: Dict[str, Any], path: str) -> tuple[Optional[Dict[str, Any]], str]:
        parts = path.split('.')
        key = parts[-1]
        parent = plan
        for part in parts[:-1]:
            if part not in parent or not isinstance(parent[part], dict):
                return None, key
            parent = parent[part]
        return parent, key

    def _ensure_parent(self, plan: Dict[str, Any], path: str) -> tuple[Dict[str, Any], str]:
        parts = path.split('.')
        key = parts[-1]
        parent = plan
        for part in parts[:-1]:
            if part not in parent or not isinstance(parent[part], dict):
                parent[part] = {}
            parent = parent[part]
        return parent, key
