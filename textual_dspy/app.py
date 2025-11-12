"""Textual application for constructing and running DSPy programs."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Optional, Any, Dict

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.events import Mount
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Input, Label, ListItem, ListView, Log

from web_dspy_builder.models import NodePorts, NodeSpec

from .controller import DSpyProgramController
from .document import ProgramDocument, default_document
from .widgets import FlowTable, NodeDetail, StatusBar


class NodeListItem(ListItem):
    """List item storing node metadata."""

    def __init__(self, node: NodeSpec) -> None:
        super().__init__(Label(f"{node.id} [{node.type}]"), id=f"node-item-{node.id}")
        self.node_id = node.id


class DSpyProgramApp(App):
    """Interactive Textual interface for DSPy graph execution."""

    CSS = """
    Screen {
        layout: vertical;
    }
    #body {
        height: 1fr;
    }
    #top-row {
        height: 70%;
    }
    #bottom-row {
        height: 30%;
        border-top: solid $surface;
        padding-top: 1;
    }
    #node-pane, #detail-pane, #run-pane {
        width: 1fr;
        padding: 1;
        border-right: solid $surface;
    }
    #run-pane {
        border-right: none;
    }
    #node-list {
        height: 1fr;
    }
    #event-log {
        height: 1fr;
    }
    #flow-table {
        height: 1fr;
    }
    #run-history {
        height: 6;
    }
    #file-pane, #run-controls {
        width: 1fr;
        padding: 0 1;
    }
    #file-buttons, #run-buttons, #node-buttons {
        height: auto;
        padding-top: 1;
    }
    #file-path, #start-node, #resume-run, #llm-engine, #llm-model, #llm-temperature, #llm-max-tokens {
        width: 1fr;
    }
    """

    BINDINGS = [
        ("ctrl+r", "run", "Run program"),
        ("ctrl+s", "save", "Save program"),
        ("ctrl+o", "load", "Load program"),
        ("ctrl+e", "replay", "Replay with overrides"),
        ("ctrl+k", "clear_overrides", "Clear overrides"),
    ]

    selected_node: reactive[Optional[str]] = reactive(None, init=False)

    def __init__(self, document: Optional[ProgramDocument] = None) -> None:
        super().__init__()
        self.controller = DSpyProgramController(document=document or default_document())
        self.controller.add_listener(self._handle_event)
        self._event_lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="body"):
            with Vertical(id="top-row"):
                with Horizontal():
                    with Vertical(id="node-pane"):
                        yield Label("Nodes", id="nodes-title")
                        yield ListView(id="node-list")
                        with Horizontal(id="node-buttons"):
                            yield Button("Add", id="add-node", variant="primary")
                            yield Button("Remove", id="remove-node", variant="warning")
                    with Vertical(id="detail-pane"):
                        yield NodeDetail(id="node-detail")
                    with Vertical(id="run-pane"):
                        yield Label("Information Flow", id="flow-title")
                        yield FlowTable()
                        yield Label("Run History", id="run-history-title")
                        yield ListView(id="run-history")
                        yield Label("Event Log", id="log-title")
                        yield Log(id="event-log")
            with Horizontal(id="bottom-row"):
                with Vertical(id="file-pane"):
                    yield Label("Program File", id="file-label")
                    yield Input(placeholder="dspy_program.json", id="file-path")
                    with Horizontal(id="file-buttons"):
                        yield Button("Save", id="save-program", variant="success")
                        yield Button("Load", id="load-program", variant="primary")
                with Vertical(id="run-controls"):
                    yield Label("Run Controls", id="run-label")
                    yield Input(placeholder="start node id (optional)", id="start-node")
                    yield Input(placeholder="resume run id (optional)", id="resume-run")
                    yield Label("LLM Engine", id="llm-engine-label")
                    yield Input(placeholder="mock", id="llm-engine")
                    yield Label("LLM Model", id="llm-model-label")
                    yield Input(placeholder="gpt-4o-mini", id="llm-model")
                    yield Label("Temperature", id="llm-temp-label")
                    yield Input(placeholder="0.0", id="llm-temperature")
                    yield Label("Max Tokens", id="llm-tokens-label")
                    yield Input(placeholder="2048", id="llm-max-tokens")
                    with Horizontal(id="run-buttons"):
                        yield Button("Run", id="run-program", variant="success")
                        yield Button("Replay", id="replay-program", variant="primary")
                        yield Button("Clear Overrides", id="clear-override-btn", variant="warning")
            yield StatusBar(id="status-bar")
        yield Footer()

    # ------------------------------------------------------------------
    # Mount lifecycle
    # ------------------------------------------------------------------
    async def on_mount(self, event: Mount) -> None:  # noqa: D401 - event hook
        """Populate widgets with the document contents."""

        self._refresh_nodes()
        self._refresh_run_history()
        self._populate_run_settings_inputs()
        self._status("Ready")

    # ------------------------------------------------------------------
    # Controller event handling
    # ------------------------------------------------------------------
    async def _handle_event(self, event: Dict[str, Any]) -> None:
        async with self._event_lock:
            self._process_event(event)

    def _process_event(self, event: Dict[str, Any]) -> None:
        log = self.query_one("#event-log", Log)
        log.write(json.dumps(event, ensure_ascii=False))
        event_type = event.get("type")
        if event_type in {"run_started", "subgraph_started"}:
            self.query_one(FlowTable).clear_rows()
            self._status("Run in progress…")
        elif event_type in {"run_complete", "subgraph_complete"}:
            self._status("Run complete")
            self._refresh_run_history()
        elif event_type == "run_error":
            self._status(f"Run error: {event.get('message', 'unknown')}")
        elif event_type == "edge_data":
            edge_id = event["edgeId"]
            edge = next((e for e in self.controller.document.graph.edges if e.id == edge_id), None)
            if edge:
                table = self.query_one(FlowTable)
                table.record_transmission(edge, event.get("value"), event.get("iteration"), bool(event.get("cached")))

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    async def action_run(self) -> None:
        await self._execute_run()

    async def action_replay(self) -> None:
        start_node = self.query_one("#start-node", Input).value.strip() or None
        resume_run = self.query_one("#resume-run", Input).value.strip() or None
        await self._execute_run(start_node=start_node, resume=resume_run)

    async def action_save(self) -> None:
        try:
            path = self._resolve_file_path()
            self.controller.save(str(path))
            self._status(f"Saved program to {path}")
        except Exception as exc:  # pragma: no cover - defensive logging
            self._status(f"Failed to save: {exc}")

    async def action_load(self) -> None:
        try:
            path = self._resolve_file_path()
            self.controller.load(str(path))
            self.selected_node = None
            self._refresh_nodes()
            self._status(f"Loaded program from {path}")
        except Exception as exc:
            self._status(f"Failed to load: {exc}")

    async def action_clear_overrides(self) -> None:
        self.controller.clear_all_overrides()
        detail = self.query_one(NodeDetail)
        if self.selected_node:
            detail.display_node(self.controller.node(self.selected_node), {})
        self._status("Cleared overrides")

    # ------------------------------------------------------------------
    # Button events
    # ------------------------------------------------------------------
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "run-program":
            await self.action_run()
        elif event.button.id == "replay-program":
            await self.action_replay()
        elif event.button.id == "save-program":
            await self.action_save()
        elif event.button.id == "load-program":
            await self.action_load()
        elif event.button.id == "add-node":
            self._add_node()
        elif event.button.id == "remove-node":
            self._remove_selected_node()
        elif event.button.id == "clear-override-btn":
            await self.action_clear_overrides()
        elif event.button.id == "apply-node":
            self._apply_node_changes()
        elif event.button.id == "apply-override":
            self._apply_override()
        elif event.button.id == "clear-override":
            self._clear_node_override()

    # ------------------------------------------------------------------
    # List view events
    # ------------------------------------------------------------------
    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id == "node-list":
            item = event.item
            if isinstance(item, NodeListItem):
                self.selected_node = item.node_id
                override = self.controller.overrides.get(item.node_id)
                self.query_one(NodeDetail).display_node(self.controller.node(item.node_id), override)
        elif event.list_view.id == "run-history":
            run_item = event.item
            if isinstance(run_item, ListItem):
                run_id = run_item.id.replace("run-", "", 1)
                self.query_one("#resume-run", Input).value = run_id

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _refresh_nodes(self) -> None:
        node_list = self.query_one("#node-list", ListView)
        node_list.clear()
        for node in self.controller.document.graph.nodes:
            node_list.append(NodeListItem(node))
        if self.controller.document.graph.nodes:
            first_node = self.controller.document.graph.nodes[0]
            node_list.index = 0
            self.selected_node = first_node.id
            self.query_one(NodeDetail).display_node(first_node, self.controller.overrides.get(first_node.id))
        else:
            self.query_one(NodeDetail).clear()

    def _refresh_run_history(self) -> None:
        history = self.query_one("#run-history", ListView)
        history.clear()
        for run_id in self.controller.available_runs():
            history.append(ListItem(Label(run_id), id=f"run-{run_id}"))

    def _resolve_file_path(self) -> Path:
        file_input = self.query_one("#file-path", Input)
        value = file_input.value.strip()
        if value:
            return Path(value)
        if self.controller.document.path:
            file_input.value = str(self.controller.document.path)
            return self.controller.document.path
        default = Path("dspy_program.json")
        file_input.value = str(default)
        return default

    async def _execute_run(self, *, start_node: Optional[str] = None, resume: Optional[str] = None) -> None:
        log = self.query_one("#event-log", Log)
        log.clear()
        table = self.query_one(FlowTable)
        table.clear_rows()
        if not self._apply_run_settings_from_inputs():
            return
        try:
            await self.controller.run(start_node=start_node, resume_from=resume)
        except Exception as exc:
            self._status(f"Run failed: {exc}")
        else:
            self._status("Run finished")

    def _status(self, message: str) -> None:
        self.query_one(StatusBar).update_message(message)

    def _populate_run_settings_inputs(self) -> None:
        llm = self.controller.document.settings.llm
        self.query_one("#llm-engine", Input).value = llm.engine
        self.query_one("#llm-model", Input).value = llm.model or ""
        self.query_one("#llm-temperature", Input).value = f"{llm.temperature:.2f}"
        self.query_one("#llm-max-tokens", Input).value = str(llm.max_tokens)

    def _apply_run_settings_from_inputs(self) -> bool:
        llm = self.controller.document.settings.llm
        engine = self.query_one("#llm-engine", Input).value.strip()
        model = self.query_one("#llm-model", Input).value.strip()
        temperature_raw = self.query_one("#llm-temperature", Input).value.strip()
        max_tokens_raw = self.query_one("#llm-max-tokens", Input).value.strip()

        if engine:
            llm.engine = engine
        if model:
            llm.model = model
        if temperature_raw:
            try:
                llm.temperature = float(temperature_raw)
            except ValueError:
                self._status("Temperature must be a number")
                return False
        if max_tokens_raw:
            try:
                llm.max_tokens = int(max_tokens_raw)
            except ValueError:
                self._status("Max tokens must be an integer")
                return False
        return True

    def _add_node(self) -> None:
        existing = {node.id for node in self.controller.document.graph.nodes}
        index = 1
        while f"node{index}" in existing:
            index += 1
        new_node = NodeSpec(
            id=f"node{index}",
            type="python",
            label=f"Node {index}",
            config={"code": "outputs['result'] = inputs.get('value', '')"},
            ports=NodePorts(inputs=["value"], outputs=["result"]),
        )
        self.controller.add_node(new_node)
        self._refresh_nodes()
        self._status(f"Added node {new_node.id}")

    def _remove_selected_node(self) -> None:
        if not self.selected_node:
            return
        try:
            self.controller.remove_node(self.selected_node)
        except KeyError:
            pass
        self.selected_node = None
        self._refresh_nodes()
        self._status("Removed node")

    def _apply_node_changes(self) -> None:
        detail = self.query_one(NodeDetail)
        updates = detail.gather_update()
        if not updates or not self.selected_node:
            self._status("Invalid node configuration")
            return
        self.controller.update_node(
            self.selected_node,
            label=updates["label"],
            type=updates["type"],
            config=updates["config"],
            inputs=updates["inputs"],
            outputs=updates["outputs"],
        )
        self._refresh_nodes()
        self._status("Node updated")

    def _apply_override(self) -> None:
        if not self.selected_node:
            self._status("Select a node to override")
            return
        detail = self.query_one(NodeDetail)
        override = detail.gather_override()
        if override is None:
            self._status("Override must be JSON object")
            return
        self.controller.set_override(self.selected_node, override)
        self._status(f"Override applied for {self.selected_node}")

    def _clear_node_override(self) -> None:
        if not self.selected_node:
            return
        self.controller.clear_override(self.selected_node)
        detail = self.query_one(NodeDetail)
        detail.display_node(self.controller.node(self.selected_node), {})
        self._status("Cleared node override")
