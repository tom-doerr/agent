#!/usr/bin/env python3
"""Simple Textual interface that prepends military time to submitted lines."""

from __future__ import annotations

from datetime import date, datetime
import re
from pathlib import Path
from typing import Optional

from textual import events
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Footer, Header, Input, Log, Static, Markdown

ARTIFACT_FILE = Path("artifact.md")
CONSTRAINTS_FILE = Path("constraints.md")
DATE_HEADING_RE = re.compile(r"^#\s*(\d{4}-\d{2}-\d{2})$")


class VimInput(Input):
    """Input widget that supports a small subset of Vim normal-mode commands."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._vim_normal = False
        self._pending_operator: Optional[str] = None
        self._pending_text_object: Optional[str] = None
        self._pending_count: int = 0
        self._count_active = False

    async def handle_key(self, event: events.Key) -> bool:  # type: ignore[override]
        key = event.key

        if self._vim_normal:
            if key == "escape":
                event.stop()
                event.prevent_default()
                self._reset_pending()
                return True
            if key == ".":
                self._repeat_delete()
                event.stop()
                event.prevent_default()
                return True
            handled = self._handle_normal_mode_key(event)
            if handled:
                return True
        else:
            if key == "escape":
                self._enter_normal_mode()
                event.stop()
                event.prevent_default()
                return True

        return await super().handle_key(event)

    async def _on_key(self, event: events.Key) -> None:  # type: ignore[override]
        if self._vim_normal:
            handled = self._handle_normal_mode_key(event)
            if handled:
                return
        await super()._on_key(event)

    def _handle_normal_mode_key(self, event: events.Key) -> bool:
        key = event.key

        if self._pending_text_object is not None:
            kind = self._pending_text_object + key
            self._apply_text_object(kind)
            event.stop()
            event.prevent_default()
            return True

        if key.isdigit():
            if not self._count_active and key == "0":
                self._apply_motion("0", 1)
                event.stop()
                event.prevent_default()
                return True
            self._pending_count = self._pending_count * 10 + int(key)
            self._count_active = True
            event.stop()
            event.prevent_default()
            return True

        if key in {"i", "I"} and self._pending_operator is None:
            self._vim_normal = False
            if key == "I":
                self.cursor_position = 0
            event.stop()
            event.prevent_default()
            self._reset_pending()
            return True

        if key == "a" and self._pending_operator is None:
            self._move_cursor(1)
            self._vim_normal = False
            event.stop()
            event.prevent_default()
            self._reset_pending()
            return True

        if key == "C" and self._pending_operator is None:
            self._pending_operator = "c"
            self._apply_operator_motion("$", self._get_count())
            event.stop()
            event.prevent_default()
            return True

        if key in {"d", "c"} and self._pending_operator is None:
            self._pending_operator = key
            event.stop()
            event.prevent_default()
            return True

        if self._pending_operator:
            if key in {"w", "b", "h", "l", "0", "$"}:
                self._apply_operator_motion(key, self._get_count())
                event.stop()
                event.prevent_default()
                return True
            if key in {"i", "a"}:
                self._pending_text_object = key
                event.stop()
                event.prevent_default()
                return True
            self._reset_pending()
            event.stop()
            event.prevent_default()
            return True

        if key == "h":
            self._move_cursor(-1)
        elif key == "l":
            self._move_cursor(1)
        elif key == "0":
            self.cursor_position = 0
        elif key == "$":
            self.cursor_position = len(self.value)
        elif key == "w":
            self.cursor_position = self._motion_word_forward(self.cursor_position, self._get_count())
        elif key == "b":
            self.cursor_position = self._motion_word_backward(self.cursor_position, self._get_count())
        elif key == "x":
            self._delete_under_cursor()
        else:
            return False

        event.stop()
        event.prevent_default()
        self._reset_pending()
        return True

    def _enter_normal_mode(self) -> None:
        self._vim_normal = True
        self._reset_pending()

    def _move_cursor(self, delta: int) -> None:
        new_pos = max(0, min(len(self.value), self.cursor_position + delta))
        self.cursor_position = new_pos

    def _delete_under_cursor(self) -> None:
        pos = self.cursor_position
        if pos >= len(self.value):
            return
        self.value = self.value[:pos] + self.value[pos + 1 :]

    def _get_count(self) -> int:
        return self._pending_count if self._pending_count else 1

    def _reset_pending(self) -> None:
        self._pending_operator = None
        self._pending_text_object = None
        self._pending_count = 0
        self._count_active = False

    def _apply_motion(self, motion: str, count: int) -> None:
        if motion == "0":
            self.cursor_position = 0
        elif motion == "$":
            self.cursor_position = len(self.value)
        elif motion == "h":
            self._move_cursor(-count)
        elif motion == "l":
            self._move_cursor(count)
        elif motion == "w":
            self.cursor_position = self._motion_word_forward(self.cursor_position, count)
        elif motion == "b":
            self.cursor_position = self._motion_word_backward(self.cursor_position, count)

    def _apply_operator_motion(self, motion: str, count: int) -> None:
        start = self.cursor_position
        end = start
        if motion == "h":
            end = max(0, start - count)
        elif motion == "l":
            end = min(len(self.value), start + count)
        elif motion == "w":
            end = self._motion_word_forward(start, count)
        elif motion == "b":
            end = self._motion_word_backward(start, count)
        elif motion == "0":
            end = 0
        elif motion == "$":
            end = len(self.value)
        else:
            self._reset_pending()
            return

        self._execute_operator(start, end)

    def _apply_text_object(self, obj: str) -> None:
        start, end = self._text_object_range(obj)
        if start is None or end is None:
            self._reset_pending()
            return
        self._execute_operator(start, end)

    def _execute_operator(self, start: int, end: int) -> None:
        if not self._pending_operator:
            self._reset_pending()
            return
        a, b = sorted((start, end))
        if a == b:
            self._reset_pending()
            return
        if self._pending_operator == "d":
            self.value = self.value[:a] + self.value[b:]
            self.cursor_position = min(a, len(self.value))
        elif self._pending_operator == "c":
            self.value = self.value[:a] + self.value[b:]
            self.cursor_position = min(a, len(self.value))
            self._vim_normal = False
        self._reset_pending()

    def _text_object_range(self, obj: str) -> tuple[Optional[int], Optional[int]]:
        if obj not in {"iw", "aw"}:
            return (None, None)
        start, end = self._word_bounds(self.cursor_position)
        if start is None or end is None:
            return (None, None)
        if obj == "aw":
            while end < len(self.value) and self.value[end].isspace():
                end += 1
            while start > 0 and self.value[start - 1].isspace():
                start -= 1
        return (start, end)

    def _word_bounds(self, pos: int) -> tuple[Optional[int], Optional[int]]:
        text = self.value
        if not text:
            return (None, None)
        cursor = min(max(pos, 0), len(text) - 1)
        if not self._is_word_char(text[cursor]):
            if cursor > 0 and self._is_word_char(text[cursor - 1]):
                cursor -= 1
            else:
                return (None, None)
        start = cursor
        while start > 0 and self._is_word_char(text[start - 1]):
            start -= 1
        end = cursor + 1
        while end < len(text) and self._is_word_char(text[end]):
            end += 1
        return start, end

    def _motion_word_forward(self, pos: int, count: int) -> int:
        cursor = pos
        for _ in range(count):
            cursor = self._skip_word_forward(cursor)
            cursor = self._skip_whitespace_forward(cursor)
        return min(cursor, len(self.value))

    def _motion_word_backward(self, pos: int, count: int) -> int:
        cursor = pos
        for _ in range(count):
            cursor = self._skip_whitespace_backward(cursor)
            cursor = self._skip_word_backward(cursor)
        return max(cursor, 0)

    def _skip_word_forward(self, pos: int) -> int:
        text = self.value
        cursor = pos
        length = len(text)
        if cursor < length and text[cursor].isspace():
            cursor = self._skip_whitespace_forward(cursor)
        while cursor < length and self._is_word_char(text[cursor]):
            cursor += 1
        return cursor

    def _skip_whitespace_forward(self, pos: int) -> int:
        text = self.value
        cursor = pos
        while cursor < len(text) and text[cursor].isspace():
            cursor += 1
        return cursor

    def _skip_whitespace_backward(self, pos: int) -> int:
        text = self.value
        cursor = max(0, pos - 1)
        while cursor > 0 and text[cursor].isspace():
            cursor -= 1
        if cursor == 0 and text[:1].isspace():
            return 0
        if cursor < len(text) and text[cursor].isspace():
            cursor = max(cursor - 1, 0)
        return cursor

    def _skip_word_backward(self, pos: int) -> int:
        text = self.value
        cursor = min(pos, len(text))
        if cursor > 0 and (cursor == len(text) or text[cursor].isspace()):
            cursor = self._skip_whitespace_backward(cursor)
        while cursor > 0 and self._is_word_char(text[cursor - 1]):
            cursor -= 1
        return cursor

    def _repeat_delete(self) -> None:
        # Simplistic dot command: repeat last delete/change motion with same operator and motion
        # Not fully implemented; placeholder to avoid errors.
        pass

    @staticmethod
    def _is_word_char(ch: str) -> bool:
        return ch.isalnum() or ch == "_"

class TimestampLogApp(App):
    """Collect free-form notes while prefixing each line with the current time."""

    CSS = """
    Screen {
        layout: vertical;
    }
    #artifact-container {
        padding: 1;
        border-bottom: solid $surface-lighten-2;
        height: 2fr;
    }
    #artifact-title {
        text-style: bold;
        padding-bottom: 1;
    }
    #artifact-status {
        color: $text-muted;
        padding-top: 0;
        padding-bottom: 0;
        text-align: right;
    }
    #artifact-view {
        height: 1fr;
        border: solid $surface-lighten-2;
        margin-bottom: 1;
    }
    #log-container {
        height: 1fr;
        padding: 1;
    }
    #input {
        margin: 0 1 1 1;
    }
    Log {
        border: solid $surface-lighten-2;
        padding: 1;
    }
    """

    BINDINGS = [
        ("ctrl+h", "toggle_help", "Help"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def __init__(
        self,
        *,
        artifact_path: Path | None = None,
        constraints_path: Path | None = None,
        artifact_refresh_seconds: float = 2.0,
    ) -> None:
        super().__init__()
        self._artifact_path = artifact_path or ARTIFACT_FILE
        self._constraints_path = constraints_path or CONSTRAINTS_FILE
        self._artifact_refresh_seconds = max(artifact_refresh_seconds, 0.1)
        self._artifact_mtime: Optional[float] = None
        self._artifact_timer = None
        self._last_constraints_date: Optional[date] = None
        self._artifact_status_message = "Artifact status: initializing…"
        self._pending_g = False  # for 'gi' shortcut

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="log-container"):
            yield Log(id="log")
        yield VimInput(placeholder="Type here and press Enter...", id="input")
        with Vertical(id="artifact-container"):
            yield Static("Artifact", id="artifact-title")
            yield Markdown(id="artifact-view")
            yield Static("Artifact status: initializing…", id="artifact-status")
        yield Static(self._help_text(), id="help-panel")
        yield Footer()

    def on_mount(self) -> None:
        self._artifact_view = self.query_one("#artifact-view", Markdown)
        self._artifact_title = self.query_one("#artifact-title", Static)
        self._artifact_status = self.query_one("#artifact-status", Static)
        self._log_widget = self.query_one("#log", Log)
        self._input = self.query_one("#input", Input)
        self._help_panel = self.query_one("#help-panel", Static)
        # Markdown is read-only by design; no extra setup needed
        self._log_widget.highlight = False
        self._log_widget.wrap = True
        self.set_focus(self._input)
        self._last_entry_date: date | None = None
        self._prepare_constraints()
        self.call_later(self._load_artifact)
        self._artifact_timer = self.set_interval(
            self._artifact_refresh_seconds,
            self._maybe_refresh_artifact,
        )
        self._artifact_status_timer = self.set_interval(
            1.0,
            self._update_artifact_status,
        )
        self._help_visible = True
        self._help_message = self._help_text()

    def _current_time(self) -> datetime:
        return datetime.now()

    def _format_line(self, message: str, current_time: datetime) -> str:
        timestamp = current_time.strftime("%H%M")
        return f"{timestamp} {message}"

    def on_input_submitted(self, event: Input.Submitted) -> None:
        message = event.value.strip()
        if not message:
            return
        current_time = self._current_time()
        current_date = current_time.date()
        if self._last_entry_date != current_date:
            self._log_widget.write_line(current_time.strftime("# %Y-%m-%d"))
            self._last_entry_date = current_date
        formatted_line = self._format_line(message, current_time)
        self._log_widget.write_line(formatted_line)
        self._append_to_constraints(current_date, formatted_line)
        self._input.value = ""

    def on_key(self, event: events.Key) -> None:  # minimal 'gi' shortcut
        # Only act when focus is NOT on the input box
        if getattr(self.focused, "id", None) == "input" or isinstance(self.focused, VimInput):
            self._pending_g = False
            return
        if event.key == "g":
            self._pending_g = True
            event.stop()
            return
        if event.key == "i" and self._pending_g:
            self.set_focus(self._input)
            self._pending_g = False
            event.stop()
            return
        # any other key cancels the sequence
        self._pending_g = False

    def _load_artifact(self) -> None:
        mtime: Optional[float] = None
        try:
            stat = self._artifact_path.stat()
        except FileNotFoundError:
            content = "(artifact not found)"
        except Exception as exc:  # pragma: no cover - unexpected failure
            content = f"(error reading artifact: {exc})"
        else:
            try:
                content = self._artifact_path.read_text(encoding="utf-8")
                mtime = stat.st_mtime
            except Exception as exc:  # pragma: no cover - unexpected failure
                content = f"(error reading artifact: {exc})"
                mtime = None

        self._artifact_mtime = mtime
        self._artifact_title.update(f"Artifact — {self._artifact_path}")
        self._artifact_view.update(content)
        self._update_artifact_status()

    def _maybe_refresh_artifact(self) -> None:
        try:
            stat = self._artifact_path.stat()
        except FileNotFoundError:
            if self._artifact_mtime is not None:
                self._artifact_mtime = None
                self._artifact_title.update(f"Artifact — {self._artifact_path}")
                self._artifact_view.update("(artifact not found)")
                self._update_artifact_status()
            return
        except Exception:  # pragma: no cover - diagnostics only
            return

        mtime = stat.st_mtime
        if self._artifact_mtime is None or mtime > self._artifact_mtime:
            self._load_artifact()
        else:
            self._update_artifact_status()

    def _update_artifact_status(self) -> None:
        if self._artifact_mtime is None:
            self._artifact_status_message = "Artifact status: not found"
            self._artifact_status.update(self._artifact_status_message)
            return
        delta = max(0, int((datetime.now() - datetime.fromtimestamp(self._artifact_mtime)).total_seconds()))
        if delta < 60:
            ago = f"{delta}s"
        elif delta < 3600:
            ago = f"{delta // 60}m {delta % 60}s"
        else:
            hours = delta // 3600
            minutes = (delta % 3600) // 60
            ago = f"{hours}h {minutes}m"
        self._artifact_status_message = f"Artifact updated {ago} ago"
        self._artifact_status.update(self._artifact_status_message)

    def _help_text(self) -> str:
        return (
            "Ctrl+H help  •  Ctrl+C exit  •  Enter submit  •  Esc/i Vim modes\n"
            "Notes append to constraints.md with YYYY-MM-DD headings"
        )

    def action_toggle_help(self) -> None:
        self._help_visible = not self._help_visible
        if self._help_visible:
            self._help_message = self._help_text()
            self._help_panel.update(self._help_message)
        self._help_panel.visible = self._help_visible
        if not self._help_visible:
            self._help_panel.update("")
            self._help_message = ""

    def _prepare_constraints(self) -> None:
        path = self._constraints_path
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            content = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            path.touch()
            content = ""
        self._last_constraints_date = self._extract_last_constraints_date(content)

    def _extract_last_constraints_date(self, text: str) -> Optional[date]:
        for line in reversed(text.splitlines()):
            match = DATE_HEADING_RE.match(line.strip())
            if match:
                try:
                    return datetime.strptime(match.group(1), "%Y-%m-%d").date()
                except ValueError:
                    continue
        return None

    def _append_to_constraints(self, current_date: date, formatted_line: str) -> None:
        path = self._constraints_path
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            existing = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            existing = ""

        date_str = current_date.strftime("%Y-%m-%d")
        needs_heading = self._last_constraints_date != current_date

        pieces: list[str] = []
        if existing and not existing.endswith("\n"):
            pieces.append("\n")
        if needs_heading:
            if existing and not existing.endswith("\n\n"):
                pieces.append("\n")
            pieces.append(f"# {date_str}\n")
        pieces.append(f"{formatted_line}\n")

        with path.open("a", encoding="utf-8") as fh:
            fh.write("".join(pieces))

        self._last_constraints_date = current_date


def _ensure_utf8_tty() -> None:
    """Fail fast if the terminal input/output isn't UTF-8 TTY.

    Textual's Linux driver decodes raw keyboard bytes as UTF-8. If the
    terminal isn't a real TTY, or if UTF-8 input isn't enabled, it can
    crash with UnicodeDecodeError. Keep behavior explicit rather than
    adding silent fallbacks.
    """
    import os
    import sys
    import subprocess

    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("timestamp_textual_app: requires an interactive UTF-8 terminal (stdin/stdout TTY).", file=sys.stderr)
        raise SystemExit(2)

    locale_hint = (os.environ.get("LC_ALL") or os.environ.get("LC_CTYPE") or os.environ.get("LANG") or "")
    if "utf" not in locale_hint.lower():
        print("Non-UTF-8 locale detected. Set LANG/LC_ALL to en_US.UTF-8 and run: stty iutf8", file=sys.stderr)
        raise SystemExit(2)

    try:
        proc = subprocess.run(["stty", "-a"], capture_output=True, text=True, check=False)
        if proc.returncode == 0:
            out = proc.stdout or ""
            has_flag = "iutf8" in out and "-iutf8" not in out
            if not has_flag:
                print("TTY UTF-8 input not enabled. Run: stty iutf8", file=sys.stderr)
                raise SystemExit(2)
    except Exception:
        # If stty isn't available or fails, continue; locale/TTY checks above still apply.
        pass


if __name__ == "__main__":
    _ensure_utf8_tty()
    TimestampLogApp().run()
