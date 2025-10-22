"""Executive ReAct module that orchestrates other NLCO components."""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional

import dspy
from pydantic import BaseModel
from rich.console import Console
from rich.panel import Panel

from affect_module import AffectReport


class ExecutiveStepSignature(dspy.Signature):
    constraints: str = dspy.InputField(desc="Active constraints from the user.")
    artifact: str = dspy.InputField(desc="Latest artifact produced by NLCO.")
    context: str = dspy.InputField(desc="Runtime context string (datetime, system status, etc.).")
    affect: str = dspy.InputField(desc="Summary of affect assessment and goal scores.")
    history: str = dspy.InputField(desc="Transcript of prior thoughts/actions/observations.")
    thought: str = dspy.OutputField(desc="Reason about the next step.")
    selected_tool: str = dspy.OutputField(desc="Choose timewarrior_control, memory_update, planning_update, finish, or none.")
    justification: str = dspy.OutputField(desc="Justify the choice.")
    summary: str = dspy.OutputField(desc="Provide a wrap-up when finishing; otherwise leave empty.")


class ExecutiveModule(dspy.Module):
    """Coordinates supporting modules via a ReAct loop."""

    def __init__(
        self,
        lm: dspy.LM,
        *,
        timewarrior_module,
        memory_module,
        planning_module=None,
        console: Optional[Console] = None,
        max_iters: int = 3,
        short_term_path: Path | str = "short_term_memory.md",
    ) -> None:
        super().__init__()
        self.lm = lm
        self.timewarrior_module = timewarrior_module
        self.memory_module = memory_module
        self.planning_module = planning_module
        self.console = console or Console()
        self.max_iters = max_iters
        self._inputs: Dict[str, str] = {}
        self.short_term_path = Path(short_term_path)
        self.tools = self._build_tools()
        self.step_predictor = dspy.Predict(
            ExecutiveStepSignature,
            instructions=(
                "Choose the next helper to invoke. Only start tracking when evidence shows the user is active. "
                "Keep memory and planning concise. Use 'finish' when no further actions are required."
            ),
        )

    def _build_tools(self) -> Dict[str, dspy.Tool]:
        tool_map: Dict[str, Callable[[], Optional[str]]] = {
            "timewarrior_control": lambda: self.timewarrior_module.run(**self._inputs),
            "memory_update": lambda: self.memory_module.run(**self._inputs),
        }

        if self.planning_module is not None:
            tool_map["planning_update"] = lambda: self.planning_module.run(**self._inputs)

        return tool_map

    def run(
        self,
        *,
        artifact: str,
        constraints: str,
        context: str,
        affect_report: Optional[AffectReport] = None,
    ) -> Optional[str]:
        self._inputs = {
            "artifact": artifact,
            "constraints": constraints,
            "context": context,
        }

        history: list[dict[str, str]] = []
        affect_summary = self._format_affect(affect_report)

        for step_idx in range(self.max_iters):
            history_text = self._format_history(history)
            prediction = self._predict_next_step(
                artifact=artifact,
                constraints=constraints,
                context=context,
                affect_summary=affect_summary,
                history_text=history_text,
            )

            step_result = self._execute_step(prediction)
            history.append(step_result.history_entry)

            if step_result.finished:
                return step_result.summary

        return None

    def _format_history(self, history: list[dict[str, str]]) -> str:
        if not history:
            return "(no previous steps)"
        lines = []
        for idx, entry in enumerate(history):
            thought = entry.get("thought", "")
            justification = entry.get("justification", "")
            tool = entry.get("tool", "")
            observation = entry.get("observation", "")
            parts = [f"Step {idx}"]
            if thought:
                parts.append(f"Thought: {thought}")
            if justification:
                parts.append(f"Reason: {justification}")
            parts.append(f"Tool: {tool}")
            parts.append(f"Observation: {observation}")
            lines.append(" | ".join(parts))
        return "\n".join(lines)

    def _append_short_term_event(self, source: str, tool: str, message: str) -> None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        line = f"- [{timestamp}] {source} -> {tool}: {message}\n"
        try:
            with self.short_term_path.open("a", encoding="utf-8") as fh:
                fh.write(line)
        except Exception as exc:
            self.console.print(Panel(f"Failed to write short-term memory: {exc}", border_style="red"))

    def _format_affect(self, report: Optional[AffectReport]) -> str:
        if report is None:
            return "(no affect report)"
        parts: List[str] = []
        if report.emotions:
            parts.append("Emotions: " + ", ".join(report.emotions))
        parts.append(f"Urgency: {report.urgency}")
        parts.append(f"Confidence: {report.confidence}")
        if report.suggested_focus:
            parts.append(f"Suggested focus: {report.suggested_focus}")
        if report.goal_scores:
            goal_bits = ", ".join(f"{goal}={score}" for goal, score in report.goal_scores.items())
            parts.append(f"Goal scores: {goal_bits}")
        if report.rationale:
            parts.append(f"Rationale: {report.rationale}")
        return " | ".join(parts)

    def _predict_next_step(
        self,
        *,
        artifact: str,
        constraints: str,
        context: str,
        affect_summary: str,
        history_text: str,
    ):
        with dspy.settings.context(lm=self.lm):
            return self.step_predictor(
                artifact=artifact,
                constraints=constraints,
                context=context,
                affect=affect_summary,
                history=history_text,
            )

    def _execute_step(self, prediction) -> "StepResult":
        thought = (prediction.thought or "").strip()
        tool_name = (prediction.selected_tool or "").strip().lower()
        justification = (prediction.justification or "").strip()
        summary_text = (prediction.summary or "").strip()

        self.console.rule("Executive Step", style="green")
        if thought:
            self.console.print(f"🤔 {thought}")
        if justification:
            self.console.print(f"➡️  {justification}")

        history_entry = {
            "thought": thought,
            "justification": justification,
            "tool": tool_name or "none",
            "observation": "",
        }

        if tool_name in {"finish", "done", "complete"}:
            summary = summary_text or justification or thought
            return StepResult(finished=True, summary=summary, history_entry=history_entry)

        if not tool_name or tool_name == "none":
            observation_text = "No action taken."
            history_entry["observation"] = observation_text
            self.console.print(Panel(observation_text, border_style="yellow", title="Observation"))
            return StepResult(finished=False, summary=None, history_entry=history_entry)

        if tool_name not in self.tools:
            message = f"Unknown tool `{tool_name}`. Stopping."
            history_entry["observation"] = message
            self.console.print(Panel(message, border_style="red"))
            return StepResult(finished=True, summary=message, history_entry=history_entry)

        observation = self.tools[tool_name]()
        observation_text = observation or "No change."
        history_entry["observation"] = observation_text
        self.console.print(Panel(observation_text, title=f"{tool_name}", border_style="blue"))
        self._append_short_term_event("Executive", tool_name, observation_text)

        summary = summary_text or None
        return StepResult(finished=False, summary=summary, history_entry=history_entry)


class StepResult(BaseModel):
    finished: bool
    summary: Optional[str]
    history_entry: dict
