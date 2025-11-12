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
from textual.containers import Container, Vertical
from textual.widgets import Footer, Header, Input, Log, Static, Markdown
from timestamp_vim_input import VimInput
from constraints_io import tail_lines as constraints_tail_lines
from file_lock import locked_file

ARTIFACT_FILE = Path("artifact.md")
CONSTRAINTS_FILE = Path("constraints.md")
DATE_HEADING_RE = re.compile(r"^#\s*(\d{4}-\d{2}-\d{2})$")

# Legacy _OldVimInput removed; app uses VimInput from timestamp_vim_input.py

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
        overflow: auto;  /* allow scrolling when content overflows */
    }
    #constraints-container {
        height: 8;
        padding: 1;
    }
    #input {
        margin: 0 1 1 1;
    }
    #constraints-view {
        border: solid $surface-lighten-2;
        /* Give a 1-col right margin to avoid last-column clipping on some mobile SSH terminals */
        padding: 1 2;
        overflow: auto;
    }
    """

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
        # Default to auto-scroll unless disabled via env
        self._auto_scroll = os.environ.get("TIMESTAMP_AUTO_SCROLL", "1").lower() not in {"0", "false", "no"}
        self._last_constraints_date: Optional[date] = None
        self._artifact_status_message = "Artifact status: initializing…"
        self._pending_g = False  # for 'gi' shortcut

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="constraints-container"):
            yield Static("Constraints", id="constraints-title")
            yield Markdown(id="constraints-view")
        # Use external VimInput; keep old class around (unused) for clarity
        yield VimInput(placeholder="Type here and press Enter...", id="input")
        with Vertical(id="artifact-container"):
            yield Static("Artifact", id="artifact-title")
            yield Markdown(id="artifact-view")
            yield Static("Artifact status: initializing…", id="artifact-status")
        yield Static(self._help_text(), id="help-panel")
        yield Footer()

    def on_mount(self) -> None:
        self._artifact_view = self.query_one("#artifact-view", Markdown)
        self._constraints_view = self.query_one("#constraints-view", Markdown)
        self._artifact_title = self.query_one("#artifact-title", Static)
        self._constraints_title = self.query_one("#constraints-title", Static)
        self._artifact_status = self.query_one("#artifact-status", Static)
        self._input = self.query_one("#input", Input)
        self._help_panel = self.query_one("#help-panel", Static)
        # Markdown is read-only by design; no extra setup needed
        # Make artifact view focusable so it can be scrolled with keyboard
        try:
            self._artifact_view.can_focus = True
        except Exception:
            pass
        # Prefer showing the end of constraints by default, but allow scrolling when focused
        self._auto_scroll = os.environ.get("TIMESTAMP_AUTO_SCROLL", "1").lower() not in {"0", "false", "no"}
        self._pad_eol = os.environ.get("TIMESTAMP_PAD_EOL", "").lower() in {"1", "true", "yes"}
        # Allow overriding right padding to dodge last-column clipping on some terminals
        try:
            right_pad = int(os.environ.get("TIMESTAMP_RIGHT_MARGIN", "2"))
        except ValueError:
            right_pad = 2
        try:
            self._constraints_view.styles.padding = (1, right_pad, 1, 1)
        except Exception:
            pass
        self.set_focus(self._input)
        self._last_entry_date: date | None = None
        self._prepare_constraints()
        self.call_later(self._load_artifact)
        self.call_later(self._load_constraints)
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

    def _load_constraints(self) -> None:
        mtime: Optional[float] = None
        def _tail_text(text: str, lines: int) -> str:
            # Keep compatibility but prefer file-tail helper elsewhere
            if lines <= 0:
                return text
            parts = text.splitlines()
            if len(parts) <= lines:
                return text
            return "\n".join(parts[-lines:])
        try:
            stat = self._constraints_path.stat()
        except FileNotFoundError:
            content = "(constraints not found)"
        except Exception as exc:  # pragma: no cover - unexpected failure
            content = f"(error reading constraints: {exc})"
        else:
            try:
                # Tail via helper for consistency
                try:
                    tail = int(os.environ.get("TIMESTAMP_CONSTRAINTS_TAIL", "200"))
                except ValueError:
                    tail = 200
                lines = constraints_tail_lines(self._constraints_path, tail)
                content = "\n".join(lines)
                mtime = stat.st_mtime
            except Exception as exc:  # pragma: no cover
                content = f"(error reading constraints: {exc})"
                mtime = None
        # Respect newlines in Markdown by converting to explicit line breaks
        # (Markdown treats single newlines as soft wraps). Two trailing spaces
        # force a <br>, preserving the original line structure.
        content = content.replace("\n", "  \n")
        self._constraints_mtime = mtime
        self._constraints_title.update(f"Constraints — {self._constraints_path}")
        self._constraints_view.update(content)
        # Scroll to bottom by default unless user is actively browsing constraints
        try:
            is_constraints_focused = self.focused is self._constraints_view  # type: ignore[comparison-overlap]
        except Exception:
            is_constraints_focused = False
        if self._auto_scroll and not is_constraints_focused:
            try:
                self._constraints_view.scroll_end(animate=False)  # type: ignore[attr-defined]
            except Exception:
                pass

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
        for method, args in (
            ("scroll_page_down", {}),
            ("scroll_relative", {"y": 10}),
            ("scroll_end", {"animate": False}),
        ):
            try:
                getattr(view, method)(**args)
                break
            except Exception:
                continue

    def action_artifact_page_up(self) -> None:
        view = getattr(self, "_artifact_view", None)
        if view is None:
            return
        for method, args in (
            ("scroll_page_up", {}),
            ("scroll_relative", {"y": -10}),
            ("scroll_home", {"animate": False}),
        ):
            try:
                getattr(view, method)(**args)
                break
            except Exception:
                continue

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
            needs_heading = self._last_constraints_date != current_date and (f"# {date_str}" not in existing)
            pieces: list[str] = []
            if existing and not existing.endswith("\n"):
                pieces.append("\n")
            if needs_heading:
                if existing and not existing.endswith("\n\n"):
                    pieces.append("\n")
                pieces.append(f"# {date_str}\n")
            pieces.append(f"{formatted_line}\n")
            fh.seek(0, 2)
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

def _maybe_enable_lenient_input() -> None:
    """Optionally monkeypatch Textual's Linux driver decode to be lenient.

    Enabled when `TIMESTAMP_LENIENT_INPUT` is set in the environment.
    On UTF-8 decode errors, falls back to cp1252 (or `TEXTUAL_FALLBACK_ENCODING`).
    Keeps the code minimal and opt-in to avoid masking real issues by default.
    """
    if not os.environ.get("TIMESTAMP_LENIENT_INPUT"):
        return
    try:
        from textual.drivers import linux_driver as _ld  # type: ignore
    except Exception:
        return

    original_decode = getattr(_ld, "decode", None)
    if not callable(original_decode):
        original_decode = None

    utf8_dec = codecs.getincrementaldecoder("utf-8")()
    fallback_enc = os.environ.get("TEXTUAL_FALLBACK_ENCODING", "cp1252")

    def safe_decode(data: bytes, final: bool = False) -> str:  # type: ignore[override]
        global _lenient_warned
        try:
            return utf8_dec.decode(data, final)
        except UnicodeDecodeError:
            # Reset decoder to a clean state and decode lossy via fallback
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
                # As a last resort, map bytes 1:1 to Unicode code points
                return data.decode("latin-1", errors="replace")

    # Only patch once
    if original_decode is not None and getattr(_ld, "decode", None) is not safe_decode:
        _ld.decode = safe_decode  # type: ignore[assignment]

    # Also patch linux_driver.read to sanitize bytes before decode, in case the
    # driver binds the original decode at definition time.
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
                    # do not flip the global warn flag here; decode() may warn too
                return (
                    b.decode(fallback_enc, errors="replace")
                     .encode("utf-8", errors="replace")
                )
        _ld.read = safe_read  # type: ignore[assignment]


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


def _parse_cli(argv: list[str]) -> None:
    """Minimal flag parser to toggle lenient input.

    Flags:
      --lenient-input            Enable decode fallback inside Textual driver
      --fallback-encoding ENC    Fallback codec (default: cp1252)
    """
    try:
        import argparse
    except Exception:
        return
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--lenient-input", action="store_true")
    parser.add_argument("--fallback-encoding", dest="fallback", default=None)
    parser.add_argument("--right-margin", dest="right_margin", type=int, default=None)
    parser.add_argument("--no-auto-scroll", action="store_true")
    parser.add_argument("--constraints-tail", dest="constraints_tail", type=int, default=None)
    parser.add_argument("--pad-eol", action="store_true")
    # Ignore unknown flags so we stay minimal
    ns, _ = parser.parse_known_args(argv)
    if ns.lenient_input:
        os.environ.setdefault("TIMESTAMP_LENIENT_INPUT", "1")
    if ns.fallback:
        os.environ["TEXTUAL_FALLBACK_ENCODING"] = ns.fallback
    if ns.right_margin is not None:
        os.environ["TIMESTAMP_RIGHT_MARGIN"] = str(ns.right_margin)
    if ns.pad_eol:
        os.environ.setdefault("TIMESTAMP_PAD_EOL", "1")
    if ns.no_auto_scroll:
        os.environ["TIMESTAMP_AUTO_SCROLL"] = "0"
    if ns.constraints_tail is not None:
        os.environ["TIMESTAMP_CONSTRAINTS_TAIL"] = str(ns.constraints_tail)


if __name__ == "__main__":
    main()
