"""Dataset browser modal for managing few-shot review examples."""

from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Static

from .config import AppConfig
from .dataset import delete_example, list_examples, update_example

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
            v = "PASS" if ex.passed else "FAIL"
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
