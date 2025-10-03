"""ReAct-based memory maintenance module for NLCO."""

from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Callable, Dict, List, Literal, Optional

import dspy
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel


class MemoryState(BaseModel):
    """Tracks in-memory edits for the current iteration."""

    original_text: str
    working_text: str
    edits_applied: int = 0
    notes: List[str] = Field(default_factory=list)


class MemoryModule(dspy.Module):
    """Maintains a persistent markdown memory via search/replace edits."""

    def __init__(
        self,
        lm: dspy.LM,
        *,
        memory_path: Path | str = "memory.md",
        max_iters: int = 4,
        console: Optional[Console] = None,
    ) -> None:
        super().__init__()
        self.lm = lm
        self.memory_path = Path(memory_path)
        self.max_iters = max_iters
        self.console = console or Console()

    def run(
        self,
        *,
        artifact: str,
        constraints: str,
        context: str,
    ) -> Optional[str]:
        """Execute a ReAct loop to update the memory file if needed."""

        initial_memory = self._read_memory()
        state = MemoryState(
            original_text=initial_memory,
            working_text=initial_memory,
        )

        tools = self._build_tools(state)

        signature = (
            dspy.Signature(
                {
                    "memory": dspy.InputField(desc="Current memory markdown text."),
                    "artifact": dspy.InputField(desc="Latest artifact produced by NLCO."),
                    "constraints": dspy.InputField(desc="User-provided soft constraints."),
                    "context": dspy.InputField(desc="Runtime context string (datetime, system info, etc.)."),
                },
                instructions=textwrap.dedent(
                    """
                    Review memory, artifact, constraints, and context. Use the provided tools to perform
                    targeted search/replace edits on memory. Only modify memory when doing so captures
                    durable, reusable knowledge (policies, routines, lessons learned). Avoid duplicating
                    transient task details already present in the artifact. Once satisfied, call the
                    `finish` tool (built-in) and summarize the final memory state in one sentence.
                    """
                ).strip(),
            )
            .append("summary", dspy.OutputField(), type_=str)
        )

        react = dspy.ReAct(signature=signature, tools=list(tools.values()), max_iters=self.max_iters)

        with dspy.settings.context(lm=self.lm):
            prediction = react(
                memory=state.original_text,
                artifact=artifact,
                constraints=constraints,
                context=context,
            )

        self._log_trajectory(prediction.trajectory)

        if state.working_text == state.original_text:
            return None

        self._write_memory(state.working_text)
        summary_line = prediction.summary.strip() if prediction.summary else "Memory updated."
        detail = f"{state.edits_applied} edit(s) applied."
        return f"{summary_line} ({detail})"

    # ------------------------------------------------------------------
    # Tool construction
    # ------------------------------------------------------------------
    def _build_tools(self, state: MemoryState) -> Dict[str, dspy.Tool]:
        console = self.console

        def show_memory(section: Literal["full", "head", "tail"] = "full", lines: int = 20) -> str:
            """Return a portion of the working memory for inspection."""

            content = state.working_text.splitlines()
            if not content:
                return "<memory is currently empty>"
            if section == "head":
                snippet = content[:lines]
            elif section == "tail":
                snippet = content[-lines:]
            else:
                snippet = content
            rendered = "\n".join(snippet)
            console.print(Panel(rendered or "<empty>", title=f"show_memory ({section})", border_style="blue", expand=False))
            return rendered

        def replace_block(search: str, replace: str) -> str:
            """Replace occurrences of `search` with `replace` in the working memory."""

            if not search:
                return "Search string is empty; aborting."
            if search not in state.working_text:
                message = f"Search term `{search}` not found."
                console.print(Panel(message, title="replace_memory", border_style="red", expand=False))
                return message

            state.working_text = state.working_text.replace(search, replace)
            state.edits_applied += 1
            state.notes.append(f"Replaced `{search}` -> `{replace}`")
            message = "Replacement applied successfully."
            console.print(Panel(message, title="replace_memory", border_style="green", expand=False))
            return message

        def append_block(content: str) -> str:
            """Append a new markdown block to the end of memory."""

            if not content.strip():
                message = "Provided content is empty; nothing appended."
                console.print(Panel(message, title="append_memory", border_style="red", expand=False))
                return message
            separator = "\n\n" if state.working_text.strip() else ""
            state.working_text += f"{separator}{content.strip()}\n"
            state.edits_applied += 1
            state.notes.append("Appended new block")
            message = "Block appended to memory."
            console.print(Panel(message, title="append_memory", border_style="green", expand=False))
            return message

        def discard_changes() -> str:
            """Reset working memory to its original state."""

            state.working_text = state.original_text
            state.edits_applied = 0
            state.notes.append("Reverted to original memory.")
            message = "Memory reverted to original contents."
            console.print(Panel(message, title="reset_memory", border_style="yellow", expand=False))
            return message

        tool_map: Dict[str, Callable[..., str]] = {
            "show_memory": show_memory,
            "replace_memory": replace_block,
            "append_memory": append_block,
            "reset_memory": discard_changes,
        }

        return {
            name: dspy.Tool(func, name=name, desc=func.__doc__ or "")
            for name, func in tool_map.items()
        }

    # ------------------------------------------------------------------
    # IO helpers
    # ------------------------------------------------------------------
    def _read_memory(self) -> str:
        if not self.memory_path.exists():
            return ""
        return self.memory_path.read_text()

    def _write_memory(self, text: str) -> None:
        self.memory_path.write_text(text)

    def _log_trajectory(self, trajectory: Dict[str, Any]) -> None:
        if not trajectory:
            return
        table = Table(title="Memory ReAct Steps", show_lines=True)
        table.add_column("#", justify="center")
        table.add_column("Thought", overflow="fold")
        table.add_column("Tool", justify="center")
        table.add_column("Args", overflow="fold")
        table.add_column("Observation", overflow="fold")

        idx = 0
        while f"thought_{idx}" in trajectory:
            thought = trajectory.get(f"thought_{idx}", "")
            tool_name = trajectory.get(f"tool_name_{idx}", "")
            tool_args = trajectory.get(f"tool_args_{idx}", {})
            observation = trajectory.get(f"observation_{idx}", "")
            table.add_row(
                str(idx),
                thought,
                tool_name,
                repr(tool_args),
                observation if isinstance(observation, str) else repr(observation),
            )
            idx += 1

        self.console.rule("Memory ReAct Steps", style="magenta")
        idx = 0
        while f"thought_{idx}" in trajectory:
            thought = trajectory.get(f"thought_{idx}", "").strip()
            tool_name = trajectory.get(f"tool_name_{idx}", "")
            tool_args = trajectory.get(f"tool_args_{idx}", {})
            observation = trajectory.get(f"observation_{idx}", "")

            if thought:
                self.console.print(f"[bold]{idx}[/bold] 🤔 {thought}")
            self.console.print(
                f"   🛠️ [cyan]{tool_name}[/cyan] args={tool_args!r}"
            )
            if observation:
                obs_text = observation if isinstance(observation, str) else repr(observation)
                self.console.print(f"   📥 {obs_text}\n")
            idx += 1
