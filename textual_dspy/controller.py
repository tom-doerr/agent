"""Controller for coordinating graph execution in the Textual UI."""

from __future__ import annotations

import asyncio
import uuid
from collections import deque
from typing import Any, Awaitable, Callable, Deque, Dict, List, Optional

from pathlib import Path

from web_dspy_builder.graph_runner import GraphRunner
from web_dspy_builder.models import EdgeSpec, NodePorts, NodeSpec, PortReference, RunSettings
from web_dspy_builder.run_manager import RunManager

from .document import ProgramDocument, default_document

EventListener = Callable[[Dict[str, Any]], Awaitable[None]]


class DSpyProgramController:
    """Manage a program document, graph execution, and run history."""

    def __init__(
        self,
        document: Optional[ProgramDocument] = None,
        *,
        manager: Optional[RunManager] = None,
    ) -> None:
        self.document = document or default_document()
        self.manager = manager or RunManager()
        self.listeners: List[EventListener] = []
        self.overrides: Dict[str, Dict[str, Any]] = {}
        self.run_history: Deque[str] = deque(maxlen=25)
        self.event_history: List[Dict[str, Any]] = []
        self._current_run_task: Optional[asyncio.Task] = None

    # ------------------------------------------------------------------
    # Subscription management
    # ------------------------------------------------------------------
    def add_listener(self, listener: EventListener) -> None:
        """Register an async listener to receive graph events."""

        self.listeners.append(listener)

    async def _emit(self, event: Dict[str, Any]) -> None:
        """Send an event to listeners and store it for replay."""

        self.event_history.append(event)
        coros = [listener(event) for listener in list(self.listeners)]
        if not coros:
            return
        await asyncio.gather(*coros, return_exceptions=True)

    # ------------------------------------------------------------------
    # Document management
    # ------------------------------------------------------------------
    def set_document(self, document: ProgramDocument) -> None:
        self.document = document

    def save(self, path: str) -> None:
        self.document.save(Path(path))

    def load(self, path: str) -> None:
        self.document = ProgramDocument.load(Path(path))

    # ------------------------------------------------------------------
    # Graph manipulation helpers
    # ------------------------------------------------------------------
    def node(self, node_id: str) -> NodeSpec:
        node_map = self.document.graph.node_map()
        if node_id not in node_map:
            raise KeyError(f"Unknown node: {node_id}")
        return node_map[node_id]

    def update_node(
        self,
        node_id: str,
        *,
        label: Optional[str] = None,
        type: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        inputs: Optional[List[str]] = None,
        outputs: Optional[List[str]] = None,
    ) -> NodeSpec:
        """Mutate a node's metadata in-place and return it."""

        node = self.node(node_id)
        if label is not None:
            node.label = label
        if type is not None:
            node.type = type
        if config is not None:
            node.config = config
        if inputs is not None or outputs is not None:
            node.ports = NodePorts(
                inputs=inputs if inputs is not None else list(node.ports.inputs),
                outputs=outputs if outputs is not None else list(node.ports.outputs),
            )
        return node

    def add_node(self, spec: NodeSpec) -> None:
        if spec.id in {node.id for node in self.document.graph.nodes}:
            raise ValueError(f"Node with id {spec.id} already exists")
        self.document.graph.nodes.append(spec)

    def remove_node(self, node_id: str) -> None:
        nodes = self.document.graph.nodes
        self.document.graph.nodes = [node for node in nodes if node.id != node_id]
        self.document.graph.edges = [
            edge
            for edge in self.document.graph.edges
            if edge.source.node != node_id and edge.target.node != node_id
        ]

    def add_edge(self, edge: EdgeSpec) -> None:
        self.document.graph.edges.append(edge)

    def remove_edge(self, edge_id: str) -> None:
        self.document.graph.edges = [edge for edge in self.document.graph.edges if edge.id != edge_id]

    def edges(self) -> List[EdgeSpec]:
        return list(self.document.graph.edges)

    # ------------------------------------------------------------------
    # Overrides and interventions
    # ------------------------------------------------------------------
    def set_override(self, node_id: str, override: Dict[str, Any]) -> None:
        self.overrides[node_id] = override

    def clear_override(self, node_id: str) -> None:
        self.overrides.pop(node_id, None)

    def clear_all_overrides(self) -> None:
        self.overrides.clear()

    # ------------------------------------------------------------------
    # Run execution
    # ------------------------------------------------------------------
    async def run(
        self,
        *,
        start_node: Optional[str] = None,
        resume_from: Optional[str] = None,
        settings: Optional[RunSettings] = None,
    ) -> None:
        """Execute the current graph, optionally resuming from a cached run."""

        if self._current_run_task and not self._current_run_task.done():
            raise RuntimeError("A run is already in progress")

        run_settings = settings or self.document.settings
        graph = self.document.graph
        run_id = f"run-{uuid.uuid4().hex}"
        resume_state = None
        if resume_from:
            resume_state = self.manager.get(resume_from)
            if resume_state is None:
                raise ValueError(f"Unknown run id: {resume_from}")

        async def sender(event: Dict[str, Any]) -> None:
            await self._emit(event)

        runner = GraphRunner(
            graph,
            run_settings,
            run_id=run_id,
            sender=sender,
            manager=self.manager,
        )

        async def _runner_task() -> None:
            try:
                await runner.run(resume=resume_state, start_node=start_node, overrides=self.overrides)
            finally:
                self.run_history.appendleft(run_id)
                self._current_run_task = None

        self._current_run_task = asyncio.create_task(_runner_task())
        await self._current_run_task

    def active_run_id(self) -> Optional[str]:
        if self._current_run_task and not self._current_run_task.done():
            return self.run_history[0] if self.run_history else None
        return None

    def available_runs(self) -> List[str]:
        return list(self.run_history)

    def create_edge(self, edge_id: str, source_node: str, source_port: str, target_node: str, target_port: str) -> EdgeSpec:
        """Convenience helper used by the UI to add connections."""

        edge = EdgeSpec(
            id=edge_id,
            source=PortReference(node=source_node, port=source_port),
            target=PortReference(node=target_node, port=target_port),
        )
        self.add_edge(edge)
        return edge
