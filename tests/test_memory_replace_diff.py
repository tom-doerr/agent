from __future__ import annotations

from io import StringIO

from rich.console import Console

from memory_module import MemoryModule, MemoryState


def test_replace_prints_unified_diff():
    # Set up a tiny in-memory state and capture console output
    out = StringIO()
    console = Console(file=out, width=120, color_system=None, markup=False)
    mod = MemoryModule(lm=None, console=console)  # lm unused for tool calls in this test

    state = MemoryState(original_text="alpha beta\nsecond line", working_text="alpha beta\nsecond line")
    tools = mod._build_tools(state)
    replace = tools["replace_memory"]

    # Call the tool directly; should print a success message and a unified diff
    replace(search="beta", replace="BETA")

    text = out.getvalue()
    # Diff header and changed line markers should be present
    assert "--- before" in text and "+++ after" in text
    assert "-alpha beta" in text
    assert "+alpha BETA" in text
