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
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Input, RichLog, Static

from .actors import InteractionActor, MemoryActor
from .config import get_config, load_config
from .dataset import list_examples, save_example, ReviewExample
from .loop import Attempt, run_actor_reviewer_loop
from .memory import MemoryManager
from .reviewer import build_reviewer, ReviewResult


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


CSS = (
    "Screen { layout: vertical; background: #0f0b0d; color: #f7f1f2; } "
    "#top-bar { layout: horizontal; height: auto; min-height: 1; "
    "  background: #1a0c0d; padding: 0 1; } "
    "#status { width: 1fr; } "
    "#spinner { width: auto; } "
    "#in { margin: 0 1; } "
    "#content { height: 1fr; layout: horizontal; } "
    "#side-pane { width: 1fr; min-width: 30; layout: vertical; } "
    "#side-pane > RichLog { border: solid #3b1416; padding: 0 1; } "
    "#log { width: 2fr; min-width: 40; border: solid #3b1416; padding: 0 1; } "
    ".user-msg { color: #f7f1f2; } "
    ".agent-msg { color: #d3a4a6; text-style: italic; } "
    ".system-msg { color: #d3a4a6; } "
    ".answer-msg { color: #ff4d4f; text-style: bold; } "
)


class ActorTUI(App):
    CSS = CSS

    def __init__(self) -> None:
        super().__init__()
        self.q: asyncio.Queue[Job] = asyncio.Queue()
        self.cfg = load_config()
        self.memory_mgr = MemoryManager(Path(self.cfg.memory_path))
        self.history: list[dict[str, str]] = []
        self._last_reviews: list[ReviewResult] = []
        self._request_start: Optional[float] = None
        self._status_timer = None
        self._rebuild_reviewers()

    def _rebuild_reviewers(self) -> None:
        self.interaction_reviewer = build_reviewer(
            "interaction", Path(self.cfg.interaction_dataset_path)
        )
        self.memory_reviewer = build_reviewer(
            "memory", Path(self.cfg.memory_dataset_path)
        )

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Static("actor-tui | idle", id="status"),
            Static("", id="spinner"),
            id="top-bar",
        )
        yield Input(placeholder="Type a message...", id="in")
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
        self.query_one(Input).focus()
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

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text:
            return
        log = self.query_one("#log", RichLog)
        if self._handle_command(text, log):
            event.input.value = ""
            return
        log.write(Text(f"You: {text}", style="user-msg"))
        log.scroll_end()
        self.history.append({"role": "user", "content": text})
        await self.q.put(Job(id=str(uuid.uuid4()), prompt=text))
        event.input.value = ""

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
        memory_text = self.memory_mgr.read()
        chat_str = format_chat_history(self.history)
        ia_kw = {
            "user_message": job.prompt,
            "memory": memory_text,
            "chat_history": chat_str,
        }
        ia_result = await loop.run_in_executor(
            None, lambda: self._run_interaction(ia_kw),
        )
        for a in ia_result.attempts:
            self._log_attempt("Interaction", a, log)
        reply = ia_result.final_output.reply
        log.write(Text(f"Assistant: {reply}", style="answer-msg"))
        log.scroll_end()
        self.history.append({"role": "assistant", "content": reply})

        # Phase 2: Memory actor + reviewer
        mem_kw = {
            "user_message": job.prompt,
            "assistant_reply": reply,
            "memory": memory_text,
        }
        mem_result = await loop.run_in_executor(
            None, lambda: self._run_memory(mem_kw),
        )
        for a in mem_result.attempts:
            self._log_attempt("Memory", a, log)

        edits = mem_result.final_output.edits or []
        if edits:
            _, diff = self.memory_mgr.apply_edits(edits)
            summary = getattr(mem_result.final_output, "summary", "")
            log.write(Text(f"Memory updated: {summary}", style="system-msg"))
        self._collect_reviews(ia_result, mem_result)
        self._refresh_memory_view()
        self._refresh_reviews_view()

    def _run_interaction(self, kwargs: dict):
        return run_actor_reviewer_loop(
            actor=InteractionActor(),
            reviewer=self.interaction_reviewer,
            actor_name="interaction",
            actor_kwargs=kwargs,
            max_iters=self.cfg.max_review_iters,
            output_field="reply",
        )

    def _run_memory(self, kwargs: dict):
        return run_actor_reviewer_loop(
            actor=MemoryActor(),
            reviewer=self.memory_reviewer,
            actor_name="memory",
            actor_kwargs=kwargs,
            max_iters=self.cfg.max_review_iters,
            output_field="edits",
        )

    def _log_attempt(self, label: str, attempt: Attempt, log: RichLog) -> None:
        out = str(
            getattr(attempt.actor_output, "reply", None)
            or getattr(attempt.actor_output, "edits", None)
            or attempt.actor_output
        )[:200]
        log.write(Text(f"  [{label} attempt {attempt.iteration}]", style="system-msg"))
        log.write(Text(f"    Output: {out}", style="agent-msg"))
        if attempt.review:
            r = attempt.review
            verdict = "PASS" if r.passed else "FAIL"
            style = "green" if r.passed else "red"
            log.write(Text(f"    Review: {verdict} - {r.reasoning}", style=style))
        log.scroll_end()

    def _collect_reviews(self, ia_result, mem_result) -> None:
        self._last_reviews = []
        for result in (ia_result, mem_result):
            for a in result.attempts:
                if a.review:
                    self._last_reviews.append(a.review)

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
        if text == "/add_review":
            return self._cmd_add_review(log)
        if text.startswith("/edit_review"):
            return self._cmd_edit_review(text, log)
        return False

    def _cmd_add_review(self, log: RichLog) -> bool:
        if not self._last_reviews:
            log.write(Text("No reviews to add.", style="system-msg"))
            return True
        for r in self._last_reviews:
            self._save_one_review(r)
        n = len(self._last_reviews)
        log.write(Text(f"Added {n} review(s).", style="system-msg"))
        self._rebuild_reviewers()
        self._refresh_reviews_view()
        return True

    def _save_one_review(self, r: ReviewResult) -> None:
        has_history = "chat_history" in r.actor_inputs
        name = "interaction" if has_history else "memory"
        path = Path(
            self.cfg.interaction_dataset_path
            if has_history else self.cfg.memory_dataset_path
        )
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

    def _start_request(self) -> None:
        self._request_start = time.monotonic()
        self.query_one("#status", Static).update("actor-tui | running...")
        self.query_one("#spinner", Static).update("...")

    def _finish_request(self, success: bool) -> None:
        elapsed = ""
        if self._request_start:
            s = int(time.monotonic() - self._request_start)
            elapsed = f" ({s}s)"
        label = "done" if success else "error"
        self.query_one("#status", Static).update(f"actor-tui | {label}{elapsed}")
        self.query_one("#spinner", Static).update("")
        self._request_start = None
