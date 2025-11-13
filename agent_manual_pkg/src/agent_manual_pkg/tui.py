from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass
import time
from typing import Any, Callable, Dict, List, Optional, Set

from rich.text import Text
from textual.app import App, ComposeResult, ScreenStackError
from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.timer import Timer
from textual.widgets import Footer, Input, OptionList, RichLog, Static
from textual.widgets.option_list import Option

from . import runtime
from .config import get_config
from .memory import MEMORY_MODULE, MemorySlotUpdate, load_memory_slots, save_memory_slots
from .satisfaction import GOAL_PLANNER, SATISFACTION_SCORER, InstrumentalGoals, SatisfactionResult


HELP_TEXT = (
    "Shortcuts:\n"
    "  ?          Toggle help\n"
    "  g i        Focus prompt input\n"
    "  ESC        Leave prompt input\n"
    "  /model     Change default model\n"
    "  /modules   Assign models per module\n"
    "  /max_tokens <n>  Set max output tokens\n"
    "  /layout stacked|wide  Switch layout for narrow terminals\n"
)


class HelpScreen(ModalScreen[None]):
    def compose(self) -> ComposeResult:
        yield Static(HELP_TEXT, id="help-panel")

    def on_key(self, event: Key) -> None:
        if event.key in {"escape", "q"}:
            self.app.pop_screen()



@dataclass
class Job:
    id: str
    prompt: str


@dataclass
class SettingDefinition:
    key: str
    label: str
    description: str
    getter: Callable[[], Any]
    setter: Callable[[Any], None]
    parser: Callable[[str], Any] | None = None
    options: List[str] | None = None


class SettingsOverlay(ModalScreen[None]):
    BINDINGS = [
        ("escape", "dismiss", "Close"),
    ]

    def __init__(self, settings: List[SettingDefinition], on_update: Callable[[], None]):
        super().__init__()
        self._settings = {setting.key: setting for setting in settings}
        self._order = [setting.key for setting in settings]
        self._active: Optional[str] = self._order[0] if self._order else None
        self._on_update = on_update
        self._editing = False

    def compose(self) -> ComposeResult:
        options = [
            Option(self._render_label(key), id=key)
            for key in self._order
        ]
        yield Vertical(
            Static("Settings", id="settings-title"),
            OptionList(*options, id="settings-options"),
            Static("Enter to edit • Use ↑/↓ to select • Esc closes", id="settings-help"),
            Input(id="settings-input", placeholder="Type value and press Enter"),
            Static("", id="settings-description"),
        )

    def on_mount(self) -> None:
        input_widget = self.query_one("#settings-input", Input)
        input_widget.display = False
        self._update_description()

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:  # type: ignore[override]
        self._active = event.option.id
        self._editing = False
        self._hide_input()
        self._refresh_options(highlight=self._active)
        self._update_description()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:  # type: ignore[override]
        self._active = event.option.id
        self._handle_selection()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if not self._active:
            return
        setting = self._settings[self._active]
        value = event.value.strip()
        if not value:
            self._hide_input()
            return
        try:
            parsed = setting.parser(value) if setting.parser else value
            setting.setter(parsed)
        except Exception as exc:  # pragma: no cover - defensive
            description = self.query_one("#settings-description", Static)
            description.update(f"{setting.description}\n\nError: {exc}")
            return
        event.input.display = False
        event.input.value = ""
        self._editing = False
        self._refresh_options(highlight=self._active)
        self._update_description()
        self._notify_update()

    def _handle_selection(self) -> None:
        if not self._active:
            return
        setting = self._settings[self._active]
        if setting.options:
            current = str(setting.getter())
            options = setting.options
            try:
                idx = options.index(current)
            except ValueError:
                idx = -1
            new_value = options[(idx + 1) % len(options)]
            setting.setter(new_value)
            self._refresh_options(highlight=self._active)
            self._update_description()
            self._notify_update()
            return
        input_widget = self.query_one("#settings-input", Input)
        input_widget.display = True
        input_widget.value = str(setting.getter() or "")
        input_widget.focus()
        self._editing = True

    def _render_label(self, key: str) -> str:
        setting = self._settings[key]
        value = setting.getter()
        return f"{setting.label}: {value}"

    def _refresh_options(self, highlight: Optional[str] = None) -> None:
        option_list = self.query_one("#settings-options", OptionList)
        current_highlight = highlight or self._active
        option_list.clear_options()
        for key in self._order:
            option = Option(self._render_label(key), id=key)
            option_list.add_option(option)
        if current_highlight and current_highlight in self._order:
            index = self._order.index(current_highlight)
            option_list.highlighted = index  # type: ignore[attr-defined]

    def _update_description(self) -> None:
        description = self.query_one("#settings-description", Static)
        if not self._active:
            description.update("")
            return
        setting = self._settings[self._active]
        description.update(f"{setting.label}\n{setting.description}\nCurrent: {setting.getter()}")

    def _hide_input(self) -> None:
        input_widget = self.query_one("#settings-input", Input)
        input_widget.display = False
        input_widget.value = ""

    def _notify_update(self) -> None:
        self._on_update()
class TUI(App):
    BINDINGS = [("ctrl+comma", "show_settings", "Settings")]
    CSS = (
        "Screen { layout: vertical; background: #0f0b0d; color: #f7f1f2; } "
        "#top-bar { layout: horizontal; height: auto; min-height: 1; padding: 0 1; background: #1a0c0d; border: solid #3b1416; } "
        "#status { width: 1fr; padding: 0 1; } "
        "#top-right { layout: horizontal; width: auto; min-width: 24; align-horizontal: right; } "
        "#spinner { padding: 0 1; min-width: 12; color: #c96161; } "
        "#reasoning { padding: 0 1; color: #ff4d4f; text-style: bold; } "
        "#content { height: 1fr; layout: horizontal; background: #130a0b; padding: 0 1 1 1; } "
        "#content.stacked { layout: vertical; } "
        "#side-pane { width: 1fr; min-width: 30; layout: vertical; } "
        "#side-pane > RichLog { border: solid #3b1416; border-title-align: left; padding: 0 1; margin-bottom: 1; background: #1a0c0d; scrollbar-color: #ff4d4f #1a0c0d; } "
        "#log { width: 2fr; min-width: 40; border: solid #3b1416; border-title-align: left; padding: 0 1; margin-left: 1; background: #1a0c0d; scrollbar-color: #ff4d4f #1a0c0d; } "
        "#log.stacked { margin-left: 0; } "
        ".user-msg { color: #f7f1f2; } "
        ".agent-msg { color: #d3a4a6; text-style: italic; } "
        ".system-msg { color: #d3a4a6; } "
        ".answer-msg { color: #ff4d4f; text-style: bold; } "
        ".context-msg { color: #ff4d4f; text-style: italic; } "
        "#settings-title { text-style: bold; color: #ff4d4f; padding: 0 1; } "
        "#settings-options { border: solid #3b1416; background: #1a0c0d; } "
        "#settings-help { color: #d3a4a6; padding: 0 1; } "
        "#settings-description { color: #f7f1f2; padding: 0 1; border: solid #3b1416; background: #1a0c0d; } "
        "#settings-input { border: solid #3b1416; background: #0f0b0d; color: #f7f1f2; } "
    )
    running = reactive(False)

    def __init__(self, concurrency: int = 1):
        super().__init__()
        self.q: asyncio.Queue[Job] = asyncio.Queue()
        self.concurrency = concurrency
        self._worker_tasks: list[asyncio.Task[None]] = []
        self.awaiting_model_choice = False
        self.awaiting_max_tokens = False
        self.awaiting_module_selection = False
        self.awaiting_module_model_choice = False
        self.selected_module: Optional[str] = None
        self.memory_slots: List[str] = load_memory_slots()
        self._status_timer: Optional[Timer] = None
        self._spinner_timer: Optional[Timer] = None
        self._spinner_text_value: str = "Idle"
        self._spinner_index: int = 0
        self._request_start: Optional[float] = None
        self._active_modules: Set[str] = set()
        self._pending_g = False
        self._history: List[Dict[str, str]] = []
        self._latest_goals: InstrumentalGoals | None = None
        self._latest_score: SatisfactionResult | None = None
        self._satisfaction_error: Optional[str] = None

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Static(id="status"),
            Horizontal(
                Static(id="spinner"),
                Static(id="reasoning"),
                id="top-right",
            ),
            id="top-bar",
        )
        yield Input(
            placeholder="Ask anything (e.g., 'What files are here? Use ls(\".\")'). Press Enter…",
            id="in",
        )
        yield Horizontal(
            Vertical(
                RichLog(id="satisfaction", wrap=True, auto_scroll=True),
                RichLog(id="memory", wrap=True, auto_scroll=True),
                RichLog(id="dspy", wrap=True, auto_scroll=True),
                RichLog(id="raw", wrap=False, auto_scroll=True),
                id="side-pane",
            ),
            RichLog(id="log", wrap=True, auto_scroll=True),
            id="content",
        )
        yield Footer()

    async def on_mount(self) -> None:
        for _ in range(self.concurrency):
            self._worker_tasks.append(asyncio.create_task(self.worker()))
        self.query_one(Input).focus()
        self._refresh_memory_view()
        self._refresh_satisfaction_view()
        self._label_panes()
        self.query_one("#dspy", RichLog).clear()
        self.query_one("#raw", RichLog).clear()
        self._update_reasoning_label()
        self._set_status("Idle")
        self._set_spinner(None)
        self._set_layout("wide")

    async def on_unmount(self) -> None:
        for task in list(self._worker_tasks):
            task.cancel()
        self._worker_tasks.clear()

    async def _process_job(self, job: Job, log: RichLog, loop: asyncio.AbstractEventLoop) -> None:
        _ = job.id[:8]
        dspy_log = self.query_one("#dspy", RichLog)
        raw_log = self.query_one("#raw", RichLog)
        self._log_prompt(job.prompt, log, dspy_log, raw_log)

        prediction = await loop.run_in_executor(None, lambda: runtime.get_agent()(prompt=job.prompt))
        steps = getattr(prediction, "steps", [])
        self._emit_step_logs(log, dspy_log, raw_log, steps)
        self._emit_raw_history(raw_log, getattr(prediction, "raw_history", []))

        updates = await loop.run_in_executor(None, lambda: MEMORY_MODULE(prompt=job.prompt, steps=steps))
        self._apply_updates_and_refresh(updates)

        answer = getattr(prediction, "answer", "")
        self._emit_answer(log, dspy_log, answer)

        await asyncio.to_thread(self._update_goals, job.prompt)
        await asyncio.to_thread(self._update_score)

    async def worker(self):
        log = self.query_one("#log", RichLog)
        loop = asyncio.get_running_loop()
        while True:
            job = await self.q.get()
            self.running = True
            self._start_request(job.prompt)
            try:
                await self._process_job(job, log, loop)
                self._finish_request(success=True)
            except Exception as exc:  # pragma: no cover - defensive logging
                _ = job.id[:8]
                self._finish_request(success=False, message=str(exc))
                log.write(Text(f"❌ {exc!r}\n", style="system-msg"))
            finally:
                self.running = False
                self.q.task_done()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        log = self.query_one("#log", RichLog)
        if not text:
            event.input.value = ""
            return
        if self._handle_blueberries(text, log, event):
            return
        log.write(Text(text, style="user-msg"))
        log.scroll_end()
        if self._handle_command(text, log):
            event.input.value = ""
            return
        if self._route_awaiting_states(text, log, event):
            return
        self._history.append({"role": "user", "content": text})
        await self.q.put(Job(id=str(uuid.uuid4()), prompt=text))
        event.input.value = ""

    def _handle_blueberries(self, text: str, log: RichLog, event: Input.Submitted) -> bool:
        if text.lower() != "blueberries":
            return False
        log.write(Text("✅ seirrebeulb\n", style="answer-msg"))
        self._history.append({"role": "assistant", "content": "seirrebeulb"})
        event.input.value = ""
        return True

    def _route_awaiting_states(self, text: str, log: RichLog, event: Input.Submitted) -> bool:
        if self._handle_module_model_choice(text, log, event):
            return True
        if self._handle_module_selection(text, log, event):
            return True
        if self._handle_max_tokens(text, log, event):
            return True
        if self._handle_model_choice(text, log, event):
            return True
        return False

    def _handle_module_model_choice(self, text: str, log: RichLog, event: Input.Submitted) -> bool:
        if self.awaiting_module_model_choice and self.selected_module:
            choice = text.lower()
            if choice in runtime.MODEL_PRESETS:
                configure_name = runtime.MODULE_INFO[self.selected_module]["configure"]
                getattr(runtime, configure_name)(choice)
                log.write(Text(f"{self.selected_module} model set to {choice}", style="system-msg"))
                self._reset_module_state()
            else:
                log.write(Text(f"unknown model '{text}'. choose from: {', '.join(runtime.MODEL_PRESETS)}", style="system-msg"))
            event.input.value = ""
            return True
        return False

    def _handle_module_selection(self, text: str, log: RichLog, event: Input.Submitted) -> bool:
        if self.awaiting_module_selection:
            choice = text.lower(); module_name: Optional[str] = None
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(runtime.MODULE_ORDER):
                    module_name = runtime.MODULE_ORDER[index]
            elif choice in runtime.MODULE_INFO:
                module_name = choice
            if module_name is None:
                log.write(Text(f"unknown module '{text}'. choose from: {', '.join(runtime.MODULE_ORDER)}", style="system-msg"))
                event.input.value = ""
                return True
            self.awaiting_module_selection = False
            self.awaiting_module_model_choice = True
            self.selected_module = module_name
            current = runtime.get_module_model(module_name)
            log.write(
                f"choose model for {module_name} ({', '.join(runtime.MODEL_PRESETS)}). current={current}",
                style="system-msg",
            )
            event.input.value = ""
            return True
        return False

    def _handle_max_tokens(self, text: str, log: RichLog, event: Input.Submitted) -> bool:
        if self.awaiting_max_tokens:
            try:
                value = int(text); assert value > 0
            except Exception:
                log.write(Text("enter a positive integer for max_tokens", style="system-msg"))
            else:
                runtime.configure_model(get_config().model, max_tokens=value)
                self.awaiting_max_tokens = False
                log.write(Text(f"max_tokens set to {value}", style="system-msg"))
            event.input.value = ""
            return True
        return False

    def _handle_model_choice(self, text: str, log: RichLog, event: Input.Submitted) -> bool:
        if self.awaiting_model_choice:
            choice = text.lower()
            if choice in runtime.MODEL_PRESETS:
                runtime.configure_model(choice)
                self.awaiting_model_choice = False
                log.write(Text(f"model switched to {choice}", style="system-msg"))
            else:
                options = ", ".join(runtime.MODEL_PRESETS)
                log.write(Text(f"unknown model '{text}'. choose from: {options}", style="system-msg"))
            event.input.value = ""
            return True
        return False

    def _route_command(self, text: str, log: RichLog, event: Input.Submitted) -> bool:
        if text.startswith("/layout"):
            parts = text.split()
            mode = parts[1].lower() if len(parts) > 1 else "stacked"
            if mode not in {"stacked", "wide"}:
                log.write(Text("usage: /layout stacked|wide", style="system-msg"))
                return True
            self._set_layout(mode)
            log.write(Text(f"layout set to {mode}", style="system-msg"))
            event.input.value = ""
            return True

        if text == "/modules":
            self.awaiting_model_choice = False
            self.awaiting_max_tokens = False
            self._reset_module_state()
            self.awaiting_module_selection = True
            self._show_modules_list(log)
            event.input.value = ""
            return True

        if text == "/model":
            options = ", ".join(runtime.MODEL_PRESETS)
            log.write(Text(f"choose model ({options}). current={get_config().model}", style="system-msg"))
            self.awaiting_model_choice = True
            self._reset_module_state()
            event.input.value = ""
            return True

        if text.startswith("/max_tokens"):
            parts = text.split()
            if len(parts) == 2:
                try:
                    value = int(parts[1])
                    assert value > 0
                except Exception:
                    log.write(Text("usage: /max_tokens <positive integer>", style="system-msg"))
                else:
                    runtime.configure_model(get_config().model, max_tokens=value)
                    log.write(Text(f"max_tokens set to {value}", style="system-msg"))
            else:
                self.awaiting_max_tokens = True
                self._reset_module_state()
                log.write(Text("enter a positive integer for max_tokens", style="system-msg"))
            event.input.value = ""
            return True

        return False

    def _show_modules_list(self, log: RichLog) -> None:
        for idx, module_name in enumerate(runtime.MODULE_ORDER, start=1):
            label = runtime.MODULE_INFO[module_name]["label"]
            current = runtime.get_module_model(module_name)
            log.write(Text(f"{idx}. {module_name} ({label}) current={current}", style="system-msg"))

    def _handle_command(self, text: str, log: RichLog) -> bool:
        """Compat wrapper: route commands through a single handler."""
        from types import SimpleNamespace
        return self._route_command(text, log, SimpleNamespace(input=SimpleNamespace(value="")))

    # ---- small helpers to reduce CC in _process_job ----
    def _log_prompt(self, prompt: str, log: RichLog, dspy_log: RichLog, raw_log: RichLog) -> None:
        log.write(Text(f"▶ {prompt!r}", style="system-msg"))
        dspy_log.write(Text(f"▶ {prompt!r}", style="system-msg"))
        raw_log.write(f"▶ {prompt!r}")

    def _emit_step_logs(self, log: RichLog, dspy_log: RichLog, raw_log: RichLog, steps: List[Dict[str, Any]]) -> None:
        for step in steps:
            thought = step.get("thought", "")
            tool = step.get("tool", "")
            args = step.get("args", {})
            obs = step.get("observation", "")
            if thought:
                log.write(Text(f"🤔 {thought}", style="context-msg"))
                dspy_log.write(Text(f"🤔 {thought}", style="context-msg"))
            if tool and tool != "finish":
                log.write(Text(f"🔧 {tool} {args}", style="context-msg"))
                dspy_log.write(Text(f"🔧 {tool} {args}", style="context-msg"))
            if tool == "run_shell" and isinstance(obs, dict):
                self._emit_shell_step(log, dspy_log, obs)
            elif obs:
                log.write(Text(f"📥 {obs}", style="context-msg"))
                dspy_log.write(Text(f"📥 {obs}", style="context-msg"))

    def _emit_shell_step(self, log: RichLog, dspy_log: RichLog, obs: Dict[str, Any]) -> None:
        cmd = obs.get("command", "")
        log.write(Text(f"🖥️ command: {cmd}", style="context-msg"))
        dspy_log.write(Text(f"🖥️ command: {cmd}", style="context-msg"))
        safety = obs.get("safety")
        if isinstance(safety, dict):
            summary = "passed" if safety.get("passed") else f"blocked ({safety.get('detail', '')})"
            log.write(Text(f"🛡️ safety: {summary}", style="context-msg"))
            dspy_log.write(Text(f"🛡️ safety: {summary}", style="context-msg"))
        out = obs.get("output", "")
        if out:
            log.write(Text(f"📥 output: {out}", style="context-msg"))
            dspy_log.write(Text(f"📥 output: {out}", style="context-msg"))
        status = obs.get("status")
        if status:
            icon = "⚠️" if status != "ok" else "✅"
            log.write(Text(f"{icon} status: {status}", style="context-msg"))
            dspy_log.write(Text(f"{icon} status: {status}", style="context-msg"))

    def _emit_raw_history(self, raw_log: RichLog, raw_history: List[str]) -> None:
        for chunk in raw_history:
            raw_log.write(chunk)
        raw_log.write("")

    def _apply_updates_and_refresh(self, updates: List[MemorySlotUpdate] | None) -> None:
        if not updates:
            return
        self._active_modules.add("memory")
        self.apply_memory_updates(updates)
        self._refresh_memory_view()
        self.query_one("#memory", RichLog).scroll_end()

    def _emit_answer(self, log: RichLog, dspy_log: RichLog, answer: str) -> None:
        log.write(Text(f"✅ {answer}\n", style="answer-msg")); dspy_log.write(Text(f"✅ {answer}", style="answer-msg"))
        if isinstance(answer, str) and answer.strip():
            self._history.append({"role": "assistant", "content": answer.strip()})

    def _update_goals(self, prompt: str) -> None:
        goals, goal_error = self._run_goal_planner(prompt)
        if goals is not None:
            self._latest_goals = goals
            if goals.goals:
                self._active_modules.add("satisfaction_goals")
        else:
            self._latest_goals = InstrumentalGoals(goals=[])
        self._satisfaction_error = goal_error
        self._refresh_satisfaction_view()

    def _update_score(self) -> None:
        score_result, score_error = self._run_satisfaction_scorer()
        if score_result is not None:
            self._latest_score = score_result
            self._active_modules.add("satisfaction_score")
        self._satisfaction_error = score_error
        self._refresh_satisfaction_view()

    # Back-compat: keep the old combined helper as a thin wrapper
    def _update_satisfaction(self, prompt: str) -> None:  # pragma: no cover
        self._update_goals(prompt)
        self._update_score()

    def _set_layout(self, mode: str) -> None:
        content = self.query_one("#content", Horizontal)
        log = self.query_one("#log", RichLog)
        if mode == "stacked":
            content.add_class("stacked")
            log.add_class("stacked")
        else:
            content.remove_class("stacked")
            log.remove_class("stacked")

    def apply_memory_updates(self, updates: List[MemorySlotUpdate]) -> None:
        changed = False
        for update in updates:
            if update.action == "create" and update.content:
                self.memory_slots.append(update.content)
                changed = True
            elif update.action == "update" and update.slot is not None and update.content:
                if 0 <= update.slot < len(self.memory_slots):
                    self.memory_slots[update.slot] = update.content
                    changed = True
            elif update.action == "delete" and update.slot is not None:
                if 0 <= update.slot < len(self.memory_slots):
                    self.memory_slots.pop(update.slot)
                    changed = True
        if changed:
            save_memory_slots(self.memory_slots)

    def _label_panes(self) -> None:
        panes = {
            "#satisfaction": "Satisfaction",
            "#memory": "Memory",
            "#dspy": "DSPy History",
            "#raw": "DSPy Raw",
            "#log": "Agent Log",
        }
        for selector, title in panes.items():
            pane = self.query_one(selector, RichLog)
            pane.border_title = title
            pane.border_title_align = "left"

    def action_show_settings(self) -> None:
        overlay = SettingsOverlay(self._build_settings(), self._settings_changed)
        self.push_screen(overlay)

    def _build_settings(self) -> List[SettingDefinition]:
        models = list(runtime.MODEL_PRESETS.keys())

        def agent_model_get() -> str:
            return runtime.get_module_model("agent")

        def agent_model_set(value: str) -> None:
            runtime.configure_model(value)

        def max_tokens_get() -> int:
            cfg = get_config()
            return cfg.max_tokens or runtime.MODEL_PRESETS[agent_model_get()]["max_tokens"]

        def max_tokens_set(value: int) -> None:
            runtime.configure_model(agent_model_get(), max_tokens=value)

        def memory_model_get() -> str:
            return runtime.get_module_model("memory")

        def memory_model_set(value: str) -> None:
            runtime.configure_memory_model(value)

        def goals_model_get() -> str:
            return runtime.get_module_model("satisfaction_goals")

        def goals_model_set(value: str) -> None:
            runtime.configure_satisfaction_goals_model(value)

        def score_model_get() -> str:
            return runtime.get_module_model("satisfaction_score")

        def score_model_set(value: str) -> None:
            runtime.configure_satisfaction_score_model(value)

        return [
            SettingDefinition(
                key="agent_model",
                label="Agent Model",
                description="Language model used for the main agent loop.",
                getter=agent_model_get,
                setter=agent_model_set,
                options=models,
            ),
            SettingDefinition(
                key="max_tokens",
                label="Max Tokens",
                description="Upper bound on completion tokens for the agent model.",
                getter=max_tokens_get,
                setter=max_tokens_set,
                parser=int,
            ),
            SettingDefinition(
                key="memory_model",
                label="Memory Model",
                description="Model that summarizes interactions into memory slots.",
                getter=memory_model_get,
                setter=memory_model_set,
                options=models,
            ),
            SettingDefinition(
                key="goals_model",
                label="Goals Model",
                description="Model used to generate instrumental goals for satisfaction tracking.",
                getter=goals_model_get,
                setter=goals_model_set,
                options=models,
            ),
            SettingDefinition(
                key="score_model",
                label="Satisfaction Model",
                description="Model that scores progress against the current goals.",
                getter=score_model_get,
                setter=score_model_set,
                options=models,
            ),
        ]

    def _settings_changed(self) -> None:
        state = "Running" if self.running else "Idle"
        self._update_reasoning_label()
        self._set_status(state, running=self.running)

    def _refresh_memory_view(self) -> None:
        memory_log = self.query_one("#memory", RichLog)
        memory_log.clear()
        for idx, text in enumerate(self.memory_slots):
            memory_log.write(f"[{idx}] {text}")

    def _refresh_satisfaction_view(self) -> None:
        log = self.query_one("#satisfaction", RichLog)
        log.clear()
        if self._satisfaction_error:
            log.write(Text(f"⚠️ {self._satisfaction_error}", style="system-msg"))
        goals = self._latest_goals.goals if self._latest_goals else []
        if goals:
            log.write(Text("🎯 Goals:", style="system-msg"))
            for idx, goal in enumerate(goals, start=1):
                log.write(Text(f"{idx}. {goal}", style="agent-msg"))
        elif self._latest_goals is None:
            log.write(Text("🎯 Goals: planning…", style="system-msg"))
        else:
            log.write(Text("🎯 Goals: (none)", style="system-msg"))
        if self._latest_score is None:
            log.write(Text("🧭 Satisfaction: pending", style="system-msg"))
        else:
            log.write(Text(f"🧭 Satisfaction: {self._latest_score.score}/9", style="agent-msg"))
            if self._latest_score.rationale:
                log.write(Text(self._latest_score.rationale, style="agent-msg"))

    def _run_goal_planner(self, prompt: str) -> tuple[InstrumentalGoals | None, str | None]:
        try:
            goals = GOAL_PLANNER(
                user_message=prompt,
                chat_history=[dict(item) for item in self._history],
                memory_slots=list(self.memory_slots),
            )
            return goals, None
        except Exception as exc:  # pragma: no cover - defensive fallback
            return None, f"goal planner failed: {exc}"

    def _run_satisfaction_scorer(self) -> tuple[SatisfactionResult | None, str | None]:
        if self._latest_goals is None:
            return None, "no goals to score"
        try:
            result = SATISFACTION_SCORER(
                instrumental_goals=list(self._latest_goals.goals),
                chat_history=[dict(item) for item in self._history],
                memory_slots=list(self.memory_slots),
            )
            return result, None
        except Exception as exc:  # pragma: no cover - defensive fallback
            return None, f"scorer failed: {exc}"

    def _reset_module_state(self) -> None:
        self.awaiting_module_selection = False
        self.awaiting_module_model_choice = False
        self.selected_module = None

    def _start_request(self, prompt: str) -> None:
        self._active_modules = {"agent"}
        self._latest_goals = None
        self._latest_score = None
        self._satisfaction_error = None
        self._refresh_satisfaction_view()
        self._request_start = time.monotonic()
        if self._status_timer:
            self._status_timer.stop()
        self._set_status("Running", running=True, elapsed=0)
        self._set_spinner("⏳ working…")
        if self.is_running:
            self._status_timer = self.set_interval(1.0, self._update_status)
        else:
            self._status_timer = None

    def _update_status(self, timer: Timer | None = None) -> None:
        if self._request_start is None:
            return
        elapsed = int(time.monotonic() - self._request_start)
        self._set_status("Running", running=True, elapsed=elapsed)

    def _finish_request(self, success: bool, message: str | None = None) -> None:
        if self._status_timer:
            self._status_timer.stop()
            self._status_timer = None
        self._set_spinner("✅ done" if success else "❌ error")
        elapsed = int(time.monotonic() - self._request_start) if self._request_start else None
        state = "Completed" if success else "Failed"
        self._set_status(state, running=False, elapsed=elapsed, error=None if success else message)
        self._request_start = None
        self._active_modules.clear()

    def _set_status(
        self,
        state: str,
        *,
        running: bool = False,
        elapsed: int | None = None,
        error: str | None = None,
    ) -> None:
        models_summary = ", ".join(f"{name}={runtime.get_module_model(name)}" for name in runtime.MODULE_ORDER)
        modules_summary = ", ".join(sorted(self._active_modules)) if self._active_modules else "-"
        parts = [f"Models: {models_summary}", f"State: {state}"]
        if elapsed is not None:
            parts.append(f"Elapsed: {elapsed // 60:02d}:{elapsed % 60:02d}")
        parts.append(f"Modules: {modules_summary}")
        if error:
            parts.append(f"Error: {error}")
        status_text = " · ".join(parts)
        self.query_one("#status", Static).update(status_text)
        self._update_reasoning_label()
        self._update_spinner_timer(running)

    def _update_spinner_timer(self, running: bool) -> None:
        if running:
            if self._spinner_timer is None and self.is_running:
                self._spinner_timer = self.set_interval(0.1, self._tick_spinner)
        elif self._spinner_timer:
            self._spinner_timer.stop()
            self._spinner_timer = None

    def _set_spinner(self, text: Optional[str]) -> None:
        self._spinner_text_value = text or "Idle"
        self._spinner_index = 0
        spinner = self.query_one("#spinner", Static)
        if spinner is not None:
            spinner.update(self._spinner_text_value)

    def _spinner_text(self) -> Text:
        return Text(self._spinner_text_value, style="system-msg")

    def _tick_spinner(self) -> None:
        base = self._spinner_text_value.rstrip(" .-")
        frame = self._spinner_frame()
        message = f"{base} {frame}".strip()
        spinner = self.query_one("#spinner", Static)
        if spinner is not None:
            spinner.update(message)
        self._spinner_index = (self._spinner_index + 1) % len(self._spinner_frames())

    def _spinner_frame(self) -> str:
        return self._spinner_frames()[self._spinner_index]

    @staticmethod
    def _spinner_frames() -> List[str]:
        return ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def _update_reasoning_label(self) -> None:
        label = self.query_one("#reasoning", Static)
        label.update(self._reasoning_summary())

    def _reasoning_summary(self) -> str:
        model_key = runtime.get_module_model("agent")
        preset = runtime.MODEL_PRESETS.get(model_key, {})
        reasoning = preset.get("reasoning") or {}
        effort = reasoning.get("max_tokens")
        return f"Reasoning Effort: {effort}" if effort is not None else "Reasoning Effort: –"

    def _handle_shortcut(self, key: str, from_input: bool = False) -> bool:
        if from_input:
            if key == "escape":
                self.set_focus(None)
                return True
            return False
        if key in {"?", "question_mark"}:
            self.push_screen(HelpScreen())
            return True
        if key == "g":
            self._pending_g = True
            return True
        if key == "i" and self._pending_g:
            self._pending_g = False
            self.set_focus(self.query_one(Input))
            return True
        self._pending_g = False
        return False

    def on_key(self, event: Key) -> None:
        try:
            focused_widget = self.focused
        except ScreenStackError:
            focused_widget = None
        if self._handle_shortcut(event.key, isinstance(focused_widget, Input)):
            event.stop()
            return
        # Let Textual route the event normally; no private API calls.


    def _module_summary(self) -> str:
        return ", ".join(sorted(self._active_modules)) if self._active_modules else "-"
