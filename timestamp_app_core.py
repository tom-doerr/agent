#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header, Input, Static, Markdown

from constraints_io import tail_lines as constraints_tail_lines
from timestamp_vim_input import VimInput

ARTIFACT_FILE = Path("artifact.md")
CONSTRAINTS_FILE = Path("constraints.md")


class TimestampLogApp(App):
    CSS = """
    Screen { layout: vertical; }
    #artifact-container { padding: 1; border-bottom: solid $surface-lighten-2; height: 2fr; }
    #artifact-title { text-style: bold; padding-bottom: 1; }
    #artifact-status { color: $text-muted; padding-top: 0; padding-bottom: 0; text-align: right; }
    #artifact-view { height: 1fr; border: solid $surface-lighten-2; margin-bottom: 1; overflow: auto; }
    #constraints-container { height: 8; padding: 1; }
    #input { margin: 0 1 1 1; }
    #constraints-view { border: solid $surface-lighten-2; padding: 1 2; overflow: auto; }
    """

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
        self._constraints_mtime: Optional[float] = None
        self._help_visible = True
        self._help_message = ""
        self._artifact_status_message = "Artifact status: initializing…"

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="constraints-container"):
            yield Static("Constraints", id="constraints-title")
            yield Markdown(id="constraints-view")
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
        self._artifact_view.can_focus = True
        self.set_focus(self._input)
        self._load_artifact()
        self._load_constraints()

    def _current_time(self) -> datetime:
        return datetime.now()

    def _help_text(self) -> str:
        return (
            "Ctrl+H help  •  Ctrl+C exit  •  Enter submit  •  Esc/i Vim modes\n"
            "Notes append to constraints.md with YYYY-MM-DD headings"
        )

    def _load_artifact(self) -> None:
        try:
            text = self._artifact_path.read_text(encoding="utf-8")
            stat = self._artifact_path.stat()
            self._artifact_mtime = stat.st_mtime
            self._artifact_title.update(f"Artifact — {self._artifact_path}")
            self._artifact_view.update(text.replace("\n", "  \n"))
            self._artifact_status_message = "Artifact updated"
            self.query_one("#artifact-status", Static).update(self._artifact_status_message)
        except Exception:
            self._artifact_view.update("(artifact not found)")

    def _load_constraints(self) -> None:
        try:
            stat = self._constraints_path.stat()
            env_tail = os.environ.get("TIMESTAMP_CONSTRAINTS_TAIL", "200")
            if str(env_tail).lower() == "auto":
                try:
                    height = int(getattr(getattr(self._constraints_view, "size", None), "height", 0))
                except Exception:
                    height = 0
                tail = max(height - 2, 1)
            else:
                try:
                    tail = int(env_tail)
                except ValueError:
                    tail = 200
            lines = constraints_tail_lines(self._constraints_path, tail)
            content = "\n".join(lines).replace("\n", "  \n")
            self._constraints_mtime = stat.st_mtime
            self._constraints_title.update(f"Constraints — {self._constraints_path}")
            self._constraints_view.update(content)
            auto = os.environ.get("TIMESTAMP_AUTO_SCROLL", "1").lower() not in {"0", "false", "no"}
            if auto:
                try:
                    self._constraints_view.scroll_end(animate=False)  # type: ignore[attr-defined]
                except Exception:
                    pass
        except FileNotFoundError:
            self._constraints_view.update("(constraints not found)")


def _ensure_utf8_tty() -> None:
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("timestamp_textual_app: requires an interactive UTF-8 terminal (stdin/stdout TTY).", file=sys.stderr)
        raise SystemExit(2)
    locale_hint = (os.environ.get("LC_ALL") or os.environ.get("LC_CTYPE") or os.environ.get("LANG") or "").lower()
    if "utf" not in locale_hint:
        print("Non-UTF-8 locale detected. Set LANG/LC_ALL to en_US.UTF-8 and run: stty iutf8", file=sys.stderr)
        raise SystemExit(2)


def _maybe_enable_lenient_input() -> None:
    if not os.environ.get("TIMESTAMP_LENIENT_INPUT"):
        return
    try:
        from textual.drivers import linux_driver as _ld  # type: ignore
    except Exception:
        return
    original_decode = getattr(_ld, "decode", None)
    if not callable(original_decode):
        return

    import codecs
    utf8_dec = codecs.getincrementaldecoder("utf-8")()
    fallback_enc = os.environ.get("TEXTUAL_FALLBACK_ENCODING", "cp1252")

    def safe_decode(data: bytes, final: bool = False) -> str:  # type: ignore[override]
        try:
            return utf8_dec.decode(data, final)
        except UnicodeDecodeError:
            try:
                utf8_dec.reset()  # type: ignore[attr-defined]
            except Exception:
                pass
            try:
                return data.decode(fallback_enc, errors="replace")
            except Exception:
                return data.decode("latin-1", errors="replace")

    _ld.decode = safe_decode  # type: ignore[assignment]


def _parse_cli(argv: list[str]) -> None:
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
