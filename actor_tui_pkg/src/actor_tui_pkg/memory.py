"""Memory file management with search/replace edits."""

from __future__ import annotations

import difflib
from pathlib import Path
from typing import List, Tuple

from .actors import MemoryEditBlock


class MemoryManager:
    def __init__(self, path: Path) -> None:
        self.path = path

    def read(self) -> str:
        if not self.path.exists():
            return ""
        return self.path.read_text()

    def apply_edits(self, edits: List[MemoryEditBlock]) -> Tuple[str, str]:
        """Apply search/replace edits. Returns (new_content, diff_text)."""
        original = self.read()
        working = original
        for edit in edits:
            if edit.search == "":
                working = working.rstrip("\n") + "\n" + edit.replace + "\n"
            elif edit.search in working:
                working = working.replace(edit.search, edit.replace, 1)
        if working != original:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(working)
        return working, self._render_diff(original, working)

    @staticmethod
    def _render_diff(before: str, after: str) -> str:
        """Render diff between texts."""
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
