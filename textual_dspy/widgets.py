"""Reusable widgets for the Textual DSPy interface."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.widgets import Button, DataTable, Input, Label, Static, TextArea

from web_dspy_builder.models import EdgeSpec, NodeSpec


class NodeDetail(Container):
    """Form for editing a node specification and runtime overrides."""

    DEFAULT_CSS = """
    NodeDetail {
        width: 1fr;
        border: solid $surface;
        padding: 1;
    }
    NodeDetail > .field-label {
        text-style: bold;
        padding-top: 1;
    }
    NodeDetail TextArea {
        height: 8;
    }
    NodeDetail #apply-row {
        padding-top: 1;
        height: auto;
    }
    """

    node_id = reactive("", init=False)

    def compose(self) -> ComposeResult:
        yield Label("Node Detail", id="detail-title")
        yield Label("ID", classes="field-label")
        yield Input(id="detail-id", placeholder="node id", disabled=True)
        yield Label("Label", classes="field-label")
        yield Input(id="detail-label", placeholder="optional label")
        yield Label("Type", classes="field-label")
        yield Input(id="detail-type", placeholder="node type")
        yield Label("Input Ports (comma separated)", classes="field-label")
        yield Input(id="detail-inputs", placeholder="port1, port2")
        yield Label("Output Ports (comma separated)", classes="field-label")
        yield Input(id="detail-outputs", placeholder="port1, port2")
        yield Label("Config (JSON)", classes="field-label")
        yield TextArea(id="detail-config")
        yield Label("Override (JSON)", classes="field-label")
        yield TextArea(id="detail-override")
        with Horizontal(id="apply-row"):
            yield Button("Apply Node", id="apply-node", variant="success")
            yield Button("Queue Override", id="apply-override", variant="primary")
            yield Button("Clear Override", id="clear-override", variant="warning")

    def clear(self) -> None:
        self.node_id = ""
        self._set_field("detail-id", "")
        self._set_field("detail-label", "")
        self._set_field("detail-type", "")
        self._set_field("detail-inputs", "")
        self._set_field("detail-outputs", "")
        self._set_field("detail-config", "{}")
        self._set_field("detail-override", "{}")

    def display_node(self, node: NodeSpec, override: Optional[Dict[str, Any]] = None) -> None:
        self.node_id = node.id
        self._set_field("detail-id", node.id)
        self._set_field("detail-label", node.label or "")
        self._set_field("detail-type", node.type)
        self._set_field("detail-inputs", ", ".join(node.ports.inputs))
        self._set_field("detail-outputs", ", ".join(node.ports.outputs))
        config_text = json.dumps(node.config, indent=2, sort_keys=True)
        self._set_field("detail-config", config_text)
        override_text = json.dumps(override or {}, indent=2, sort_keys=True)
        self._set_field("detail-override", override_text)

    @property
    def current_override(self) -> Optional[Dict[str, Any]]:
        text = self._get_field("detail-override")
        try:
            return json.loads(text) if text.strip() else {}
        except json.JSONDecodeError:
            return None

    def gather_update(self) -> Optional[Dict[str, Any]]:
        """Return updated node attributes or ``None`` on parse errors."""

        if not self.node_id:
            return None
        config_text = self._get_field("detail-config")
        try:
            config = json.loads(config_text or "{}")
        except json.JSONDecodeError:
            return None
        inputs = self._split_ports(self._get_field("detail-inputs"))
        outputs = self._split_ports(self._get_field("detail-outputs"))
        return {
            "label": self._get_field("detail-label"),
            "type": self._get_field("detail-type"),
            "config": config,
            "inputs": inputs,
            "outputs": outputs,
        }

    def gather_override(self) -> Optional[Dict[str, Any]]:
        text = self._get_field("detail-override")
        if not text.strip():
            return {}
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return None
        if not isinstance(data, dict):
            return None
        return data

    def _split_ports(self, value: str) -> Optional[list[str]]:
        if not value.strip():
            return []
        return [port.strip() for port in value.split(",") if port.strip()]

    def _get_field(self, widget_id: str) -> str:
        widget = self.query_one(f"#{widget_id}")
        return getattr(widget, "value", getattr(widget, "text", ""))

    def _set_field(self, widget_id: str, value: str) -> None:
        widget = self.query_one(f"#{widget_id}")
        if hasattr(widget, "value"):
            widget.value = value
        elif isinstance(widget, TextArea):
            widget.text = value
        elif isinstance(widget, Static):
            widget.update(value)
        else:  # pragma: no cover - defensive path
            widget.update(value)


class FlowTable(DataTable):
    """Table that tracks the most recent transmissions on each edge."""

    DEFAULT_CSS = """
    FlowTable {
        height: 1fr;
    }
    """

    def __init__(self) -> None:
        super().__init__(id="flow-table", zebra_stripes=True)
        self._rows: Dict[str, object] = {}

    def on_mount(self) -> None:
        self.add_columns("Edge", "Source", "Target", "Value", "Iteration", "Cached")

    def clear_rows(self) -> None:
        self.clear(columns=False)
        self._rows.clear()

    def record_transmission(self, edge: EdgeSpec, value: Any, iteration: Optional[int], cached: bool) -> None:
        """Update the table to reflect a new transmission."""

        if isinstance(value, str):
            summary = value[:120]
        elif isinstance(value, (int, float)):
            summary = str(value)
        else:
            summary = json.dumps(value, ensure_ascii=False)[:120]
        row = self._rows.get(edge.id)
        cached_marker = "yes" if cached else "no"
        if row is None:
            row_key = self.add_row(
                edge.id,
                f"{edge.source.node}:{edge.source.port}",
                f"{edge.target.node}:{edge.target.port}",
                summary,
                "-" if iteration is None else str(iteration),
                cached_marker,
            )
            self._rows[edge.id] = row_key
        else:
            self.update_cell(row, 0, edge.id)
            self.update_cell(row, 1, f"{edge.source.node}:{edge.source.port}")
            self.update_cell(row, 2, f"{edge.target.node}:{edge.target.port}")
            self.update_cell(row, 3, summary)
            self.update_cell(row, 4, "-" if iteration is None else str(iteration))
            self.update_cell(row, 5, cached_marker)


class StatusBar(Static):
    """Simple status indicator widget."""

    DEFAULT_CSS = """
    StatusBar {
        height: 1;
        border-top: solid $surface;
        padding: 0 1;
    }
    """

    def update_message(self, message: str) -> None:
        self.update(message)
