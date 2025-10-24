import types
import pytest


class StubLog:
    def __init__(self) -> None:
        self.entries = []
        self.border_title = None
        self.border_title_align = None

    def write(self, item) -> None:
        self.entries.append(item)

    def clear(self) -> None:
        self.entries.clear()

    def scroll_end(self) -> None:
        pass


class StubStatic:
    def __init__(self) -> None:
        self.contents = []

    def update(self, value) -> None:
        self.contents.append(value)


def extract_plain(text):
    return getattr(text, "plain", str(text))


def test_handle_model_command(monkeypatch):
    from agent_manual_pkg.tui import TUI

    app = TUI()
    log = StubLog()

    monkeypatch.setattr("agent_manual_pkg.tui.get_config", lambda: types.SimpleNamespace(model="chat"))
    monkeypatch.setattr(
        "agent_manual_pkg.tui.runtime.MODEL_PRESETS",
        {"chat": {"slug": "test/chat", "temperature": 0.1, "max_tokens": 1000}},
    )

    consumed = app._handle_command("/model", log)
    assert consumed is True
    assert app.awaiting_model_choice is True
    assert any("choose model" in extract_plain(e) for e in log.entries)


@pytest.mark.asyncio
async def test_blueberries_response(monkeypatch):
    from agent_manual_pkg.tui import TUI

    app = TUI()
    log = StubLog()
    status = StubStatic()
    spinner = StubStatic()
    reasoning = StubStatic()

    def fake_query_one(selector, widget_type=None):
        if selector == "#log":
            return log
        if selector == "#status":
            return status
        if selector == "#spinner":
            return spinner
        if selector == "#reasoning":
            return reasoning
        raise AssertionError(f"unexpected selector {selector}")

    monkeypatch.setattr(app, "query_one", fake_query_one)

    event = types.SimpleNamespace(value="blueberries", input=types.SimpleNamespace(value=""))
    await app.on_input_submitted(event)

    plains = [extract_plain(x) for x in log.entries]
    assert any("seirrebeulb" in p for p in plains)

