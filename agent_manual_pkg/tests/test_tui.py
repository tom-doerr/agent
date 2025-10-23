import asyncio
import sys
import types
from pathlib import Path

import pytest
from textual.css import parse as css_parse
from textual.css.stylesheet import Stylesheet

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from agent_manual_pkg.tui import Job, TUI


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


def test_label_panes_sets_titles(monkeypatch):
    app = TUI()
    panes = {selector: StubLog() for selector in ("#satisfaction", "#memory", "#dspy", "#raw", "#log")}

    def fake_query_one(selector, widget_type):
        return panes[selector]

    monkeypatch.setattr(app, "query_one", fake_query_one)
    app._label_panes()

    assert panes["#dspy"].border_title == "DSPy History"
    assert panes["#raw"].border_title == "DSPy Raw"
    for pane in panes.values():
        assert pane.border_title_align == "left"


@pytest.mark.asyncio
async def test_process_job_streams_to_dspy_log(monkeypatch):
    app = TUI()
    dspy_log = StubLog()
    raw_log = StubLog()

    def fake_query_one(selector, widget_type):
        if selector == "#dspy":
            return dspy_log
        if selector == "#raw":
            return raw_log
        raise AssertionError(f"unexpected selector {selector}")

    monkeypatch.setattr(app, "query_one", fake_query_one)
    monkeypatch.setattr(app, "_refresh_satisfaction_view", lambda: None)
    monkeypatch.setattr(app, "_refresh_memory_view", lambda: None)

    steps = [
        {"thought": "consider options", "tool": "plan", "args": {"next": "run"}, "observation": "ok"},
    ]

    class DummyAgent:
        def __call__(self, *, prompt: str):
            assert prompt == "hello"
            return types.SimpleNamespace(steps=steps, answer="all done", raw_history=["PROMPT: example"])

    monkeypatch.setattr("agent_manual_pkg.tui.runtime.get_agent", lambda: DummyAgent())
    monkeypatch.setattr("agent_manual_pkg.tui.MEMORY_MODULE", lambda prompt, steps: [])
    app._run_goal_planner = lambda prompt: (types.SimpleNamespace(goals=[]), None)
    app._run_satisfaction_scorer = lambda: (types.SimpleNamespace(score=5, rationale="fine"), None)

    job = Job(id="123", prompt="hello")
    log = StubLog()
    status = StubStatic()
    spinner = StubStatic()
    reasoning = StubStatic()

    def fake_query_one(selector, widget_type=None):
        if selector == "#dspy":
            return dspy_log
        if selector == "#raw":
            return raw_log
        if selector == "#status":
            return status
        if selector == "#spinner":
            return spinner
        if selector == "#reasoning":
            return reasoning
        raise AssertionError(f"unexpected selector {selector}")

    monkeypatch.setattr(app, "query_one", fake_query_one)

    await app._process_job(job, log, asyncio.get_running_loop())

    plains = [extract_plain(item) for item in dspy_log.entries]
    assert any("▶ 'hello'" in entry for entry in plains)
    assert any("consider options" in entry for entry in plains)
    assert any("plan" in entry for entry in plains)
    assert any("all done" in entry for entry in plains)
    assert any(isinstance(entry, str) and entry.startswith("PROMPT") for entry in raw_log.entries)


def test_update_reasoning_label(monkeypatch):
    app = TUI()
    label = StubStatic()
    monkeypatch.setattr(app, "query_one", lambda selector, widget=None: label)
    app._update_reasoning_label()
    assert any("Reasoning Effort" in str(item) for item in label.contents)


def test_css_parses():
    scope = "inline"
    location = ("<inline>", "")
    list(css_parse.parse(scope, TUI.CSS, location))


def test_stylesheet_compiles_without_error(tmp_path):
    sheet = Stylesheet()
    css_file = tmp_path / "theme.css"
    css_file.write_text(TUI.CSS)
    sheet.read(css_file)


def test_build_settings_definitions(monkeypatch):
    app = TUI()
    cfg = types.SimpleNamespace(max_tokens=None)
    monkeypatch.setattr("agent_manual_pkg.tui.get_config", lambda: cfg)
    monkeypatch.setattr(
        "agent_manual_pkg.tui.runtime.MODEL_PRESETS",
        {
            "chat": {"slug": "test/chat", "temperature": 0.2, "max_tokens": 1000},
            "reasoner": {"slug": "test/reasoner", "temperature": 0.4, "max_tokens": 2000},
        },
    )
    monkeypatch.setattr("agent_manual_pkg.tui.runtime.get_module_model", lambda name: "chat")
    monkeypatch.setattr("agent_manual_pkg.tui.runtime.configure_model", lambda *args, **kwargs: None)
    monkeypatch.setattr("agent_manual_pkg.tui.runtime.configure_memory_model", lambda value: None)
    monkeypatch.setattr("agent_manual_pkg.tui.runtime.configure_satisfaction_goals_model", lambda value: None)
    monkeypatch.setattr("agent_manual_pkg.tui.runtime.configure_satisfaction_score_model", lambda value: None)

    settings = app._build_settings()
    keys = [setting.key for setting in settings]
    assert keys == ["agent_model", "max_tokens", "memory_model", "goals_model", "score_model"]
    token_setting = next(setting for setting in settings if setting.key == "max_tokens")
    assert token_setting.parser("2048") == 2048
