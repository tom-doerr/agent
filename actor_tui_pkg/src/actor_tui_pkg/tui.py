"""Textual TUI for the actor-reviewer agent."""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from rich.text import Text
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widgets import Footer, RichLog, Static, TextArea

from .actors import InteractionActor, MemoryActor
from .config import get_config, load_config
from .dataset import list_examples, save_example, ReviewExample
from .dataset_views import DatasetBrowser
from .router import Router
from .tool_actor import ToolCallingActor
from .loop import Attempt, run_actor_reviewer_loop
from .memory import MemoryManager
from .reviewer import build_reviewer, ReviewResult
from .state import SystemState


@dataclass
class Job:
    id: str
    prompt: str


def format_chat_history(history: list[dict[str, str]]) -> str:
    lines = []
    for msg in history[-20:]:
        role = msg.get("role", "?")
        lines.append(f"{role}: {msg.get('content', '')}")
    return "\n".join(lines)


class ChatTextArea(TextArea):
    """TextArea where Enter submits and paste inserts normally."""

    class Submitted(Message):
        def __init__(self, text: str) -> None:
            super().__init__()
            self.text = text

    async def _on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            event.stop()
            event.prevent_default()
            text = self.text.strip()
            if text:
                self.post_message(self.Submitted(text))
            return
        await super()._on_key(event)


CSS = (
    "Screen { layout: vertical; background: #0f0b0d; color: #f7f1f2; } "
    "#top-bar { layout: horizontal; height: auto; min-height: 1; "
    "  background: #1a0c0d; padding: 0 1; } "
    "#status { width: 1fr; } "
    "#spinner { width: auto; } "
    "#in { height: 3; margin: 0 1; } "
    "#content { height: 1fr; layout: horizontal; } "
    "#side-pane { width: 1fr; min-width: 30; layout: vertical; } "
    "#side-pane > RichLog { border: solid #3b1416; padding: 0 1; } "
    "#log { width: 2fr; min-width: 40; border: solid #3b1416; padding: 0 1; } "
    ".user-msg { color: #ffffff; text-style: bold; } "
    ".agent-msg { color: #d3a4a6; text-style: italic; } "
    ".system-msg { color: #d3a4a6; } "
    ".answer-msg { color: #ff4d4f; text-style: bold; } "
    ".phase-msg { color: #5fafaf; } "
    ".attempt-msg { color: #888888; } "
    ".cmd-msg { color: #d4a647; } "
    ".cmd-out { color: #777777; } "
    ".pass-msg { color: #4ec94e; text-style: bold; } "
    ".fail-msg { color: #e05555; text-style: bold; } "
    ".mem-msg { color: #888888; text-style: italic; } "
)


class ActorTUI(App):
    CSS = CSS

    def __init__(self) -> None:
        super().__init__()
        self.q: asyncio.Queue[Job] = asyncio.Queue()
        self.cfg = load_config()
        self.memory_mgr = MemoryManager(Path(self.cfg.memory_path))
        self.history: list[dict[str, str]] = []
        self._last_reviews: list[tuple[str, ReviewResult]] = []
        self._request_start: Optional[float] = None
        self._status_timer = None
        self._phase: str = "idle"
        self._rebuild_reviewers()

    def _rebuild_reviewers(self) -> None:
        self.interaction_reviewer = build_reviewer(
            "interaction", Path(self.cfg.interaction_dataset_path)
        )
        self.memory_reviewer = build_reviewer(
            "memory", Path(self.cfg.memory_dataset_path)
        )
        self.tool_reviewer = build_reviewer(
            "tool", Path(self.cfg.tool_dataset_path)
        )

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Static("actor-tui | idle", id="status"),
            Static("", id="spinner"),
            id="top-bar",
        )
        yield ChatTextArea("", id="in")
        yield Horizontal(
            Vertical(
                RichLog(id="memory", wrap=True, auto_scroll=True),
                RichLog(id="reviews", wrap=True, auto_scroll=True),
                id="side-pane",
            ),
            RichLog(id="log", wrap=True, auto_scroll=True),
            id="content",
        )
        yield Footer()

    async def on_mount(self) -> None:
        asyncio.create_task(self._worker())
        self.query_one("#in", ChatTextArea).focus()
        self._label_panes()
        self._refresh_memory_view()
        self._refresh_reviews_view()

    def _label_panes(self) -> None:
        for sel, title in {
            "#memory": "Memory",
            "#reviews": "Reviews",
            "#log": "Chat",
        }.items():
            pane = self.query_one(sel, RichLog)
            pane.border_title = title
            pane.border_title_align = "left"

    BINDINGS = [("ctrl+d", "show_datasets", "Datasets")]

    async def on_chat_text_area_submitted(self, event: ChatTextArea.Submitted) -> None:
        text = event.text
        ta = self.query_one("#in", ChatTextArea)
        log = self.query_one("#log", RichLog)
        if self._handle_command(text, log):
            ta.clear()
            return
        log.write(Text(f">> {text}", style="user-msg"))
        log.scroll_end()
        self.history.append({"role": "user", "content": text})
        await self.q.put(Job(id=str(uuid.uuid4()), prompt=text))
        ta.clear()

    async def _worker(self) -> None:
        log = self.query_one("#log", RichLog)
        loop = asyncio.get_running_loop()
        while True:
            job = await self.q.get()
            self._start_request()
            try:
                await self._process_message(job, log, loop)
                self._finish_request(success=True)
            except Exception as exc:
                log.write(Text(f"Error: {exc}", style="system-msg"))
                self._finish_request(success=False)
            finally:
                self.q.task_done()

    async def _process_message(
        self, job: Job, log: RichLog, loop: asyncio.AbstractEventLoop
    ) -> None:
        state = SystemState(
            user_message=job.prompt,
            memory=self.memory_mgr.read(),
            chat_history=format_chat_history(self.history),
        )
        self._set_phase("Routing")
        route_result = await loop.run_in_executor(
            None, lambda: self._route(state),
        )
        route = route_result.route.strip().lower()
        log.write(Text(f"--- Route: {route} ---", style="phase-msg"))
        if route == "tool":
            actor_result = await self._run_tool_phase(state, log, loop)
        else:
            actor_result = await self._run_ia_phase(state, log, loop)
        reply = actor_result.final_output.reply
        log.write(Text(f"<< {reply}", style="answer-msg"))
        log.scroll_end()
        self.history.append({"role": "assistant", "content": reply})

        # Phase 2: Memory actor + reviewer
        state.assistant_reply = reply
        self._set_phase("Memory actor")
        mem_result = await loop.run_in_executor(
            None, lambda: self._run_memory(state, log),
        )

        edits = mem_result.final_output.edits or []
        if edits:
            _, diff = self.memory_mgr.apply_edits(edits)
            summary = getattr(mem_result.final_output, "summary", "")
            log.write(Text(f"  Memory: {summary}", style="mem-msg"))
        else:
            log.write(Text("  Memory: no changes", style="mem-msg"))
        self._collect_reviews(actor_result, mem_result)
        self._refresh_memory_view()
        self._refresh_reviews_view()

    def _route(self, state: SystemState):
        return Router()(state)

    async def _run_ia_phase(self, state, log, loop):
        self._set_phase("Interaction actor")
        return await loop.run_in_executor(
            None, lambda: self._run_interaction(state, log),
        )

    async def _run_tool_phase(self, state, log, loop):
        self._set_phase("Tool actor")
        return await loop.run_in_executor(
            None, lambda: self._run_tool(state, log),
        )

    def _run_interaction(self, state: SystemState, log: RichLog):
        m = self.cfg.max_review_iters
        return run_actor_reviewer_loop(
            actor=InteractionActor(),
            reviewer=self.interaction_reviewer,
            actor_name="interaction",
            state=state,
            max_iters=m,
            output_field="reply",
            on_actor_done=lambda i, p: self.call_from_thread(
                self._log_actor_output, "Interaction", i, m, p, log,
            ),
            on_attempt=lambda a: self.call_from_thread(
                self._log_review, "Interaction", a, log,
            ),
        )

    def _run_memory(self, state: SystemState, log: RichLog):
        m = self.cfg.max_review_iters
        return run_actor_reviewer_loop(
            actor=MemoryActor(),
            reviewer=self.memory_reviewer,
            actor_name="memory",
            state=state,
            max_iters=m,
            output_field="edits",
            on_actor_done=lambda i, p: self.call_from_thread(
                self._log_actor_output, "Memory", i, m, p, log,
            ),
            on_attempt=lambda a: self.call_from_thread(
                self._log_review, "Memory", a, log,
            ),
        )

    def _log_command(self, cmd: str, output: str, log: RichLog) -> None:
        log.write(Text(f"    $ {cmd}", style="cmd-msg"))
        truncated = output[:200]
        if len(output) > 200:
            truncated += "..."
        for line in truncated.splitlines():
            log.write(Text(f"    | {line}", style="cmd-out"))
        log.scroll_end()

    def _run_tool(self, state: SystemState, log: RichLog):
        m = self.cfg.max_review_iters
        cb = lambda c, o: self.call_from_thread(self._log_command, c, o, log)
        return run_actor_reviewer_loop(
            actor=ToolCallingActor(on_command=cb),
            reviewer=self.tool_reviewer,
            actor_name="tool",
            state=state,
            max_iters=m,
            output_field="reply",
            on_actor_done=lambda i, p: self.call_from_thread(
                self._log_actor_output, "Tool", i, m, p, log,
            ),
            on_attempt=lambda a: self.call_from_thread(
                self._log_review, "Tool", a, log,
            ),
        )

    def _log_actor_output(
        self, label: str, iteration: int, max_iters: int,
        prediction: object, log: RichLog,
    ) -> None:
        log.write(Text(f"  Attempt {iteration}/{max_iters}", style="attempt-msg"))
        reply = getattr(prediction, "reply", None)
        edits = getattr(prediction, "edits", None)
        if reply:
            log.write(Text(f"    Reply: {str(reply)[:200]}", style="agent-msg"))
        elif edits:
            log.write(Text(f"    Edits: {str(edits)[:200]}", style="agent-msg"))
        log.scroll_end()

    def _log_review(
        self, label: str, attempt: Attempt, log: RichLog,
    ) -> None:
        if attempt.review:
            r = attempt.review
            verdict = "PASS" if r.passed else "FAIL"
            style = "pass-msg" if r.passed else "fail-msg"
            log.write(Text(f"    {verdict} - {r.reasoning}", style=style))
            log.scroll_end()

    def _collect_reviews(self, *results) -> None:
        self._last_reviews = []
        for result in results:
            for a in result.attempts:
                if a.review:
                    self._last_reviews.append((result.actor_name, a.review))

    def _refresh_memory_view(self) -> None:
        pane = self.query_one("#memory", RichLog)
        pane.clear()
        content = self.memory_mgr.read()
        if content:
            for line in content.splitlines():
                pane.write(line)
        else:
            pane.write("(empty)")

    def _refresh_reviews_view(self) -> None:
        pane = self.query_one("#reviews", RichLog)
        pane.clear()
        for path_key, label in [
            (self.cfg.interaction_dataset_path, "Interaction"),
            (self.cfg.memory_dataset_path, "Memory"),
            (self.cfg.tool_dataset_path, "Tool"),
        ]:
            examples = list_examples(Path(path_key))
            pane.write(Text(f"-- {label} ({len(examples)}) --", style="system-msg"))
            for i, ex in enumerate(examples[-5:]):
                v = "PASS" if ex.passed else "FAIL"
                pane.write(f"  [{i}] {v}: {ex.reasoning[:80]}")

    def _handle_command(self, text: str, log: RichLog) -> bool:
        if text == "/reviews":
            self._refresh_reviews_view()
            log.write(Text("Reviews refreshed.", style="system-msg"))
            return True
        if text == "/samples":
            return self._cmd_samples(log)
        if text.startswith("/save"):
            return self._cmd_save(text, log)
        if text.startswith("/edit_review"):
            return self._cmd_edit_review(text, log)
        if text == "/datasets":
            self._open_datasets()
            return True
        return False

    def _cmd_samples(self, log: RichLog) -> bool:
        if not self._last_reviews:
            log.write(Text("No samples from last run.", style="system-msg"))
            return True
        for i, (name, r) in enumerate(self._last_reviews):
            v = "PASS" if r.passed else "FAIL"
            out = r.actor_output[:80]
            log.write(Text(f"  [{i}] {name}: {v} - {out}", style="system-msg"))
        log.write(Text("Use /save <idx> pass|fail [reasoning]", style="system-msg"))
        return True

    def _cmd_save(self, text: str, log: RichLog) -> bool:
        if text.strip() == "/save_all":
            return self._cmd_save_all(log)
        parts = text.split(maxsplit=3)
        if len(parts) < 3:
            log.write(Text("Usage: /save <idx> pass|fail [reasoning]", style="system-msg"))
            return True
        try:
            idx = int(parts[1])
            passed = parts[2].lower() == "pass"
            reasoning = parts[3] if len(parts) > 3 else None
        except (ValueError, IndexError):
            log.write(Text("Invalid args.", style="system-msg"))
            return True
        return self._do_save(idx, passed, reasoning, log)

    def _do_save(self, idx, passed, reasoning, log):
        if idx < 0 or idx >= len(self._last_reviews):
            log.write(Text("Index out of range.", style="system-msg"))
            return True
        name, r = self._last_reviews[idx]
        r = ReviewResult(
            reasoning=reasoning or r.reasoning,
            passed=passed,
            actor_inputs=r.actor_inputs,
            actor_output=r.actor_output,
        )
        self._save_one_review(name, r)
        self._rebuild_reviewers()
        self._refresh_reviews_view()
        log.write(Text(f"Saved [{idx}].", style="system-msg"))
        return True

    def _cmd_save_all(self, log: RichLog) -> bool:
        if not self._last_reviews:
            log.write(Text("No samples.", style="system-msg"))
            return True
        for name, r in self._last_reviews:
            self._save_one_review(name, r)
        n = len(self._last_reviews)
        self._rebuild_reviewers()
        self._refresh_reviews_view()
        log.write(Text(f"Saved {n} samples.", style="system-msg"))
        return True

    def _save_one_review(self, name: str, r: ReviewResult) -> None:
        path_map = {
            "interaction": self.cfg.interaction_dataset_path,
            "memory": self.cfg.memory_dataset_path,
            "tool": self.cfg.tool_dataset_path,
        }
        path = Path(path_map.get(name, self.cfg.interaction_dataset_path))
        ex = ReviewExample(
            actor_name=name,
            actor_inputs=r.actor_inputs,
            actor_output=r.actor_output,
            reasoning=r.reasoning,
            passed=r.passed,
        )
        save_example(path, ex)

    def _cmd_edit_review(self, text: str, log: RichLog) -> bool:
        from .dataset import update_example
        parts = text.split(maxsplit=3)
        if len(parts) < 3:
            log.write(Text(
                "Usage: /edit_review <idx> pass|fail [reasoning]",
                style="system-msg",
            ))
            return True
        try:
            idx = int(parts[1])
            passed = parts[2].lower() == "pass"
            reasoning = parts[3] if len(parts) > 3 else None
        except (ValueError, IndexError):
            log.write(Text("Invalid args.", style="system-msg"))
            return True
        path = Path(self.cfg.interaction_dataset_path)
        try:
            update_example(path, idx, reasoning=reasoning, passed=passed)
        except (IndexError, FileNotFoundError) as e:
            log.write(Text(f"Error: {e}", style="system-msg"))
            return True
        log.write(Text(f"Updated review {idx}.", style="system-msg"))
        self._rebuild_reviewers()
        self._refresh_reviews_view()
        return True

    def action_show_datasets(self) -> None:
        self._open_datasets()

    def _open_datasets(self) -> None:
        def on_dismiss(_result: None) -> None:
            self._rebuild_reviewers()
            self._refresh_reviews_view()
        self.push_screen(DatasetBrowser(self.cfg), callback=on_dismiss)

    def _set_phase(self, phase: str) -> None:
        self._phase = phase
        self._update_status_display()

    def _start_request(self) -> None:
        self._request_start = time.monotonic()
        self._phase = "starting"
        self._update_status_display()
        self._status_timer = self.set_interval(1.0, self._tick_status)

    def _tick_status(self) -> None:
        self._update_status_display()

    def _update_status_display(self) -> None:
        elapsed = ""
        if self._request_start:
            s = int(time.monotonic() - self._request_start)
            elapsed = f" {s}s"
        self.query_one("#status", Static).update(f"actor-tui | {self._phase}{elapsed}")

    def _finish_request(self, success: bool) -> None:
        if self._status_timer:
            self._status_timer.stop()
            self._status_timer = None
        elapsed = ""
        if self._request_start:
            s = int(time.monotonic() - self._request_start)
            elapsed = f" ({s}s)"
        label = "done" if success else "error"
        self._phase = "idle"
        self.query_one("#status", Static).update(f"actor-tui | {label}{elapsed}")
        self.query_one("#spinner", Static).update("")
        self._request_start = None
