from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass
import time
from typing import Any, Dict, List, Optional, Set

from rich.text import Text
from textual.app import App, ComposeResult, ScreenStackError
from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.timer import Timer
from textual.widgets import Footer, Input, RichLog, Static

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


class TUI(App):
    CSS = (
        "Screen { layout: vertical; } "
        "#status { padding: 0 1; border: solid $boost; } "
        "#content { height: 1fr; layout: horizontal; } "
        "#side-pane { width: 1fr; layout: vertical; } "
        "#satisfaction { height: 1fr; border: solid $accent; padding: 0 1; } "
        "#memory { height: 1fr; border: solid $accent; padding: 0 1; } "
        "#log { width: 2fr; border: solid $accent; padding: 0 1; } "
        ".user-msg { color: $success; } "
        ".agent-msg { color: $warning; } "
        ".system-msg { color: $text-muted; } "
        ".answer-msg { color: $accent; text-style: bold; } "
        ".context-msg { color: $boost; text-style: italic; }"
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
        yield Static(id="status")
        yield Static(id="spinner")
        yield Input(
            placeholder="Ask anything (e.g., 'What files are here? Use ls(\".\")'). Press Enter…",
            id="in",
        )
        yield Horizontal(
            Vertical(
                RichLog(id="satisfaction", wrap=True, auto_scroll=True),
                RichLog(id="memory", wrap=True, auto_scroll=True),
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
        self._set_status("Idle")
        self._set_spinner(None)

    async def _process_job(self, job: Job, log: RichLog, loop: asyncio.AbstractEventLoop) -> None:
        jid = job.id[:8]
        log.write(Text(f"▶ {job.prompt!r}", style="system-msg"))

        def run_agent() -> Dict[str, Any]:
            return runtime.AGENT.run(job.prompt)

        result = await loop.run_in_executor(None, run_agent)
        for step in result["steps"]:
            thought = step.get("thought", "")
            tool = step.get("tool", "")
            args = step.get("args", {})
            obs = step.get("observation", "")
            if thought:
                log.write(Text(f"🤔 {thought}", style="context-msg"))
            if tool and tool != "finish":
                log.write(Text(f"🔧 {tool} {args}", style="context-msg"))
            if tool == "run_shell" and isinstance(obs, dict):
                cmd = obs.get("command", "")
                log.write(Text(f"🖥️ command: {cmd}", style="context-msg"))
                safety = obs.get("safety")
                if isinstance(safety, dict):
                    summary = "passed" if safety.get("passed") else f"blocked ({safety.get('detail', '')})"
                    log.write(Text(f"🛡️ safety: {summary}", style="context-msg"))
                out = obs.get("output", "")
                if out:
                    log.write(Text(f"📥 output: {out}", style="context-msg"))
                status = obs.get("status")
                if status:
                    icon = "⚠️" if status != "ok" else "✅"
                    log.write(Text(f"{icon} status: {status}", style="context-msg"))
            elif obs:
                log.write(Text(f"📥 {obs}", style="context-msg"))

        updates = await loop.run_in_executor(None, lambda: MEMORY_MODULE(prompt=job.prompt, steps=result["steps"]))
        if updates:
            self._active_modules.add("memory")
            self.apply_memory_updates(updates)
            self._refresh_memory_view()
            self.query_one("#memory", RichLog).scroll_end()

        answer = result.get("answer", "")
        log.write(Text(f"✅ {answer}\n", style="answer-msg"))
        if isinstance(answer, str) and answer.strip():
            self._history.append({"role": "assistant", "content": answer.strip()})

        goals, goal_error = await asyncio.to_thread(self._run_goal_planner, job.prompt)
        if goals is not None:
            self._latest_goals = goals
            if goals.goals:
                self._active_modules.add("satisfaction_goals")
        else:
            self._latest_goals = InstrumentalGoals(goals=[])
        self._satisfaction_error = goal_error
        self._refresh_satisfaction_view()

        score_result, score_error = await asyncio.to_thread(self._run_satisfaction_scorer)
        if score_result is not None:
            self._latest_score = score_result
            self._active_modules.add("satisfaction_score")
        self._satisfaction_error = score_error
        self._refresh_satisfaction_view()

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
                jid = job.id[:8]
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

        log.write(Text(text, style="user-msg"))
        log.scroll_end()

        if self.awaiting_module_model_choice and self.selected_module:
            choice = text.lower()
            if choice in runtime.MODEL_PRESETS:
                configure_name = runtime.MODULE_INFO[self.selected_module]["configure"]
                configure_fn = getattr(runtime, configure_name)
                configure_fn(choice)
                log.write(Text(f"{self.selected_module} model set to {choice}", style="system-msg"))
                self._reset_module_state()
            else:
                log.write(Text(f"unknown model '{text}'. choose from: {', '.join(runtime.MODEL_PRESETS)}", style="system-msg"))
            event.input.value = ""
            return

        if self.awaiting_module_selection:
            choice = text.lower()
            module_name: Optional[str] = None
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(runtime.MODULE_ORDER):
                    module_name = runtime.MODULE_ORDER[index]
            elif choice in runtime.MODULE_INFO:
                module_name = choice
            if module_name is None:
                log.write(Text(f"unknown module '{text}'. choose from: {', '.join(runtime.MODULE_ORDER)}", style="system-msg"))
                event.input.value = ""
                return
            self.awaiting_module_selection = False
            self.awaiting_module_model_choice = True
            self.selected_module = module_name
            current = runtime.get_module_model(module_name)
            log.write(
                f"choose model for {module_name} ({', '.join(runtime.MODEL_PRESETS)}). current={current}",
                style="system-msg",
            )
            event.input.value = ""
            return

        if self.awaiting_max_tokens:
            try:
                value = int(text)
                if value <= 0:
                    raise ValueError
            except ValueError:
                log.write(Text("enter a positive integer for max_tokens", style="system-msg"))
            else:
                runtime.configure_model(get_config().model, max_tokens=value)
                self.awaiting_max_tokens = False
                log.write(Text(f"max_tokens set to {value}", style="system-msg"))
            event.input.value = ""
            return

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
            return

        if text == "/modules":
            self.awaiting_model_choice = False
            self.awaiting_max_tokens = False
            self._reset_module_state()
            self.awaiting_module_selection = True
            for idx, module_name in enumerate(runtime.MODULE_ORDER, start=1):
                label = runtime.MODULE_INFO[module_name]["label"]
                current = runtime.get_module_model(module_name)
                log.write(Text(f"{idx}. {module_name} ({label}) current={current}", style="system-msg"))
            event.input.value = ""
            return

        if text == "/model":
            options = ", ".join(runtime.MODEL_PRESETS)
            log.write(Text(f"choose model ({options}). current={get_config().model}", style="system-msg"))
            self.awaiting_model_choice = True
            self._reset_module_state()
            event.input.value = ""
            return

        if text.startswith("/max_tokens"):
            parts = text.split()
            if len(parts) == 2:
                try:
                    value = int(parts[1])
                    if value <= 0:
                        raise ValueError
                except ValueError:
                    log.write(Text("usage: /max_tokens <positive integer>", style="system-msg"))
                else:
                    runtime.configure_model(get_config().model, max_tokens=value)
                    log.write(Text(f"max_tokens set to {value}", style="system-msg"))
            else:
                self.awaiting_max_tokens = True
                self._reset_module_state()
                log.write(Text("enter a positive integer for max_tokens", style="system-msg"))
            event.input.value = ""
            return

        self._history.append({"role": "user", "content": text})
        await self.q.put(Job(id=str(uuid.uuid4()), prompt=text))
        event.input.value = ""

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
        handled = self._handle_shortcut(event.key, isinstance(focused_widget, Input))
        if handled:
            event.stop()
            return
        try:
            screen = self.screen
        except ScreenStackError:
            screen = None
        if screen is not None:
            screen._forward_event(event)


    def _module_summary(self) -> str:
        return ", ".join(sorted(self._active_modules)) if self._active_modules else "-"
