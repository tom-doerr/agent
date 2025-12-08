"""Predict-based memory maintenance module for NLCO."""

from __future__ import annotations

from pathlib import Path
import difflib
from typing import List, Optional

import dspy
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel


class EditBlock(BaseModel):
    """A line-number based edit operation."""
    line: int = Field(description="Line number (1-indexed, 0 to append)")
    content: str = Field(description="New content for this line")


class MemoryModule(dspy.Module):
    """Maintains a persistent markdown memory via search/replace edits."""

    def __init__(
        self,
        lm: dspy.LM,
        *,
        memory_path: Path | str = "memory.md",
        console: Optional[Console] = None,
    ) -> None:
        super().__init__()
        self.lm = lm
        self.memory_path = Path(memory_path)
        self.console = console or Console()

    def run(
        self,
        *,
        artifact: str,
        constraints: str,
        context: str,
    ) -> Optional[str]:
        """Execute a Predict call to update the memory file if needed."""

        initial_memory = self._read_memory()

        class MemoryEditSignature(dspy.Signature):
            """Review memory and context. Output line-number edits to capture durable
            knowledge. Maintain a Hypotheses section with evidence for/against each.
            Edits use 1-indexed line numbers; line=0 appends new content."""

            constraints: str = dspy.InputField()
            artifact: str = dspy.InputField()
            context: str = dspy.InputField()
            memory: str = dspy.InputField()
            edits: List[EditBlock] = dspy.OutputField()
            summary: str = dspy.OutputField()

        predict = dspy.Predict(MemoryEditSignature)

        with dspy.settings.context(lm=self.lm):
            prediction = predict(
                memory=initial_memory,
                artifact=artifact,
                constraints=constraints,
                context=context,
            )

        edits = prediction.edits or []
        if not edits:
            return None

        working = initial_memory
        applied = 0
        for edit in edits:
            working, ok = self._apply_edit(working, edit)
            if ok:
                applied += 1

        if working == initial_memory:
            return None

        full_diff = self._render_diff(initial_memory, working)
        if full_diff.strip():
            self.console.print(Panel(full_diff, title="Memory Delta", border_style="magenta"))

        self._write_memory(working)
        summary = prediction.summary.strip() if prediction.summary else "Memory updated."
        self.console.print(Panel(summary, title=f"Memory ({applied} edit(s))", border_style="cyan"))
        return f"{summary} ({applied} edit(s))"

    # ------------------------------------------------------------------
    # IO helpers
    # ------------------------------------------------------------------
    def _read_memory(self) -> str:
        if not self.memory_path.exists():
            return ""
        return self.memory_path.read_text()

    def _write_memory(self, text: str) -> None:
        self.memory_path.write_text(text)

    def _apply_edit(self, text: str, edit: EditBlock) -> tuple[str, bool]:
        """Apply a line-number edit. line=0 appends."""
        lines = text.splitlines()
        if edit.line == 0:
            self.console.print(Panel(edit.content, title="Appending", border_style="green"))
            lines.append(edit.content)
            return "\n".join(lines), True
        if 1 <= edit.line <= len(lines):
            old = lines[edit.line - 1]
            lines[edit.line - 1] = edit.content
            self.console.print(f"[red]- L{edit.line}: {old}[/red]")
            self.console.print(f"[green]+ L{edit.line}: {edit.content}[/green]")
            return "\n".join(lines), True
        self.console.print(f"[red]Line {edit.line} out of range[/red]")
        return text, False

    # ------------------------------------------------------------------
    # Small helper: render unified diff between texts
    # ------------------------------------------------------------------
    def _render_diff(self, before: str, after: str) -> str:
        a = before.splitlines(keepends=True)
        b = after.splitlines(keepends=True)
        out = []
        for ln in difflib.ndiff(a, b):
            c, txt = ln[0], ln.rstrip()
            if c == "+":
                out.append(f"[green]{txt}[/green]")
            elif c == "-":
                out.append(f"[red]{txt}[/red]")
            elif c == "?":
                out.append(f"[yellow]{txt}[/yellow]")
        return "\n".join(out)
