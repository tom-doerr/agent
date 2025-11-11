#!/usr/bin/env python3
"""Alternative Textual-based TUI for running NLCO iterations."""

from __future__ import annotations

import contextlib
from functools import partial
import io
import traceback
from pathlib import Path
from typing import Optional

import dspy
from rich.console import Console
from rich.panel import Panel
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.worker import Worker, WorkerState
from textual.widgets import Button, Footer, Header, Label, Static, TextArea, Input

try:  # Textual 0.50+ exposes Log at widgets namespace
    from textual.widgets import Log  # type: ignore
except ImportError:  # pragma: no cover - backwards compatibility
    from textual.widgets._log import Log  # type: ignore

from affect_module import AffectModule, AffectReport
from context_provider import create_context_string
from memory_module import MemoryModule
from metrics_utils import run_with_metrics
from planning_module import PlanningModule
from timewarrior_module import TimewarriorModule
from refiner_signature import RefineSignature, SystemState
from nootropics_log import load_recent_nootropics_lines

try:  # Optional MLflow support
    import mlflow
    from packaging.version import Version
except Exception:  # pragma: no cover - diagnostics only
    mlflow = None
    Version = None


CONSTRAINTS_FILE = Path("constraints.md")
ARTIFACT_FILE = Path("artifact.md")
MEMORY_FILE = Path("memory.md")
SHORT_TERM_PATH = Path("short_term_memory.md")
STRUCTURED_SCHEDULE_FILE = Path("structured_schedule.json")


def _sanitize_metric_name(name: str) -> str:
    import re

    return re.sub(r"[^a-z0-9_]+", "_", name.lower())


def _log_iteration_payload(
    iteration: int,
    affect_report: Optional[AffectReport],
    executive_summary: Optional[str],
) -> None:
    if affect_report:
        if affect_report.urgency:
            mlflow.log_param("affect_urgency", affect_report.urgency)
        if affect_report.emotions:
            mlflow.log_param("affect_emotions", ", ".join(affect_report.emotions))
        if affect_report.goal_scores:
            for goal, score in affect_report.goal_scores.items():
                metric_name = _sanitize_metric_name(f"goal_{goal}")
                mlflow.log_metric(metric_name, int(score), step=iteration)
    if executive_summary:
        mlflow.log_param("executive_summary", executive_summary[:250])
    mlflow.log_metric("iteration", iteration)


def log_iteration_to_mlflow(
    iteration: int,
    affect_report: Optional[AffectReport],
    executive_summary: Optional[str],
    *,
    mlflow_enabled: bool,
) -> None:
    if not mlflow_enabled or mlflow is None:
        return
    try:
        active_run = mlflow.active_run()
        if active_run is None:
            with mlflow.start_run(run_name=f"iteration-{iteration}"):
                _log_iteration_payload(iteration, affect_report, executive_summary)
        else:
            _log_iteration_payload(iteration, affect_report, executive_summary)
    except Exception:  # pragma: no cover - diagnostics only
        traceback.print_exc()


class NLCOTextualApp(App):
    """Interactive Textual UI that drives NLCO iterations."""

    CSS = """
    Screen {
        layout: vertical;
    }
    #controls {
        height: auto;
        padding: 1;
        border-bottom: solid $surface-lighten-2;
    }
    #constraints-pane {
        height: 12;
        padding: 1;
        border-bottom: solid $surface-lighten-2;
    }
    #constraints-log {
        height: 1fr;
        border: solid $surface-lighten-2;
        padding: 1;
    }
    #message-input-row {
        height: auto;
        padding-top: 1;
    }
    #message-input {
        width: 1fr;
        margin-right: 1;
    }
    #editor-row {
        height: 30;
        padding: 1;
        border-bottom: solid $surface-lighten-2;
        overflow: hidden;
    }
    .editor-container {
        width: 1fr;
        padding-right: 1;
    }
    .editor-container:last-child {
        padding-right: 0;
    }
    .editor-container .stage-title {
        padding-bottom: 1;
    }
    .editor-container TextArea {
        height: 1fr;
        border: solid $surface-lighten-2;
    }
    #stage-columns {
        height: 1fr;
    }
    .stage-container {
        height: 1fr;
        padding: 1;
        border-right: solid $surface-lighten-2;
    }
    .stage-container:last-child {
        border-right: none;
    }
    .stage-title {
        text-style: bold;
        padding-bottom: 1;
    }
    Log {
        height: 1fr;
        border: solid $surface-lighten-2;
        padding: 1;
    }
    #artifact-view {
        height: 1fr;
    }
    #context-view {
        border: solid $surface-lighten-2;
        padding: 1;
        height: auto;
        min-height: 6;
    }
    #summary-strip {
        padding: 0 1;
        height: auto;
        border-bottom: solid $surface-lighten-2;
    }
    """

    BINDINGS = [
        ("r", "run_iteration", "Run iteration"),
        ("ctrl+s", "save_editors", "Save editors"),
        ("ctrl+l", "clear_logs", "Clear logs"),
        ("q", "quit", "Quit"),
    ]

    is_running: reactive[bool] = reactive(False)
    iteration_counter: reactive[int] = reactive(0)

    def __init__(self) -> None:
        super().__init__()
        self._worker: Optional[Worker] = None
        self._mlflow_enabled = False
        self._constraint_messages: list[str] = []
        self._setup_language_models()
        self._configure_mlflow()

    # ------------------------------------------------------------------
    # Setup helpers
    # ------------------------------------------------------------------
    def _setup_language_models(self) -> None:
        self._primary_lm = dspy.LM("deepseek/deepseek-reasoner", max_tokens=40_000)
        dspy.configure(lm=self._primary_lm)
        self._support_lm = dspy.LM("deepseek/deepseek-chat", max_tokens=4_000, temperature=0)
        self._refiner = dspy.Predict(
            RefineSignature,
            instructions=(
                "Refine the artifact based on the critique while keeping any human-readable schedule narrative within the artifact text."
            ),
        )

    def _configure_mlflow(self) -> None:
        if mlflow is None:
            return
        try:
            mlflow.set_tracking_uri("http://localhost:5010")
            mlflow.set_experiment("nlco_iter")
            if Version is not None and Version(mlflow.__version__) >= Version("2.18.0"):
                try:
                    mlflow.dspy.autolog()
                except Exception:
                    pass
            self._mlflow_enabled = True
        except Exception:
            self._mlflow_enabled = False

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="summary-strip"):
            yield Label("Status: Ready", id="status-label")
            yield Label("Iterations: 0", id="iteration-label")
            mlflow_label = "MLflow: on" if self._mlflow_enabled else "MLflow: off"
            yield Label(mlflow_label, id="mlflow-label")
        with Horizontal(id="controls"):
            yield Button("Run iteration (r)", id="run-button", variant="success")
            yield Button("Save editors (Ctrl+S)", id="save-editors-button", variant="primary")
            yield Button("Clear logs (Ctrl+L)", id="clear-button", variant="warning")
        with Vertical(id="constraints-pane"):
            yield Label("Constraints (recent lines)", classes="stage-title")
            yield Log(id="constraints-log")
            with Horizontal(id="message-input-row"):
                yield Input(placeholder="Type a new constraint message…", id="message-input")
                yield Button("Send", id="send-message-button", variant="primary")
        with Horizontal(id="editor-row"):
            with Vertical(id="artifact-editor-pane", classes="editor-container"):
                yield Label("Artifact", classes="stage-title")
                yield TextArea(id="artifact-editor")
        with Horizontal(id="stage-columns"):
            with Vertical(classes="stage-container"):
                yield Label("Context", classes="stage-title")
                yield Static("", id="context-view")
                yield Label("Nootropics (last 72h)", classes="stage-title")
                yield Log(id="nootropics-log")
                yield Label("Timewarrior", classes="stage-title")
                yield Log(id="timewarrior-log")
                yield Label("Memory", classes="stage-title")
                yield Log(id="memory-log")
                yield Label("Planning", classes="stage-title")
                yield Log(id="planning-log")
            with Vertical(classes="stage-container"):
                yield Label("Affect", classes="stage-title")
                yield Log(id="affect-log")
                yield Label("Refinement", classes="stage-title")
                yield Log(id="refine-log")
                yield Label("Structured Schedule", classes="stage-title")
                yield Log(id="schedule-log")
            with Vertical(classes="stage-container"):
                yield Label("Artifact", classes="stage-title")
                yield Log(id="artifact-log")
                yield Label("Console Log", classes="stage-title")
                yield Log(id="console-log")
        yield Footer()

    # ------------------------------------------------------------------
    # Reactive watchers
    # ------------------------------------------------------------------
    def watch_is_running(self, running: bool) -> None:
        run_button = self.query_one("#run-button", Button)
        run_button.disabled = running
        status = "Running" if running else "Ready"
        self.query_one("#status-label", Label).update(f"Status: {status}")

    def watch_iteration_counter(self, count: int) -> None:
        self.query_one("#iteration-label", Label).update(f"Iterations: {count}")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    async def on_mount(self) -> None:  # noqa: D401 - event hook
        self._load_constraint_messages()
        self._load_artifact_editor()
        self._load_memory_log()
        self._load_nootropics_log()
        self.query_one("#message-input", Input).focus()

    def action_run_iteration(self) -> None:
        if self.is_running:
            return
        self._persist_artifact_editor()
        constraints_snapshot = self._get_constraints_text()
        self._persist_constraints_file(constraints_snapshot)
        self.iteration_counter += 1
        iteration_index = self.iteration_counter
        self.is_running = True
        self._clear_stage_views()
        self._append_console_log(f"Starting iteration {iteration_index}\n")
        work = partial(
            self._run_iteration,
            iteration_index=iteration_index,
            constraints_text=constraints_snapshot,
        )
        self._worker = self.run_worker(
            work,
            name=f"iteration-{iteration_index}",
            exclusive=True,
            thread=True,
            exit_on_error=False,
        )
        if self._worker is not None:
            if hasattr(self._worker, "finished"):
                self._worker.finished.connect(self._on_worker_finished)
                self._worker.error.connect(self._on_worker_error)

    def action_clear_logs(self) -> None:
        self.query_one("#console-log", Log).clear()

    def action_save_editors(self) -> None:
        self._persist_artifact_editor()
        self._persist_constraints_file()
        self._append_console_log("Editors saved to files.\n")

    async def action_quit(self) -> None:  # noqa: D401 - override default docstring
        await self.shutdown()

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "run-button":
            self.action_run_iteration()
        elif event.button.id == "clear-button":
            self.action_clear_logs()
        elif event.button.id == "save-editors-button":
            self.action_save_editors()
        elif event.button.id == "send-message-button":
            message_input = self.query_one("#message-input", Input)
            self._handle_new_message(message_input.value)
            message_input.value = ""
            message_input.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "message-input":
            self._handle_new_message(event.value)
            event.input.value = ""
            event.input.focus()

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:  # pragma: no cover - Textual dispatch
        if self._worker is None or event.worker is not self._worker:
            return
        if event.state is WorkerState.SUCCESS:
            self._on_worker_finished(event.worker)
        elif event.state is WorkerState.ERROR:
            self._on_worker_error(event.worker)

    def _on_worker_finished(self, _: Worker) -> None:
        self._append_console_log("Iteration finished.\n")
        self.is_running = False

    def _on_worker_error(self, worker: Worker) -> None:
        exc = worker.error
        if exc is None:
            return
        formatted = "".join(traceback.format_exception(exc))
        self._append_console_log(formatted)
        self.query_one("#status-label", Label).update("Status: Error")
        self.is_running = False

    # ------------------------------------------------------------------
    # Worker logic
    # ------------------------------------------------------------------
    def _run_iteration(self, *, iteration_index: int, constraints_text: str) -> None:
        buffer = io.StringIO()
        console = Console(file=buffer, record=True, force_terminal=True, color_system="truecolor", width=120)
        cursor = 0

        def consume_log() -> str:
            nonlocal cursor
            content = buffer.getvalue()
            if len(content) == cursor:
                return ""
            chunk = content[cursor:]
            cursor = len(content)
            return chunk

        def flush_log() -> None:
            text = consume_log()
            if text:
                self.call_from_thread(self._append_console_log, text)

        mlflow_run = None
        if self._mlflow_enabled and mlflow is not None:
            mlflow_run = mlflow.start_run(run_name=f"iteration-{iteration_index}")

        try:
            with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
                artifact = ARTIFACT_FILE.read_text()
                constraints = constraints_text
                context = create_context_string()
                _noo = load_recent_nootropics_lines()
                if _noo:
                    context += "\n\nNootropics (last 72h)\n" + "\n".join(_noo)
                self.call_from_thread(self._update_context, context)
                flush_log()

                time_module = TimewarriorModule(
                    self._support_lm,
                    console=console,
                    short_term_path=SHORT_TERM_PATH,
                )
                time_status = time_module.run(
                    artifact=artifact,
                    constraints=constraints,
                    context=context,
                )
                flush_log()
                self.call_from_thread(
                    self._update_stage_log,
                    "timewarrior",
                    time_status or "No change",
                )

                memory_module = MemoryModule(self._primary_lm, console=console)
                memory_feedback = memory_module.run(
                    artifact=artifact,
                    constraints=constraints,
                    context=context,
                )
                flush_log()
                self.call_from_thread(
                    self._update_stage_log,
                    "memory",
                    memory_feedback or "Memory unchanged",
                )

                planning_module = PlanningModule(self._support_lm, console=console)
                plan_feedback = planning_module.run(
                    artifact=artifact,
                    constraints=constraints,
                    context=context,
                )
                flush_log()
                self.call_from_thread(
                    self._update_stage_log,
                    "planning",
                    plan_feedback or "Plan unchanged",
                )

                affect_module = AffectModule(self._support_lm, console=console)
                affect_report = affect_module.run(
                    artifact=artifact,
                    constraints=constraints,
                    context=context,
                )
                flush_log()
                self.call_from_thread(
                    self._update_affect,
                    affect_report,
                )

                log_iteration_to_mlflow(
                    iteration_index,
                    affect_report,
                    executive_summary=None,
                    mlflow_enabled=self._mlflow_enabled,
                )

                try:
                    prev_mtime = ARTIFACT_FILE.stat().st_mtime
                except FileNotFoundError:
                    import datetime as _dt
                    prev_mtime = _dt.datetime.now().timestamp()
                import datetime as _dt
                _state = SystemState(
                    last_artifact_update=_dt.datetime.fromtimestamp(prev_mtime).isoformat(timespec="seconds")
                )

                refine_pred = run_with_metrics(
                    "Refiner",
                    self._refiner,
                    artifact=artifact,
                    constraints=constraints,
                    system_state=_state,
                    context=context,
                )
                refined = getattr(refine_pred, "refined_artifact", "")
                structured_schedule_display = "Structured schedule disabled."
                timeline_display = ""
                flush_log()
                self.call_from_thread(self._update_stage_log, "refine", refined)
                combined_schedule_display = f"{timeline_display}\n\n{structured_schedule_display}".strip()
                self.call_from_thread(
                    self._update_stage_log,
                    "schedule",
                    combined_schedule_display,
                )

                ARTIFACT_FILE.write_text(refined)
                self.call_from_thread(self._update_artifact_editor, refined)

        except Exception as exc:  # pragma: no cover - defensive
            flush_log()
            message = "".join(traceback.format_exception(exc))
            self.call_from_thread(self._append_console_log, message)
            raise
        finally:
            flush_log()
            if mlflow_run is not None:
                mlflow.end_run()

    # ------------------------------------------------------------------
    # UI update helpers (main thread only)
    # ------------------------------------------------------------------
    def _clear_stage_views(self) -> None:
        self.query_one("#nootropics-log", Log).clear()
        self.query_one("#timewarrior-log", Log).clear()
        self.query_one("#memory-log", Log).clear()
        self.query_one("#planning-log", Log).clear()
        self.query_one("#affect-log", Log).clear()
        self.query_one("#refine-log", Log).clear()
        self.query_one("#schedule-log", Log).clear()
        self.query_one("#artifact-log", Log).clear()
        self.query_one("#context-view", Static).update("")

    def _append_console_log(self, text: str) -> None:
        if not text:
            return
        log = self.query_one("#console-log", Log)
        for line in text.rstrip().splitlines():
            log.write(line)

    def _update_context(self, context: str) -> None:
        panel = Panel(context, title="Context", border_style="cyan")
        self.query_one("#context-view", Static).update(panel)

    def _update_stage_log(self, stage: str, content: str) -> None:
        if stage == "memory":
            self._update_memory_display(content)
            return

        widget_map = {
            "timewarrior": "#timewarrior-log",
            "planning": "#planning-log",
            "refine": "#refine-log",
            "schedule": "#schedule-log",
        }
        if stage not in widget_map:
            return
        widget = self.query_one(widget_map[stage], Log)
        widget.clear()
        if content:
            for line in content.rstrip().splitlines():
                widget.write(line)

    def _update_affect(self, report: Optional[AffectReport]) -> None:
        widget = self.query_one("#affect-log", Log)
        widget.clear()
        if report is None:
            widget.write("Affect report unavailable")
            return
        widget.write(f"Emotions: {', '.join(report.emotions) or 'neutral'}")
        widget.write(f"Urgency: {report.urgency}")
        widget.write(f"Confidence: {report.confidence}")
        if report.suggested_focus:
            widget.write(f"Suggested focus: {report.suggested_focus}")
        if report.rationale:
            widget.write("Rationale:")
            for line in report.rationale.splitlines():
                widget.write(f"  {line}")
        if report.goal_scores:
            widget.write("Goal scores:")
            for goal, score in report.goal_scores.items():
                widget.write(f"  {goal}: {score}")

    def _update_artifact(self, text: str) -> None:
        widget = self.query_one("#artifact-log", Log)
        widget.clear()
        if text:
            for line in text.rstrip().splitlines():
                widget.write(line)
        
    def _update_artifact_editor(self, text: str) -> None:
        editor = self.query_one("#artifact-editor", TextArea)
        editor.text = text
        self._update_artifact(text)

    def _load_memory_log(self) -> None:
        self._update_memory_display(None)

    def _load_nootropics_log(self) -> None:
        log = self.query_one("#nootropics-log", Log)
        log.clear()
        try:
            lines = load_recent_nootropics_lines()
        except Exception as exc:  # pragma: no cover - defensive
            log.write(f"<error loading nootropics log: {exc}>")
            return
        if not lines:
            log.write("<no entries in last 72h>")
            return
        for line in lines:
            log.write(line)

    def _update_memory_display(self, feedback: Optional[str]) -> None:
        log = self.query_one("#memory-log", Log)
        log.clear()
        try:
            memory_text = MEMORY_FILE.read_text() if MEMORY_FILE.exists() else ""
        except Exception as exc:  # pragma: no cover - defensive logging
            memory_text = f"<error reading memory: {exc}>"
        if memory_text.strip():
            for line in memory_text.splitlines():
                log.write(line or " ")
        else:
            log.write("<memory is empty>")
        if feedback:
            log.write("")
            log.write(f"Update: {feedback}")

    def _refresh_constraints_log(self) -> None:
        log = self.query_one("#constraints-log", Log)
        log.clear()
        # Show the last few lines from constraints.md to reflect external edits (e.g., TimestampLogApp)
        tail_lines = 40
        try:
            if not CONSTRAINTS_FILE.exists():
                log.write("No constraints yet.")
                return
            lines = CONSTRAINTS_FILE.read_text().splitlines()
            for line in lines[-tail_lines:]:
                log.write(line or " ")
        except Exception as exc:  # pragma: no cover - defensive
            log.write(f"<error reading constraints: {exc}>")

    def _handle_new_message(self, text: str) -> None:
        message = (text or "").strip()
        if not message:
            return
        self._constraint_messages.append(message)
        self._refresh_constraints_log()
        self._persist_constraints_file()
        self._append_console_log(f"Recorded constraint message #{len(self._constraint_messages)}.")

    def _get_constraints_text(self) -> str:
        return "\n\n".join(self._constraint_messages).strip()

    def _load_constraint_messages(self) -> None:
        self._constraint_messages.clear()
        if CONSTRAINTS_FILE.exists():
            raw = CONSTRAINTS_FILE.read_text().strip()
            if raw:
                segments = [segment.strip() for segment in raw.split("\n\n") if segment.strip()]
                self._constraint_messages.extend(segments)
        self._refresh_constraints_log()

    def _persist_constraints_file(self, text: Optional[str] = None) -> None:
        content = text if text is not None else self._get_constraints_text()
        CONSTRAINTS_FILE.write_text(content)

    def _load_artifact_editor(self) -> None:
        artifact_text = ARTIFACT_FILE.read_text() if ARTIFACT_FILE.exists() else ""
        editor = self.query_one("#artifact-editor", TextArea)
        editor.text = artifact_text
        self._update_artifact(artifact_text)

    def _persist_artifact_editor(self) -> None:
        artifact_editor = self.query_one("#artifact-editor", TextArea)
        ARTIFACT_FILE.write_text(artifact_editor.text or "")


def main() -> None:
    app = NLCOTextualApp()
    app.run()


if __name__ == "__main__":
    main()
