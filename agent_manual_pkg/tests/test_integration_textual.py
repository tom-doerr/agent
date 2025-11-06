import asyncio
import types
import pytest

from textual.widgets import Input


@pytest.mark.asyncio
async def test_panes_visible_and_layout_toggle(monkeypatch):
    from agent_manual_pkg.tui import TUI

    app = TUI()
    async with app.run_test(headless=True, size=(100, 30)) as pilot:
        # Panes exist
        for sel in ("#satisfaction", "#memory", "#dspy", "#raw", "#log"):
            app.query_one(sel)

        # Switch to stacked, then back to wide
        inp = app.query_one(Input)
        inp.value = "/layout stacked"
        await pilot.press("enter")
        assert "stacked" in app.query_one("#content").classes
        assert "stacked" in app.query_one("#log").classes

        inp.value = "/layout wide"
        await pilot.press("enter")
        assert "stacked" not in app.query_one("#content").classes
        assert "stacked" not in app.query_one("#log").classes


@pytest.mark.asyncio
async def test_submit_message_runs_agent(monkeypatch):
    from agent_manual_pkg import tui as tui_mod
    from agent_manual_pkg.tui import TUI
    from agent_manual_pkg.satisfaction import InstrumentalGoals, SatisfactionResult

    # Stub agent + satisfaction to avoid network/LM calls
    class DummyAgent:
        def __call__(self, *, prompt: str):
            return types.SimpleNamespace(
                steps=[{"thought": "ok", "tool": "finish", "args": {}, "observation": "done"}],
                answer="done",
                raw_history=["PROMPT: done"],
            )

    monkeypatch.setattr(tui_mod.runtime, "get_agent", lambda: DummyAgent())
    monkeypatch.setattr(tui_mod, "MEMORY_MODULE", lambda prompt, steps: [])
    monkeypatch.setattr(tui_mod, "GOAL_PLANNER", lambda **kw: InstrumentalGoals(goals=["x"]))
    monkeypatch.setattr(tui_mod, "SATISFACTION_SCORER", lambda **kw: SatisfactionResult(score=7, rationale="ok"))

    app = TUI()
    async with app.run_test(headless=True, size=(100, 30)) as pilot:
        # Send a normal prompt
        inp = app.query_one(Input)
        inp.value = "hello"
        await pilot.press("enter")

        # Wait for the job to complete
        for _ in range(200):
            if not app.running:
                break
            await asyncio.sleep(0.01)
        assert app.running is False

        # History should include the assistant reply
        assert any(item.get("role") == "assistant" and item.get("content") == "done" for item in app._history)

        # Slash command toggles state
        inp.value = "/modules"
        await pilot.press("enter")
        assert app.awaiting_module_selection is True

