import asyncio
import atexit
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import dspy
import pytest
from typing import get_type_hints

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SRC = ROOT / "agent_manual_pkg" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

CONFIG_PATH = ROOT / "tests" / "_agent_manual_config.json"
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
if CONFIG_PATH.exists():
    CONFIG_PATH.unlink()
os.environ["AGENT_MANUAL_CONFIG"] = str(CONFIG_PATH)
atexit.register(lambda: CONFIG_PATH.unlink(missing_ok=True))

MEMORY_PATH = CONFIG_PATH.with_name("memory.json")
if MEMORY_PATH.exists():
    MEMORY_PATH.unlink()
atexit.register(lambda: MEMORY_PATH.unlink(missing_ok=True))

from agent_manual_pkg import app
import agent_manual_pkg.runtime as runtime
import agent_manual_pkg.cli as cli
from textual.widgets import Input, RichLog
from textual.events import Key
from textual.css.stylesheet import Stylesheet
import agent_manual_pkg.tui as tui_module
from agent_manual_pkg import satisfaction


@pytest.fixture(autouse=True)
def clear_memory_file():
    if MEMORY_PATH.exists():
        MEMORY_PATH.unlink()
    app.update_config(module_models={}, persist=True)
    yield
    if MEMORY_PATH.exists():
        MEMORY_PATH.unlink()
    app.update_config(module_models={}, persist=True)


@pytest.fixture(autouse=True)
def sync_to_thread(monkeypatch):
    async def _run_inline(func, /, *args, **kwargs):
        return func(*args, **kwargs)

    monkeypatch.setattr(asyncio, "to_thread", _run_inline)
    yield


@pytest.fixture
def memory_stub(monkeypatch, request):
    if request.node.get_closest_marker("no_memory_stub"):
        yield
        return
    original_predict = dspy.Predict
    summary_signature = getattr(app.MemoryModule, "SummarySignature", None)
    goal_signature = getattr(satisfaction, "_GoalsSignature", None)
    score_signature = getattr(satisfaction, "_ScoreSignature", None)

    class _StubPredictor:
        def __call__(self, **_: object) -> object:
            return SimpleNamespace(updates='[{"action": "create", "content": "stub memory"}]')

    class _GoalPredictor:
        def __call__(self, **_: object) -> object:
            return SimpleNamespace(instrumental_goals=["stub goal"])

    class _ScorePredictor:
        def __call__(self, **_: object) -> object:
            return SimpleNamespace(score=5, rationale="stub rationale")

    def _factory(signature, *args, **kwargs):
        if summary_signature is not None and signature is summary_signature:
            return _StubPredictor()
        if goal_signature is not None and signature is goal_signature:
            return _GoalPredictor()
        if score_signature is not None and signature is score_signature:
            return _ScorePredictor()
        return original_predict(signature, *args, **kwargs)

    monkeypatch.setattr(dspy, "Predict", _factory)
    monkeypatch.setattr(runtime, "build_lm", lambda *_, **__: object())
    original_goal = satisfaction.GOAL_PLANNER
    original_scorer = satisfaction.SATISFACTION_SCORER

    class GoalStub:
        def __call__(self, **kwargs):
            return satisfaction.InstrumentalGoals(goals=["stub goal"])

    class ScoreStub:
        def __call__(self, **kwargs):
            return satisfaction.SatisfactionResult(score=5, rationale="stub")

    monkeypatch.setattr(satisfaction, "GOAL_PLANNER", GoalStub())
    monkeypatch.setattr(satisfaction, "SATISFACTION_SCORER", ScoreStub())
    try:
        yield
    finally:
        monkeypatch.setattr(dspy, "Predict", original_predict)
        monkeypatch.setattr(satisfaction, "GOAL_PLANNER", original_goal)
        monkeypatch.setattr(satisfaction, "SATISFACTION_SCORER", original_scorer)




def test_ls_lists_contents(tmp_path):
    (tmp_path / "b_dir").mkdir()
    (tmp_path / "a.txt").write_text("")

    result = app.ls(os.fspath(tmp_path))

    assert result == "a.txt\nb_dir/"


def test_tool_wraps_ls():
    tool = app.TOOLS[0]

    assert tool.name == "ls"
    assert tool.func is app.ls


def test_signature_instructions_mentions_ls():
    assert "ls(path)" in app.SIGNATURE.instructions


def test_run_shell_runs_safe_command():
    result = app.run_shell("echo hello")
    assert result["status"] == "ok"
    assert result["command"] == "echo hello"
    assert result["output"] == "hello"
    assert result["safety"]["passed"] is True


def test_run_shell_blocks_banned_command():
    blocked = app.run_shell("rm -rf /")
    assert blocked["status"] == "blocked"
    assert blocked["safety"]["passed"] is False


def test_tool_list_contains_run_shell():
    names = {tool.name for tool in app.TOOLS}
    assert "run_shell" in names



def test_send_message_tool():
    assert any(tool.name == "send_message" for tool in app.TOOLS)
    assert app.send_message("hello") == "hello"


@pytest.mark.asyncio
async def test_tui_logs_wrap():
    tui = app.TUI(concurrency=0)
    async with tui.run_test():
        log_widget = tui.query_one("#log", RichLog)
        memory_widget = tui.query_one("#memory", RichLog)
        satisfaction_widget = tui.query_one("#satisfaction", RichLog)
        assert log_widget.wrap is True
        assert memory_widget.wrap is True
        assert satisfaction_widget.wrap is True


def test_css_includes_message_styles():
    css = app.TUI.CSS
    assert ".user-msg" in css
    assert ".agent-msg" in css
    assert ".system-msg" in css
    assert ".answer-msg" in css
    assert ".context-msg" in css




def test_shortcut_help(monkeypatch):
    tui = app.TUI(concurrency=0)
    gen = tui.compose()
    next(gen)  # status
    input_widget = next(gen)
    next(gen)  # log
    next(gen)  # memory
    pushed = []
    monkeypatch.setattr(tui, "push_screen", lambda screen: pushed.append(screen))
    assert tui._handle_shortcut("?", False) is True
    assert len(pushed) == 1 and isinstance(pushed[0], app.HelpScreen)
    assert tui._handle_shortcut("question_mark", False) is True
    assert len(pushed) == 2
    assert tui._handle_shortcut("?", True) is False


def test_shortcut_gi_focus_input(monkeypatch):
    tui = app.TUI(concurrency=0)
    gen = tui.compose()
    next(gen)  # status
    input_widget = next(gen)
    next(gen)  # log
    next(gen)  # memory
    assert tui._handle_shortcut("g", False) is True
    recorded = []
    tui.set_focus = lambda widget, *args, **kwargs: recorded.append(widget)
    original_query_one = tui.query_one
    tui.query_one = lambda selector, *args, **kwargs: input_widget if selector is Input else original_query_one(selector, *args, **kwargs)
    assert tui._handle_shortcut("i", False) is True
    assert recorded and recorded[-1] is input_widget
    assert tui._handle_shortcut("x", False) is False


def test_shortcut_escape_leaves_input():
    tui = app.TUI(concurrency=0)
    gen = tui.compose()
    next(gen)  # status
    input_widget = next(gen)
    next(gen)  # log
    next(gen)  # memory
    recorded = []
    tui.set_focus = lambda widget, *args, **kwargs: recorded.append(widget)
    assert tui._handle_shortcut("escape", True) is True
    assert recorded and recorded[-1] is None


def test_on_key_does_not_crash_without_screen():
    tui = app.TUI(concurrency=0)
    event = Key("backspace", "\x7f")
    tui.on_key(event)  # should not raise


def test_on_key_forwards_when_screen_present():
    tui = app.TUI(concurrency=0)
    forwarded = []

    class DummyScreen:
        focused = None

        def _forward_event(self, event):
            forwarded.append(event)

    stack = object.__getattribute__(tui, "_screen_stack")  # bypass descriptor to mutate
    stack.append(DummyScreen())

    event = Key("backspace", "\x7f")
    tui.on_key(event)
    assert forwarded == [event]


@pytest.mark.asyncio
async def test_tui_help_screen(memory_stub):
    tui = app.TUI(concurrency=0)
    async with tui.run_test() as pilot:
        await pilot.press("#in", "escape")
        await pilot.press("question_mark")
        await pilot.pause(0.05)
        assert isinstance(tui.screen, app.HelpScreen)


def test_configure_model_switches_lm():
    original = app.CURRENT_MODEL
    app.configure_model("reasoner")
    assert app.CURRENT_MODEL == "reasoner"
    assert app.LM.model == app.MODEL_PRESETS["reasoner"]["slug"]
    data = json.loads(CONFIG_PATH.read_text())
    assert data["model"] == "reasoner"


def test_get_module_model_respects_overrides():
    cfg_before = app.get_config()
    original_model = cfg_before.model
    original_modules = dict(cfg_before.module_models)
    try:
        app.configure_model("chat", persist=True)
        app.update_config(module_models={"memory": "reasoner"}, persist=True)
        assert runtime.get_module_model("memory") == "reasoner"
        assert runtime.get_module_model("unknown") == app.get_config().model
    finally:
        app.update_config(module_models=original_modules, persist=True)
        app.configure_model(original_model, persist=True)


def test_safety_check_behaviour():
    ok, detail = runtime.SAFETY.assess("echo hi")
    assert ok is True and detail == "passed"
    blocked, msg = runtime.SAFETY.assess("rm -rf /tmp")
    assert blocked is False and "rm -rf /" in msg
    assert runtime.SAFETY.forward("rm -rf /") is False


def test_runtime_dynamic_attrs():
    runtime.configure_model("chat", persist=False)
    assert runtime.AGENT is not None
    with pytest.raises(AttributeError):
        getattr(runtime, "does_not_exist")


def test_configure_satisfaction_modules():
    runtime.configure_satisfaction_goals_model("chat")
    runtime.configure_satisfaction_score_model("reasoner")
    cfg = app.get_config()
    assert cfg.module_models["satisfaction_goals"] == "chat"
    assert cfg.module_models["satisfaction_score"] == "reasoner"


def test_instrumental_goals_model_normalizes():
    model = satisfaction.InstrumentalGoals(goals="Goal A\nGoal B")
    assert model.goals == ["Goal A", "Goal B"]


def test_satisfaction_result_rationale_is_trimmed():
    text = "x" * 500
    result = satisfaction.SatisfactionResult(score=5, rationale=text)
    assert len(result.rationale) == 200


def test_build_lm_includes_reasoning(monkeypatch):
    captured = {}

    def fake_lm(*, model, max_tokens, temperature, reasoning):
        captured["model"] = model
        captured["max_tokens"] = max_tokens
        captured["temperature"] = temperature
        captured["reasoning"] = reasoning
        return object()

    monkeypatch.setattr(dspy, "LM", fake_lm)
    runtime.build_lm("reasoner")
    preset = runtime.MODEL_PRESETS["reasoner"]
    assert captured["model"] == preset["slug"]
    assert captured["reasoning"] == preset["reasoning"]


def test_goal_planner_uses_runtime_model(memory_stub):
    goals = satisfaction.GOAL_PLANNER(
        user_message="Plan next steps",
        chat_history=[{"role": "user", "content": "Do thing"}],
        memory_slots=["remember"]
    )
    assert goals.goals


def test_satisfaction_scorer_outputs_result(memory_stub):
    result = satisfaction.SATISFACTION_SCORER(
        instrumental_goals=["goal"],
        chat_history=[{"role": "assistant", "content": "done"}],
        memory_slots=[]
    )
    assert 1 <= result.score <= 9


def test_spinner_updates(monkeypatch):
    tui = app.TUI(concurrency=0)

    class StubSpinner:
        def __init__(self):
            self.messages: list[str] = []

        def update(self, message: str) -> None:
            self.messages.append(message)

    spinner = StubSpinner()

    def fake_query(selector, *args, **kwargs):
        if selector == "#spinner":
            return spinner
        raise AssertionError(selector)

    monkeypatch.setattr(tui, "query_one", fake_query)
    tui._set_spinner("⏳ working…")
    tui._spinner_index = 0
    tui._tick_spinner()

    assert spinner.messages[0] == "⏳ working…"
    assert spinner.messages[1].startswith("⏳ working…")

def test_tui_css_parses():
    stylesheet = Stylesheet()
    stylesheet.set_variables(
        {
            "accent": "#ffffff",
            "boost": "#ffffff",
            "success": "#00ff00",
            "warning": "#ffaa00",
            "text-muted": "#888888",
        }
    )
    stylesheet.add_source(app.TUI.CSS)
    stylesheet.parse()


def test_process_job_log_annotation_is_resolvable():
    hints = get_type_hints(tui_module.TUI._process_job, globalns=vars(tui_module))
    assert hints["log"] is RichLog


def test_configure_model_rejects_unknown():
    try:
        app.configure_model("bogus")
    except ValueError as err:
        assert "unknown model" in str(err)
    else:
        raise AssertionError("configure_model should raise on unknown model")


def test_agent_wrapper_exposes_run():
    assert hasattr(app.AGENT, "run")
    assert isinstance(app.AGENT, app.ReadableReAct)


def test_config_file_created():
    assert CONFIG_PATH.exists()


def test_configure_model_updates_max_tokens():
    cfg = app.get_config()
    original_model = cfg.model
    original_tokens = cfg.max_tokens

    app.configure_model(original_model, max_tokens=1234)
    assert app.get_config().max_tokens == 1234
    data = json.loads(CONFIG_PATH.read_text())
    assert data["max_tokens"] == 1234

    if original_tokens is None:
        app.update_config(max_tokens=None)
        app.configure_model(original_model, persist=True)
    else:
        app.configure_model(original_model, max_tokens=original_tokens)


def test_main_cli_sets_model_and_tokens(monkeypatch):
    calls = []

    def fake_configure(model, max_tokens=None, persist=True):
        calls.append(("configure", model, max_tokens, persist))

    class DummyTUI:
        def __init__(self, concurrency=1):
            calls.append(("tui_init", concurrency))

        def run(self):
            calls.append(("tui_run",))

    monkeypatch.setattr(cli, "configure_model", fake_configure)
    monkeypatch.setattr(cli, "TUI", lambda concurrency=1: DummyTUI(concurrency))

    cli.main(["--config", str(CONFIG_PATH), "--model", "reasoner", "--max-tokens", "2048"])

    assert ("configure", "reasoner", 2048, True) in calls
    assert ("tui_init", 1) in calls
    assert ("tui_run",) in calls


def test_main_cli_defaults_to_config(monkeypatch):
    captures = []

    def fake_configure(model, max_tokens=None, persist=True):
        captures.append((model, max_tokens, persist))

    class DummyTUI:
        def __init__(self, concurrency=1):
            pass

        def run(self):
            pass

    monkeypatch.setattr(cli, "configure_model", fake_configure)
    monkeypatch.setattr(cli, "TUI", lambda concurrency=1: DummyTUI(concurrency))

    cli.main(["--config", str(CONFIG_PATH)])

    assert captures[0][0] == app.get_config().model
    assert captures[0][1] is None
    assert captures[0][2] is False


@pytest.mark.asyncio
async def test_worker_logs_shell_integration(monkeypatch, memory_stub):
    class StubLog:
        def __init__(self) -> None:
            self.lines: list[str] = []

        def write(self, message: str, **_: object) -> None:
            self.lines.append(message)

        def clear(self) -> None:
            self.lines.clear()

        def scroll_end(self) -> None:
            pass

    class StubStatus:
        def __init__(self):
            self.history: list[str] = []

        def update(self, message: str) -> None:
            self.history.append(message)

    main_log = StubLog()
    memory_log = StubLog()
    satisfaction_log = StubLog()
    status_log = StubStatus()

    def fake_query_one(selector, node_type=None, **kwargs):
        if selector == "#log" or selector is RichLog and node_type is None:
            return main_log
        if selector == "#memory":
            return memory_log
        if selector == "#satisfaction":
            return satisfaction_log
        if selector == "#status":
            return status_log
        if selector == "#spinner":
            return status_log
        raise AssertionError(f"Unexpected query: {selector}")

    class FakePlanner:
        def __call__(self, **kwargs):
            return satisfaction.InstrumentalGoals(goals=["goal 1", "goal 2"])

    class FakeScorer:
        def __call__(self, **kwargs):
            return satisfaction.SatisfactionResult(score=7, rationale="solid")

    monkeypatch.setattr(tui_module, "GOAL_PLANNER", FakePlanner())
    monkeypatch.setattr(tui_module, "SATISFACTION_SCORER", FakeScorer())

    monkeypatch.setattr(runtime, "AGENT", SimpleNamespace(run=lambda prompt: {
        "answer": "done",
        "steps": [
            {
                "thought": "consider command",
                "tool": "run_shell",
                "args": {"command": "echo hi"},
                "observation": {
                    "command": "echo hi",
                    "output": "hi",
                    "status": "ok",
                    "safety": {"passed": True, "detail": "passed"},
                },
            }
        ],
    }))

    tui = app.TUI(concurrency=0)
    monkeypatch.setattr(tui, "query_one", fake_query_one)
    monkeypatch.setattr(tui, "call_from_thread", lambda func, *a, **k: func(*a, **k))

    job = app.Job(id="abcdef123456", prompt="run shell")

    async def run_immediate(executor, func, *args):
        return func(*args)

    fake_loop = SimpleNamespace(run_in_executor=run_immediate)
    tui._start_request(job.prompt)
    await tui._process_job(job, main_log, fake_loop)
    tui._finish_request(success=True)

    assert any("🖥️ command: echo hi" in line for line in main_log.lines)
    assert any("🛡️ safety: passed" in line for line in main_log.lines)
    assert any("📥 output: hi" in line for line in main_log.lines)
    assert memory_log.lines
    assert MEMORY_PATH.exists()
    stored = json.loads(MEMORY_PATH.read_text())
    assert stored and all(len(entry) <= 100 for entry in stored)
    assert any("State: Running" in entry for entry in status_log.history)
    assert any("State: Completed" in entry for entry in status_log.history)
    assert any("🎯" in line for line in satisfaction_log.lines)
    assert any("🧭" in line for line in satisfaction_log.lines)


@pytest.mark.asyncio


@pytest.mark.asyncio
async def test_status_updates_on_failure(monkeypatch, memory_stub):
    class StubLog:
        def __init__(self) -> None:
            self.lines: list[str] = []

        def write(self, message: str, **_: object) -> None:
            self.lines.append(message)

        def clear(self) -> None:
            self.lines.clear()

        def scroll_end(self) -> None:
            pass

        def scroll_end(self) -> None:
            pass

    class StubStatus:
        def __init__(self):
            self.lines: list[str] = []

        def update(self, message: str) -> None:
            self.lines.append(message)

    main_log = StubLog()
    memory_log = StubLog()
    satisfaction_log = StubLog()
    status_log = StubStatus()

    def fake_query(selector, node_type=None, **kwargs):
        if selector == "#log" or selector is RichLog and node_type is None:
            return main_log
        if selector == "#memory":
            return memory_log
        if selector == "#satisfaction":
            return satisfaction_log
        if selector == "#status":
            return status_log
        if selector == "#spinner":
            return status_log
        if selector == Input:
            return type("DummyInput", (), {"focus": lambda self: None})()
        return None

    def raise_error(prompt: str):
        raise ValueError("boom")

    monkeypatch.setattr(runtime.AGENT, "run", raise_error)

    tui = app.TUI(concurrency=0)
    monkeypatch.setattr(tui, "query_one", fake_query)

    job = app.Job(id="deadbeef", prompt="fail")
    tui._start_request(job.prompt)
    with pytest.raises(ValueError):
        await tui._process_job(job, main_log, asyncio.get_running_loop())
    tui._finish_request(False, "boom")

    assert any("Failed" in entry for entry in status_log.lines)
    assert any("Error: boom" in entry for entry in status_log.lines)

async def test_on_input_model_command(monkeypatch):
    class StubLog:
        def __init__(self):
            self.lines: list[str] = []

        def write(self, message: str, **_: object) -> None:
            self.lines.append(message)

        def clear(self) -> None:
            self.lines.clear()

        def scroll_end(self) -> None:
            pass

    class StubStatus:
        def __init__(self):
            self.lines: list[str] = []

        def update(self, message: str) -> None:
            self.lines.append(message)

    main_log = StubLog()
    memory_log = StubLog()
    status_log = StubStatus()
    satisfaction_log = StubLog()

    tui = app.TUI(concurrency=0)

    def fake_query(selector, node_type=None, **kwargs):
        if selector == "#log" or selector is RichLog and node_type is None:
            return main_log
        if selector == "#memory":
            return memory_log
        if selector == "#satisfaction":
            return satisfaction_log
        if selector == "#status":
            return status_log
        if selector == "#spinner":
            return status_log
        if selector == Input:
            return type("DummyInput", (), {"focus": lambda self: None})()
        return None

    monkeypatch.setattr(tui, "query_one", fake_query)

    event = SimpleNamespace(value="/model", input=SimpleNamespace(value="/model"))
    await tui.on_input_submitted(event)

    assert tui.awaiting_model_choice is True
    assert any("choose model" in line for line in main_log.lines)
    assert event.input.value == ""


@pytest.mark.asyncio
async def test_on_input_model_selection(monkeypatch):
    calls = []

    def fake_configure(model, max_tokens=None, persist=True):
        calls.append((model, max_tokens, persist))

    tui = app.TUI(concurrency=0)
    status_log = type("StubStatus", (), {"update": lambda self, message: None})()

    class StubLog:
        def write(self, message: str, **_: object) -> None:
            return None

        def clear(self) -> None:
            return None

        def scroll_end(self) -> None:
            return None

    stub_log = StubLog()
    satisfaction_log = StubLog()

    def fake_query(selector, node_type=None, **kwargs):
        if selector == "#log" or selector is RichLog and node_type is None:
            return stub_log
        if selector == "#memory":
            return stub_log
        if selector == "#satisfaction":
            return satisfaction_log
        if selector == "#status":
            return status_log
        return None

    monkeypatch.setattr(tui, "query_one", fake_query)
    monkeypatch.setattr(runtime, "configure_model", fake_configure)

    tui.awaiting_model_choice = True
    event = SimpleNamespace(value="reasoner", input=SimpleNamespace(value="reasoner"))
    await tui.on_input_submitted(event)

    assert tui.awaiting_model_choice is False
    assert calls[-1] == ("reasoner", None, True)


@pytest.mark.asyncio
async def test_on_input_max_tokens(monkeypatch):
    captured = []

    def fake_configure(model, max_tokens=None, persist=True):
        captured.append((model, max_tokens, persist))

    log_lines = []

    class StubLog:
        def write(self, message: str, **_: object) -> None:
            log_lines.append(message)

        def clear(self) -> None:
            pass

        def scroll_end(self) -> None:
            pass

    status_log = type("StubStatus", (), {"update": lambda self, message: None})()
    tui = app.TUI(concurrency=0)
    stub_log = StubLog()
    satisfaction_log = StubLog()

    def fake_query(selector, node_type=None, **kwargs):
        if selector == "#log" or selector is RichLog and node_type is None:
            return stub_log
        if selector == "#memory":
            return stub_log
        if selector == "#satisfaction":
            return satisfaction_log
        if selector == "#status":
            return status_log
        return None

    monkeypatch.setattr(tui, "query_one", fake_query)
    monkeypatch.setattr(runtime, "configure_model", fake_configure)

    event = SimpleNamespace(value="/max_tokens 2048", input=SimpleNamespace(value="/max_tokens 2048"))
    await tui.on_input_submitted(event)

    assert captured[-1] == (app.get_config().model, 2048, True)
    assert any("max_tokens set to 2048" in line for line in log_lines)


@pytest.mark.asyncio
async def test_on_input_max_tokens_prompt(monkeypatch):
    captured = []

    def fake_configure(model, max_tokens=None, persist=True):
        captured.append((model, max_tokens, persist))

    log_lines = []

    class StubLog:
        def write(self, message: str, **_: object) -> None:
            log_lines.append(message)

        def clear(self) -> None:
            pass

        def scroll_end(self) -> None:
            pass

    status_log = type("StubStatus", (), {"update": lambda self, message: None})()
    tui = app.TUI(concurrency=0)
    stub_log = StubLog()
    satisfaction_log = StubLog()

    def fake_query(selector, node_type=None, **kwargs):
        if selector == "#log" or selector is RichLog and node_type is None:
            return stub_log
        if selector == "#memory":
            return stub_log
        if selector == "#satisfaction":
            return satisfaction_log
        if selector == "#status":
            return status_log
        return None

    monkeypatch.setattr(tui, "query_one", fake_query)
    monkeypatch.setattr(runtime, "configure_model", fake_configure)

    event1 = SimpleNamespace(value="/max_tokens", input=SimpleNamespace(value="/max_tokens"))
    await tui.on_input_submitted(event1)
    assert tui.awaiting_max_tokens is True

    event2 = SimpleNamespace(value="3000", input=SimpleNamespace(value="3000"))
    await tui.on_input_submitted(event2)

    assert tui.awaiting_max_tokens is False
    assert captured[-1] == (app.get_config().model, 3000, True)
    assert any("max_tokens set to 3000" in line for line in log_lines)


def test_memory_module_generates_updates(memory_stub):
    updates = app.MEMORY_MODULE(
        prompt="List files",
        steps=[
            {
                "thought": "Need directory contents",
                "tool": "run_shell",
                "args": {"command": "ls"},
                "observation": {"status": "ok", "output": "agent_manual_pkg", "command": "ls"},
            }
        ],
    )

    assert updates, "memory module should emit updates"
    assert all(isinstance(update, app.MemorySlotUpdate) for update in updates)
    assert all(len(update.content or "") <= 100 for update in updates)


def test_apply_memory_updates_write_read(monkeypatch):
    tui = app.TUI(concurrency=0)

    def fake_query(selector, node_type=None, **kwargs):
        class DummyLog:
            def write(self, message, **_: object):
                pass

            def clear(self):
                pass

            def scroll_end(self):
                pass

        return DummyLog()

    monkeypatch.setattr(tui, "query_one", fake_query)

    create_update = app.MemorySlotUpdate(action="create", content="remember this")
    tui.apply_memory_updates([create_update])
    assert app.load_memory_slots()[-1] == "remember this"

    update_update = app.MemorySlotUpdate(action="update", slot=0, content="new text")
    tui.apply_memory_updates([update_update])
    assert app.load_memory_slots()[0] == "new text"

    delete_update = app.MemorySlotUpdate(action="delete", slot=0)
    tui.apply_memory_updates([delete_update])
    assert not app.load_memory_slots()


@pytest.mark.asyncio
async def test_modules_menu_selection(monkeypatch, memory_stub):
    class StubLog:
        def __init__(self):
            self.lines: list[str] = []

        def write(self, message: str, **_: object) -> None:
            self.lines.append(message)

        def clear(self) -> None:
            self.lines.clear()

        def scroll_end(self) -> None:
            pass

    main_log = StubLog()
    memory_log = StubLog()
    satisfaction_log = StubLog()

    def fake_query(selector, node_type=None, **kwargs):
        if selector == "#log":
            return main_log
        if selector == "#memory":
            return memory_log
        if selector == "#satisfaction":
            return satisfaction_log
        return None

    calls: list[tuple[str, str]] = []

    def wrapped_configure_model(model, max_tokens=None, persist=True):
        calls.append(("agent", model))

    configure_memory_calls: list[tuple[str, str]] = []

    def wrapped_configure_memory(model, persist=True):
        configure_memory_calls.append(("memory", model))

    monkeypatch.setattr(runtime, "configure_model", wrapped_configure_model)
    monkeypatch.setattr(runtime, "configure_memory_model", wrapped_configure_memory)

    tui = app.TUI(concurrency=0)
    monkeypatch.setattr(tui, "query_one", fake_query)
    monkeypatch.setattr(tui, "call_from_thread", lambda func, *a, **k: func(*a, **k))

    cmd = SimpleNamespace(value="/modules", input=SimpleNamespace(value="/modules"))
    await tui.on_input_submitted(cmd)
    assert tui.awaiting_module_selection is True
    assert any("agent" in line for line in main_log.lines)

    select_agent = SimpleNamespace(value="agent", input=SimpleNamespace(value="agent"))
    await tui.on_input_submitted(select_agent)
    assert tui.awaiting_module_model_choice is True
    assert tui.selected_module == "agent"

    pick_reasoner = SimpleNamespace(value="reasoner", input=SimpleNamespace(value="reasoner"))
    await tui.on_input_submitted(pick_reasoner)
    assert tui.awaiting_module_model_choice is False
    assert ("agent", "reasoner") in calls

    # memory module via numeric selection
    main_log.clear()
    await tui.on_input_submitted(SimpleNamespace(value="/modules", input=SimpleNamespace(value="/modules")))
    await tui.on_input_submitted(SimpleNamespace(value="2", input=SimpleNamespace(value="2")))
    await tui.on_input_submitted(SimpleNamespace(value="chat", input=SimpleNamespace(value="chat")))
    assert ("memory", "chat") in configure_memory_calls
