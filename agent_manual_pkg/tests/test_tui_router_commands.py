from __future__ import annotations

from types import SimpleNamespace
import types

import pytest

import sys
sys.path.insert(0, 'agent_manual_pkg/src')
from agent_manual_pkg.tui import TUI  # type: ignore
from agent_manual_pkg.tui import runtime  # type: ignore


class StubLogNode:
    def __init__(self) -> None:
        self.entries: list[str] = []
        self.classes: set[str] = set()

    # RichLog-like
    def write(self, item, **_: object) -> None:
        self.entries.append(str(getattr(item, "plain", item)))

    def clear(self) -> None:
        self.entries.clear()

    def scroll_end(self) -> None:  # pragma: no cover
        pass

    # Node-like
    def add_class(self, name: str) -> None:
        self.classes.add(name)

    def remove_class(self, name: str) -> None:
        self.classes.discard(name)


class StubContent:
    def __init__(self) -> None:
        self.classes: set[str] = set()

    def add_class(self, name: str) -> None:
        self.classes.add(name)

    def remove_class(self, name: str) -> None:
        self.classes.discard(name)


@pytest.mark.asyncio
async def test_layout_command_via_on_input(monkeypatch):
    tui = TUI(concurrency=0)
    log = StubLogNode()
    content = StubContent()

    def q(selector, *_a, **_k):
        if selector == "#log":
            return log
        if selector == "#content":
            return content
        raise AssertionError(selector)

    monkeypatch.setattr(tui, "query_one", q)

    event = SimpleNamespace(value="/layout stacked", input=SimpleNamespace(value="/layout stacked"))
    await tui.on_input_submitted(event)

    assert "stacked" in content.classes
    assert "stacked" in log.classes
    assert event.input.value == ""


@pytest.mark.asyncio
async def test_modules_flow_sets_model(monkeypatch):
    tui = TUI(concurrency=0)
    log = StubLogNode()

    def q(selector, *_a, **_k):
        if selector == "#log":
            return log
        raise AssertionError(selector)

    monkeypatch.setattr(tui, "query_one", q)

    # Minimal runtime surface
    monkeypatch.setattr(runtime, "MODEL_PRESETS", {"chat": {"slug": "m/chat"}, "reasoner": {"slug": "m/r"}})
    monkeypatch.setattr(runtime, "MODULE_ORDER", ["agent"])  # single, index 1
    monkeypatch.setattr(runtime, "MODULE_INFO", {"agent": {"label": "Agent", "configure": "configure_model"}})

    captured: list[str] = []

    def fake_configure(model: str, **kwargs):  # type: ignore[override]
        captured.append(model)

    monkeypatch.setattr(runtime, "configure_model", fake_configure)
    monkeypatch.setattr("agent_manual_pkg.tui.get_config", lambda: types.SimpleNamespace(model="chat"))
    monkeypatch.setattr(runtime, "get_module_model", lambda name: "chat")

    # Start modules flow
    await tui.on_input_submitted(SimpleNamespace(value="/modules", input=SimpleNamespace(value="/modules")))
    assert tui.awaiting_module_selection is True

    # Pick the only module by numeric index
    await tui.on_input_submitted(SimpleNamespace(value="1", input=SimpleNamespace(value="1")))
    assert tui.awaiting_module_model_choice is True and tui.selected_module == "agent"

    # Choose a model
    await tui.on_input_submitted(SimpleNamespace(value="reasoner", input=SimpleNamespace(value="reasoner")))

    assert tui.awaiting_module_model_choice is False
    assert captured and captured[-1] == "reasoner"

