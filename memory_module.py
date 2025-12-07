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
    """A single search/replace edit operation."""
    search: str = Field(description="Exact text to find (empty string to append)")
    replace: str = Field(description="Text to replace with")


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
            """Review memory and context. Output search/replace edits to capture durable
            knowledge. Maintain a Hypotheses section with evidence for/against each.
            Do refine the memory and the hythotheses on it every time, don't just output an empty list.
            You only can modify the memory text, you can't edit the constraints or the artitact.
            Do write the hypotheses into the memory text itself.
            Use empty search string to append."""

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
        """Apply a single edit. Empty search means append."""
        if not edit.search:
            sep = "\n\n" if text.strip() else ""
            self.console.print(Panel(edit.replace.strip(), title="Appending", border_style="green"))
            return text + sep + edit.replace.strip() + "\n", True
        if edit.search not in text:
            self.console.print(Panel(edit.search[:80], title="Not found", border_style="red"))
            return text, False
        result = text.replace(edit.search, edit.replace)
        self.console.print(self._render_diff(text, result))
        return result, True

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
