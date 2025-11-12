from __future__ import annotations

from types import SimpleNamespace
import builtins

import pytest

import sys
sys.path.insert(0, 'agent_manual_pkg/src')
from agent_manual_pkg import tui as app  # type: ignore
from agent_manual_pkg.tui import runtime  # type: ignore


class StubLog:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def write(self, message: str, **_: object) -> None:
        # Accept both Text and str; coerce to str for assertions
        self.lines.append(str(message))

    def clear(self) -> None:
        self.lines.clear()

    def scroll_end(self) -> None:  # pragma: no cover - noop
        pass


def _fake_query_one(selector: str, *_args, **_kwargs):
    if selector == "#log":
        return _fake_query_one.log
    return None


@pytest.mark.asyncio
async def test_model_command_and_choice(monkeypatch):
    _fake_query_one.log = StubLog()
    tui = app.TUI(concurrency=0)
    monkeypatch.setattr(tui, "query_one", _fake_query_one)

    calls: list[str] = []

    def wrapped_configure(model: str, **kwargs):  # type: ignore[override]
        calls.append(model)

    monkeypatch.setattr(runtime, "configure_model", wrapped_configure)

    # Trigger the model selection menu
    await tui.on_input_submitted(SimpleNamespace(value="/model", input=SimpleNamespace(value="/model")))
    assert tui.awaiting_model_choice is True

    # Choose a valid model key
    some_model = next(iter(runtime.MODEL_PRESETS.keys()))
    await tui.on_input_submitted(SimpleNamespace(value=some_model, input=SimpleNamespace(value=some_model)))
    assert tui.awaiting_model_choice is False
    assert some_model in calls


@pytest.mark.asyncio
async def test_max_tokens_prompt_and_value(monkeypatch):
    _fake_query_one.log = StubLog()
    tui = app.TUI(concurrency=0)
    monkeypatch.setattr(tui, "query_one", _fake_query_one)

    captured: dict[str, int] = {}

    def wrapped_configure(model: str, *, max_tokens=None, **kwargs):  # type: ignore[override]
        captured["max_tokens"] = int(max_tokens or 0)

    monkeypatch.setattr(runtime, "configure_model", wrapped_configure)

    # Ask for max_tokens without arg -> prompt state
    await tui.on_input_submitted(SimpleNamespace(value="/max_tokens", input=SimpleNamespace(value="/max_tokens")))
    assert tui.awaiting_max_tokens is True

    # Provide a positive integer
    await tui.on_input_submitted(SimpleNamespace(value="200", input=SimpleNamespace(value="200")))
    assert tui.awaiting_max_tokens is False
    assert captured.get("max_tokens") == 200
