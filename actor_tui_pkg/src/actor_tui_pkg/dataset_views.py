"""Modals: dataset browser, help screen, samples screen."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Static

from .config import AppConfig
from .dataset import delete_example, list_examples, update_example
from .reviewer import ReviewResult

DATASET_CSS = (
    "DatasetBrowser { align: center middle; } "
    "#ds-outer { width: 90%; height: 85%; background: #1a0c0d; border: solid #3b1416; } "
    "#ds-title { text-align: center; text-style: bold; padding: 1; } "
    "#ds-tabs { height: auto; padding: 0 1; } "
    "#ds-table { height: 1fr; } "
    "#ds-actions { height: auto; padding: 1; } "
    "#ds-status { height: auto; padding: 0 1; color: #d3a4a6; } "
)

DATASETS = {
    "interaction": "interaction_dataset_path",
    "memory": "memory_dataset_path",
    "tool": "tool_dataset_path",
}


_HELP_CMDS = [
    ("/help", "Show this help"),
    ("/samples", "Browse last run samples"),
    ("/save N pass|fail [reason]", "Save sample"),
    ("/save_all", "Save all samples"),
    ("/edit_review N pass|fail [reason]", "Edit entry"),
    ("/reviews", "Refresh reviews pane"),
    ("/datasets", "Dataset browser"),
]
_HELP_KEYS = [("Enter", "Send"), ("Ctrl+D", "Datasets"), ("Ctrl+H", "Help")]


HELP_CSS = (
    "HelpScreen { align: center middle; } "
    "#help-outer { width: 60; height: auto; max-height: 80%;"
    " background: #1a0c0d; border: solid #3b1416; padding: 1 2; } "
    "#help-title { text-align: center; text-style: bold; color: #5fafaf; } "
)


class HelpScreen(ModalScreen[None]):
    CSS = HELP_CSS
    BINDINGS = [("escape", "dismiss", "Close")]

    def compose(self) -> ComposeResult:
        with Vertical(id="help-outer"):
            yield Static("Help", id="help-title")
            yield Static("", id="help-body")
            yield Button("Close", id="help-close")

    def on_mount(self) -> None:
        t = Text()
        t.append("Commands\n", "bold #5fafaf")
        for c, d in _HELP_CMDS:
            t.append(f"  {c:<30}", "#d4a647")
            t.append(f"{d}\n", "#d3a4a6")
        t.append("\nKeys\n", "bold #5fafaf")
        for k, d in _HELP_KEYS:
            t.append(f"  {k:<30}", "#f0a050")
            t.append(f"{d}\n", "#d3a4a6")
        self.query_one("#help-body", Static).update(t)

    def on_button_pressed(self, ev: Button.Pressed) -> None:
        if ev.button.id == "help-close":
            self.dismiss(None)


SAMP_CSS = (
    "SamplesScreen { align: center middle; } "
    "#samp-outer { width: 90%; height: 70%; background: #1a0c0d;"
    " border: solid #3b1416; } "
    "#samp-title { text-align: center; text-style: bold; color: #5fafaf; padding: 1; } "
    "#samp-table { height: 1fr; } "
    "#samp-actions { height: auto; padding: 1; } "
    "#samp-status { height: auto; padding: 0 1; color: #d3a4a6; } "
)


class SamplesScreen(ModalScreen[Optional[str]]):
    CSS = SAMP_CSS
    BINDINGS = [("escape", "dismiss", "Close")]

    def __init__(self, reviews):
        super().__init__()
        self._reviews = reviews

    def compose(self) -> ComposeResult:
        with Vertical(id="samp-outer"):
            yield Static("Samples", id="samp-title")
            yield DataTable(id="samp-table", zebra_stripes=True, cursor_type="row")
            with Horizontal(id="samp-actions"):
                yield Button("Save Pass", id="samp-pass", variant="success")
                yield Button("Save Fail", id="samp-fail", variant="error")
                yield Button("Save All", id="samp-all", variant="warning")
                yield Button("Close", id="samp-close")
            yield Static("", id="samp-status")

    def on_mount(self) -> None:
        tbl = self.query_one("#samp-table", DataTable)
        tbl.add_columns("#", "Actor", "Verdict", "Output")
        for i, (name, r) in enumerate(self._reviews):
            v = Text("PASS", "bold #4ec94e") if r.passed else Text("FAIL", "bold #e05555")
            tbl.add_row(str(i), name, v, r.actor_output[:60])
        st = self.query_one("#samp-status", Static)
        st.update(f"{len(self._reviews)} samples")

    def _sel_idx(self) -> int | None:
        tbl = self.query_one("#samp-table", DataTable)
        if tbl.row_count == 0:
            return None
        rk, _ = tbl.coordinate_to_cell_key(tbl.cursor_coordinate)
        return int(tbl.get_row(rk)[0])

    def on_button_pressed(self, ev: Button.Pressed) -> None:
        bid = ev.button.id
        if bid == "samp-close":
            self.dismiss(None)
        elif bid == "samp-pass":
            idx = self._sel_idx()
            if idx is not None:
                self.dismiss(f"save:{idx}:pass")
        elif bid == "samp-fail":
            idx = self._sel_idx()
            if idx is not None:
                self.dismiss(f"save:{idx}:fail")
        elif bid == "samp-all":
            self.dismiss("save_all")


class DatasetBrowser(ModalScreen[None]):
    """Modal for browsing and editing review datasets."""

    CSS = DATASET_CSS
    BINDINGS = [("escape", "dismiss", "Close")]

    def __init__(self, cfg: AppConfig) -> None:
        super().__init__()
        self.cfg = cfg
        self._active = "interaction"

    def compose(self) -> ComposeResult:
        with Vertical(id="ds-outer"):
            yield Static("Dataset Browser", id="ds-title")
            with Horizontal(id="ds-tabs"):
                yield Button("Interaction", id="ds-btn-interaction", variant="primary")
                yield Button("Memory", id="ds-btn-memory")
                yield Button("Tool", id="ds-btn-tool")
            yield DataTable(id="ds-table", zebra_stripes=True, cursor_type="row")
            with Horizontal(id="ds-actions"):
                yield Button("Toggle", id="ds-toggle", variant="warning")
                yield Button("Delete", id="ds-delete", variant="error")
                yield Button("Close", id="ds-close")
            yield Static("", id="ds-status")

    def on_mount(self) -> None:
        table = self.query_one("#ds-table", DataTable)
        table.add_columns("#", "Passed", "Reasoning", "Output")
        self._refresh_table()

    @property
    def _path(self) -> Path:
        attr = DATASETS[self._active]
        return Path(getattr(self.cfg, attr))

    def _refresh_table(self) -> None:
        table = self.query_one("#ds-table", DataTable)
        table.clear()
        examples = list_examples(self._path)
        for i, ex in enumerate(examples):
            v = Text("PASS", "bold #4ec94e") if ex.passed else Text("FAIL", "bold #e05555")
            table.add_row(str(i), v, ex.reasoning[:60], ex.actor_output[:40])
        status = self.query_one("#ds-status", Static)
        status.update(f"{self._active}: {len(examples)} examples")

    def _switch_tab(self, name: str) -> None:
        self._active = name
        for key in DATASETS:
            btn = self.query_one(f"#ds-btn-{key}", Button)
            btn.variant = "primary" if key == name else "default"
        self._refresh_table()

    def _selected_index(self) -> int | None:
        table = self.query_one("#ds-table", DataTable)
        if table.row_count == 0:
            return None
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        row = table.get_row(row_key)
        return int(row[0])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "ds-btn-interaction":
            self._switch_tab("interaction")
        elif bid == "ds-btn-memory":
            self._switch_tab("memory")
        elif bid == "ds-btn-tool":
            self._switch_tab("tool")
        elif bid == "ds-toggle":
            self._toggle_selected()
        elif bid == "ds-delete":
            self._delete_selected()
        elif bid == "ds-close":
            self.dismiss(None)

    def _toggle_selected(self) -> None:
        idx = self._selected_index()
        if idx is None:
            return
        examples = list_examples(self._path)
        if idx >= len(examples):
            return
        new_passed = not examples[idx].passed
        update_example(self._path, idx, passed=new_passed)
        self._refresh_table()

    def _delete_selected(self) -> None:
        idx = self._selected_index()
        if idx is None:
            return
        try:
            delete_example(self._path, idx)
        except (IndexError, FileNotFoundError):
            pass
        self._refresh_table()
