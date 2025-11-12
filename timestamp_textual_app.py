#!/usr/bin/env python3
"""Simple Textual interface that prepends military time to submitted lines."""

from __future__ import annotations

from datetime import date, datetime
import os
import sys
import codecs

_lenient_warned = False
import re
from pathlib import Path
from typing import Optional

from textual import events
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header, Input, Static, Markdown
from timestamp_vim_input import VimInput
from constraints_io import tail_lines as constraints_tail_lines
from file_lock import locked_file
from timestamp_app_core import (
    _ensure_utf8_tty,
    _maybe_enable_lenient_input,
    _parse_cli,
    md_preserve_lines as _core_md_preserve_lines,
    constraints_tail_from_height as _core_tail_from_height,
    scroll_end as _core_scroll_end,
    scroll_page_down as _core_scroll_page_down,
    scroll_page_up as _core_scroll_page_up,
)
from timestamp_app_core import TimestampLogApp as _CoreTimestampLogApp

ARTIFACT_FILE = Path("artifact.md")
CONSTRAINTS_FILE = Path("constraints.md")
DATE_HEADING_RE = re.compile(r"^#\s*(\d{4}-\d{2}-\d{2})$")

# Legacy _OldVimInput removed; app uses VimInput from timestamp_vim_input.py

class TimestampLogApp(_CoreTimestampLogApp):
    """Wrapper app: extends the core app with timers, vim shortcuts, and help toggles."""

    BINDINGS = [
        ("ctrl+h", "toggle_help", "Help"),  # some terminals map this to backspace
        ("f1", "toggle_help", "Help"),       # reliable alternative
        ("ctrl+c", "quit", "Quit"),
        ("pageup", "artifact_page_up", "Artifact Up"),
        ("pagedown", "artifact_page_down", "Artifact Down"),
    ]

    def __init__(
        self,
        *,
        artifact_path: Path | None = None,
        constraints_path: Path | None = None,
        artifact_refresh_seconds: float = 2.0,
        constraints_refresh_seconds: float = 2.0,
    ) -> None:
        super().__init__()
        self._artifact_path = artifact_path or ARTIFACT_FILE
        self._constraints_path = constraints_path or CONSTRAINTS_FILE
        self._artifact_refresh_seconds = max(artifact_refresh_seconds, 0.1)
        self._constraints_refresh_seconds = max(constraints_refresh_seconds, 0.1)
        self._artifact_mtime: Optional[float] = None
        self._artifact_timer = None
        self._constraints_mtime: Optional[float] = None
        self._constraints_timer = None
        self._last_constraints_date: Optional[date] = None
        self._artifact_status_message = "Artifact status: initializing…"
        self._pending_g = False  # for 'gi' shortcut

    # Compose/CSS are inherited from core

    def on_mount(self) -> None:
        # Let core wire up UI and initial loads
        super().on_mount()
        self._input = self.query_one("#input", Input)
        self._help_panel = self.query_one("#help-panel", Static)
        self.set_focus(self._input)
        self._last_entry_date: date | None = None
        self._prepare_constraints()
        self._artifact_timer = self.set_interval(
            self._artifact_refresh_seconds,
            self._maybe_refresh_artifact,
        )
        self._constraints_timer = self.set_interval(
            self._constraints_refresh_seconds,
            self._maybe_refresh_constraints,
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
            self._last_entry_date = current_date
        formatted_line = self._format_line(message, current_time)
        # Keep file clean; don't persist padding; update constraints file, then view
        self._append_to_constraints(current_date, formatted_line)
        self._load_constraints()
        self._input.value = ""

    def on_key(self, event: events.Key) -> None:  # minimal 'gi' / 'ga' shortcuts
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
        if event.key == "a" and self._pending_g:
            self.set_focus(self._artifact_view)
            self._pending_g = False
            event.stop()
            return
        # any other key cancels the sequence
        self._pending_g = False

    # _load_artifact is inherited (core handles status + markdown line breaks)

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

    # _load_constraints is inherited (core handles tail + markdown + scroll)

    def _maybe_refresh_constraints(self) -> None:
        try:
            stat = self._constraints_path.stat()
        except FileNotFoundError:
            if self._constraints_mtime is not None:
                self._constraints_mtime = None
                self._constraints_title.update(f"Constraints — {self._constraints_path}")
                self._constraints_view.update("(constraints not found)")
            return
        except Exception:
            return
        mtime = stat.st_mtime
        if self._constraints_mtime is None or mtime > self._constraints_mtime:
            self._load_constraints()

    # --- small helpers / overrides ---

    def _md_preserve_lines(self, text: str) -> str:
        # Convert newlines to explicit <br> in Markdown
        return text.replace("\n", "  \n")

    def _maybe_scroll_constraints_end(self) -> None:
        # Scroll unless the constraints view is focused or auto-scroll is disabled
        try:
            is_focused = self.focused is self._constraints_view  # type: ignore[comparison-overlap]
        except Exception:
            is_focused = False
        auto = getattr(self, "_auto_scroll", None)
        enabled = auto() if callable(auto) else (bool(auto) if auto is not None else True)
        if enabled and not is_focused:
            _core_scroll_end(self._constraints_view)

    # Override core behavior to add focus guard, while keeping old helper name for tests
    def _scroll_constraints_end(self) -> None:  # type: ignore[override]
        self._maybe_scroll_constraints_end()

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

    def action_artifact_page_down(self) -> None:
        view = getattr(self, "_artifact_view", None)
        if view is None:
            return
        _core_scroll_page_down(view)

    def action_artifact_page_up(self) -> None:
        view = getattr(self, "_artifact_view", None)
        if view is None:
            return
        _core_scroll_page_up(view)

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
        date_str = current_date.strftime("%Y-%m-%d")
        with locked_file(path, "a+") as fh:
            try:
                fh.seek(0)
                existing = fh.read()
            except Exception:
                existing = ""
            # snapshot before write
            try:
                from backups import ensure_backups  # local import to avoid startup cost
                ensure_backups(path, content=existing)
            except Exception:
                pass
            needs_heading = (self._last_constraints_date != current_date) and (f"# {date_str}" not in existing)
            from constraints_io import build_append_block
            fh.seek(0, 2)
            fh.write(build_append_block(existing, needs_heading, date_str, formatted_line))
        self._last_constraints_date = current_date




def main() -> None:
    import sys
    _parse_cli(sys.argv[1:])
    _ensure_utf8_tty()
    _maybe_enable_lenient_input()
    try:
        TimestampLogApp().run()
    except UnicodeDecodeError:
        print(
            "Textual received non-UTF-8 bytes from TTY. Ensure your terminal, keyboard/paste, and stty are UTF-8 (try: stty iutf8).",
            file=sys.stderr,
        )
        raise SystemExit(2)
    

def _parse_cli(argv: list[str]) -> None:  # wrapper to keep test import path stable
    from timestamp_app_core import _parse_cli as _core_parse
    _core_parse(argv)


# Wrapper adds a small 'stty iutf8' check expected by tests
def _ensure_utf8_tty() -> None:  # type: ignore[override]
    from timestamp_app_core import _ensure_utf8_tty as _core_tty
    import subprocess
    _core_tty()
    try:
        proc = subprocess.run(["stty", "-a"], capture_output=True, text=True, check=False)
        if proc.returncode == 0:
            out = proc.stdout or ""
            if "iutf8" not in out or "-iutf8" in out:
                print("TTY UTF-8 input not enabled. Run: stty iutf8", file=sys.stderr)
                raise SystemExit(2)
    except Exception:
        # If stty is unavailable, core checks already enforced UTF-8 TTY and locale
        pass


# Keep richer lenient-input behavior (warning + read patch) expected by tests
def _maybe_enable_lenient_input() -> None:  # type: ignore[override]
    if not os.environ.get("TIMESTAMP_LENIENT_INPUT"):
        return
    try:
        from textual.drivers import linux_driver as _ld  # type: ignore
    except Exception:
        return
    original_decode = getattr(_ld, "decode", None)
    utf8_dec = codecs.getincrementaldecoder("utf-8")()
    fallback_enc = os.environ.get("TEXTUAL_FALLBACK_ENCODING", "cp1252")

    def safe_decode(data: bytes, final: bool = False) -> str:  # type: ignore[override]
        global _lenient_warned
        try:
            return utf8_dec.decode(data, final)
        except UnicodeDecodeError:
            try:
                utf8_dec.reset()  # type: ignore[attr-defined]
            except Exception:
                pass
            if not _lenient_warned:
                print(
                    f"[timestamp_textual_app] lenient input enabled: falling back to {fallback_enc} for non-UTF-8 bytes.",
                    file=sys.stderr,
                )
                _lenient_warned = True
            try:
                return data.decode(fallback_enc, errors="replace")
            except Exception:
                return data.decode("latin-1", errors="replace")

    if callable(original_decode) and getattr(_ld, "decode", None) is not safe_decode:
        _ld.decode = safe_decode  # type: ignore[assignment]

    orig_read = getattr(_ld, "read", None)
    if callable(orig_read):
        def safe_read(fd: int, n: int) -> bytes:  # type: ignore[override]
            b = orig_read(fd, n)
            try:
                b.decode("utf-8")
                return b
            except UnicodeDecodeError:
                if not _lenient_warned:
                    print(
                        f"[timestamp_textual_app] lenient input: sanitizing bytes via {fallback_enc}→utf-8.",
                        file=sys.stderr,
                    )
                return (
                    b.decode(fallback_enc, errors="replace").encode("utf-8", errors="replace")
                )
        _ld.read = safe_read  # type: ignore[assignment]


if __name__ == "__main__":
    main()
