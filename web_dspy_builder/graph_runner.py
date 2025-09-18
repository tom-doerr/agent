"""Graph execution engine for the DSPy visual builder."""

from __future__ import annotations

import asyncio
from contextlib import redirect_stdout
from dataclasses import dataclass, field
from datetime import datetime, timezone
from graphlib import CycleError, TopologicalSorter
from io import StringIO
from typing import Any, Awaitable, Callable, Dict, Iterable, List, Optional, Set

from pydantic import BaseModel

from .llm import LLMEngine
from .models import (
    EdgeSpec,
    EdgeTransmission,
    GraphSpec,
    NodeCache,
    NodeSpec,
    RunSettings,
    RunState,
)
from .run_manager import RunManager


EventSender = Callable[[Dict[str, Any]], Awaitable[None]]


@dataclass
class NodeExecutionResult:
    """Result returned by node executors."""

    outputs: Dict[str, Any]
    transmissions: Optional[List[EdgeTransmission]] = None
    logs: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExecutionError(RuntimeError):
    """Raised when the graph cannot be executed."""


class BaseNodeExecutor:
    """Base class for all node executors."""

    def __init__(self, runner: "GraphRunner", spec: NodeSpec) -> None:
        self.runner = runner
        self.spec = spec

    async def run(self, inputs: Dict[str, Any], overrides: Dict[str, Any]) -> NodeExecutionResult:
        raise NotImplementedError

    def output_ports(self) -> List[str]:
        if self.spec.ports.outputs:
            return self.spec.ports.outputs
        return ["output"]


class InputNodeExecutor(BaseNodeExecutor):
    """Node that emits configured or overridden values."""

    async def run(self, inputs: Dict[str, Any], overrides: Dict[str, Any]) -> NodeExecutionResult:
        values_config = self.spec.config.get("values")
        outputs: Dict[str, Any]
        if isinstance(values_config, dict):
            outputs = dict(values_config)
        else:
            outputs = {}

        default_value = self.spec.config.get("value")
        value = overrides.get("value", default_value)
        if value is None and "value" in overrides:
            value = overrides["value"]

        ports = self.output_ports()
        if ports and value is not None:
            outputs.setdefault(ports[0], value)
        elif value is not None:
            outputs.setdefault("value", value)

        for port, override_value in overrides.items():
            if port == "value":
                continue
            outputs[port] = override_value

        return NodeExecutionResult(outputs=outputs)


class PythonNodeExecutor(BaseNodeExecutor):
    """Execute custom python code within a restricted environment."""

    SAFE_BUILTINS = {
        "len": len,
        "min": min,
        "max": max,
        "sum": sum,
        "sorted": sorted,
        "range": range,
        "enumerate": enumerate,
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "list": list,
        "dict": dict,
        "set": set,
        "tuple": tuple,
        "zip": zip,
        "any": any,
        "all": all,
    }

    async def run(self, inputs: Dict[str, Any], overrides: Dict[str, Any]) -> NodeExecutionResult:
        code = overrides.get("code", self.spec.config.get("code", ""))
        local_vars: Dict[str, Any] = {
            "inputs": inputs,
            "config": self.spec.config,
            "outputs": {},
        }
        stdout = StringIO()
        with redirect_stdout(stdout):
            exec(  # noqa: S102 - execution is sandboxed via SAFE_BUILTINS
                code,
                {"__builtins__": self.SAFE_BUILTINS},
                local_vars,
            )
        outputs: Dict[str, Any] = local_vars.get("outputs") or {}
        metadata = {"stdout": stdout.getvalue()}
        return NodeExecutionResult(outputs=outputs, metadata=metadata)


class LLMNodeExecutor(BaseNodeExecutor):
    """Invoke the configured language model using a simple templating approach."""

    async def run(self, inputs: Dict[str, Any], overrides: Dict[str, Any]) -> NodeExecutionResult:
        prompt_template = overrides.get("prompt") or self.spec.config.get("prompt", "")
        stop = overrides.get("stop") or self.spec.config.get("stop")
        prompt = self._render_prompt(prompt_template, inputs)
        response = await asyncio.to_thread(self.runner.llm.complete, prompt, stop=stop)
        output_port = self.output_ports()[0]
        return NodeExecutionResult(outputs={output_port: response})

    def _render_prompt(self, template: str, inputs: Dict[str, Any]) -> str:
        rendered = template
        for key, value in inputs.items():
            token = "{{" + key + "}}"
            rendered = rendered.replace(token, str(value))
        return rendered


class OutputNodeExecutor(BaseNodeExecutor):
    """Collect incoming values; outputs mirror the collected inputs."""

    async def run(self, inputs: Dict[str, Any], overrides: Dict[str, Any]) -> NodeExecutionResult:
        result = dict(inputs)
        result.update(overrides)
        return NodeExecutionResult(outputs=result)


class LoopNodeExecutor(BaseNodeExecutor):
    """Execute a nested graph for each item provided on the "items" input."""

    async def run(self, inputs: Dict[str, Any], overrides: Dict[str, Any]) -> NodeExecutionResult:
        items = overrides.get("items", inputs.get("items", []))
        if items is None:
            items_list: List[Any] = []
        elif isinstance(items, list):
            items_list = items
        else:
            items_list = list(items) if isinstance(items, (tuple, set)) else [items]

        body_graph_data = overrides.get("bodyGraph") or self.spec.config.get("bodyGraph")
        if not body_graph_data:
            return NodeExecutionResult(outputs={self.output_ports()[0]: items_list})

        body_graph = GraphSpec.model_validate(body_graph_data)
        loop_outputs_config = self.spec.config.get("loopOutputs", [])
        if not loop_outputs_config:
            raise ExecutionError(
                f"Loop node {self.spec.id} is missing loopOutputs configuration"
            )

        aggregated: Dict[str, List[Any]] = {entry["target"]: [] for entry in loop_outputs_config}
        iteration_metadata: List[Dict[str, Any]] = []

        for index, item in enumerate(items_list):
            iteration_scope = {
                "scope": "loop",
                "parentNodeId": self.spec.id,
                "loopIteration": index,
            }
            namespaced_graph = _namespace_graph(body_graph, f"{self.spec.id}::iter{index}::")
            prepare_loop_bindings(namespaced_graph, item, inputs)
            subrunner = GraphRunner(
                namespaced_graph,
                self.runner.settings,
                run_id=f"{self.runner.run_id}:{self.spec.id}:{index}",
                sender=self.runner.sender,
                manager=None,
                scope=iteration_scope,
                parent=self.runner,
            )
            result = await subrunner.run()
            iteration_metadata.append({
                "outputs": result.final_outputs,
                "nodes": list(result.node_outputs.keys()),
            })
            for entry in loop_outputs_config:
                original_id = entry["node"]
                port = entry.get("port", "output")
                target = entry["target"]
                namespaced_id = f"{self.spec.id}::iter{index}::{original_id}"
                node_outputs = result.node_outputs.get(namespaced_id, {})
                value = node_outputs.get(port)
                aggregated.setdefault(target, []).append(value)

        transmissions: List[EdgeTransmission] = []
        for edge in self.runner.outgoing_edges(self.spec.id):
            values = aggregated.get(edge.source.port, [])
            if not isinstance(values, list):
                values = [values]
            for iteration, value in enumerate(values):
                transmissions.append(
                    EdgeTransmission(
                        edge_id=edge.id,
                        source=edge.source,
                        target=edge.target,
                        value=value,
                        iteration=iteration,
                    )
                )

        return NodeExecutionResult(
            outputs=aggregated,
            transmissions=transmissions,
            metadata={"iterations": iteration_metadata},
        )


class CognitionNodeExecutor(BaseNodeExecutor):
    """Invoke the typed cognition agent and expose structured outputs."""

    INPUT_FIELDS = (
        "observation",
        "episodic_memory",
        "goals",
        "constraints",
        "utility_def",
        "prior_belief",
        "attention_results",
        "system_events",
    )

    def __init__(self, runner: "GraphRunner", spec: NodeSpec) -> None:
        super().__init__(runner, spec)
        from cognition_typed_dspy import CognitionAgent

        self.agent = CognitionAgent()

    async def run(self, inputs: Dict[str, Any], overrides: Dict[str, Any]) -> NodeExecutionResult:
        resolved: Dict[str, Any] = {}
        for field in self.INPUT_FIELDS:
            if field in overrides:
                resolved[field] = overrides[field]
            elif field in inputs:
                resolved[field] = inputs[field]
            else:
                resolved[field] = self.spec.config.get(field, "")

        outputs = await asyncio.to_thread(self.agent.forward, **resolved)
        serialised = {key: self._serialise(value) for key, value in outputs.items()}
        metadata = {"inputs": resolved}
        return NodeExecutionResult(outputs=serialised, metadata=metadata)

    def _serialise(self, value: Any) -> Any:
        if isinstance(value, BaseModel):
            return value.model_dump(mode="python")
        if isinstance(value, list):
            return [self._serialise(item) for item in value]
        if isinstance(value, dict):
            return {key: self._serialise(item) for key, item in value.items()}
        return value


EXECUTOR_REGISTRY: Dict[str, Callable[["GraphRunner", NodeSpec], BaseNodeExecutor]] = {
    "input": InputNodeExecutor,
    "llm": LLMNodeExecutor,
    "prompt": LLMNodeExecutor,
    "python": PythonNodeExecutor,
    "output": OutputNodeExecutor,
    "loop": LoopNodeExecutor,
    "loopInput": InputNodeExecutor,
    "loopOutput": OutputNodeExecutor,
    "cognition": CognitionNodeExecutor,
}


def create_executor(runner: "GraphRunner", spec: NodeSpec) -> BaseNodeExecutor:
    try:
        factory = EXECUTOR_REGISTRY[spec.type]
    except KeyError as exc:  # pragma: no cover - defensive branch
        raise ExecutionError(f"Unsupported node type: {spec.type}") from exc
    return factory(runner, spec)


@dataclass
class GraphRunResult:
    """Details returned after running a graph."""

    run_id: str
    node_outputs: Dict[str, Dict[str, Any]]
    final_outputs: Dict[str, Any]
    run_state: RunState


class GraphRunner:
    """Execute a graph specification and stream events through a sender."""

    def __init__(
        self,
        graph: GraphSpec,
        settings: RunSettings,
        run_id: str,
        sender: EventSender,
        manager: Optional[RunManager],
        *,
        scope: Optional[Dict[str, Any]] = None,
        parent: Optional["GraphRunner"] = None,
    ) -> None:
        self.graph = graph
        self.settings = settings
        self.run_id = run_id
        self.sender = sender
        self.manager = manager
        self.scope = scope or {"scope": "graph"}
        self.parent = parent
        self.node_map = graph.node_map()
        self._edges_by_source: Dict[str, List[EdgeSpec]] = {}
        self._edges_by_target: Dict[str, List[EdgeSpec]] = {}
        for edge in graph.edges:
            self._edges_by_source.setdefault(edge.source.node, []).append(edge)
            self._edges_by_target.setdefault(edge.target.node, []).append(edge)
        self.llm = parent.llm if parent else LLMEngine(settings.llm)
        self.run_state = RunState(
            run_id=run_id,
            graph=graph,
            settings=settings,
            started_at=datetime.now(timezone.utc),
        )
        if manager:
            manager.register(self.run_state)

    async def run(
        self,
        *,
        resume: Optional[RunState] = None,
        start_node: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> GraphRunResult:
        overrides = overrides or {}
        start_type = "run_started" if self.scope.get("scope") == "graph" else "subgraph_started"
        await self._emit_event({"type": start_type})

        cached_nodes, nodes_to_execute = self._plan_execution(
            resume, start_node, overrides
        )
        results: Dict[str, Dict[str, Any]] = {}

        for node_id in self._topological_order():
            node = self.node_map[node_id]
            node_overrides = overrides.get(node_id, {})
            if node_id in cached_nodes and resume:
                cache = resume.node_results[node_id]
                results[node_id] = cache.outputs
                await self._emit_event(cache.to_event())
                for transmission in cache.transmissions:
                    transmission.cached = True
                    await self._emit_event(transmission.to_event())
                continue

            if node_id not in nodes_to_execute:
                continue

            inputs = self._collect_inputs(node_id, results)
            inputs.update(node_overrides.get("inputs", {}))
            executor = create_executor(self, node)
            await self._emit_event({"type": "node_start", "nodeId": node_id})

            started_at = datetime.now(timezone.utc)
            try:
                execution_result = await executor.run(inputs, node_overrides)
            except Exception as exc:  # pragma: no cover - error branch
                error_type = "run_error" if self.scope.get("scope") == "graph" else "subgraph_error"
                await self._emit_event(
                    {
                        "type": error_type,
                        "nodeId": node_id,
                        "message": str(exc),
                    }
                )
                raise

            if execution_result.logs:
                await self._emit_event(
                    {
                        "type": "node_log",
                        "nodeId": node_id,
                        "log": execution_result.logs,
                    }
                )

            results[node_id] = execution_result.outputs

            transmissions = execution_result.transmissions
            if transmissions is None:
                transmissions = self._default_transmissions(node_id, execution_result.outputs)
            for transmission in transmissions:
                await self._emit_event(transmission.to_event())

            completed_at = datetime.now(timezone.utc)
            cache_entry = NodeCache(
                node_id=node_id,
                outputs=execution_result.outputs,
                transmissions=transmissions,
                signature=node.signature(),
                started_at=started_at,
                completed_at=completed_at,
                metadata=execution_result.metadata,
            )
            self.run_state.node_results[node_id] = cache_entry
            await self._emit_event(
                {
                    "type": "node_end",
                    "nodeId": node_id,
                    "outputs": execution_result.outputs,
                    "metadata": execution_result.metadata,
                }
            )

        final_outputs = self._collect_graph_outputs(results)
        complete_type = "run_complete" if self.scope.get("scope") == "graph" else "subgraph_complete"
        await self._emit_event({"type": complete_type, "outputs": final_outputs})
        return GraphRunResult(
            run_id=self.run_id,
            node_outputs=results,
            final_outputs=final_outputs,
            run_state=self.run_state,
        )

    def _collect_inputs(
        self, node_id: str, results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        collected: Dict[str, List[Any]] = {}
        for edge in self._edges_by_target.get(node_id, []):
            source_outputs = results.get(edge.source.node, {})
            if edge.source.port not in source_outputs:
                continue
            collected.setdefault(edge.target.port, []).append(
                source_outputs[edge.source.port]
            )

        processed: Dict[str, Any] = {}
        for port, values in collected.items():
            processed[port] = values[0] if len(values) == 1 else values

        defaults = self.node_map[node_id].config.get("defaults", {})
        for port, default_value in defaults.items():
            processed.setdefault(port, default_value)
        return processed

    def _collect_graph_outputs(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        output_nodes = [node for node in self.graph.nodes if node.type == "output"]
        if not output_nodes:
            return {}
        summary: Dict[str, Any] = {}
        for node in output_nodes:
            summary[node.id] = results.get(node.id, {})
        return summary

    def _plan_execution(
        self,
        resume: Optional[RunState],
        start_node: Optional[str],
        overrides: Dict[str, Any],
    ) -> tuple[Set[str], Set[str]]:
        if not resume or not self.settings.allow_cache_reuse:
            return set(), set(self.node_map.keys())

        changed_nodes: Set[str] = set()
        for node_id, node in self.node_map.items():
            cached_signature = resume.node_signature(node_id)
            if cached_signature is None or cached_signature != node.signature():
                changed_nodes.add(node_id)

        if start_node and start_node not in self.node_map:
            raise ExecutionError(f"Unknown start node: {start_node}")

        nodes_to_execute: Set[str] = set()
        if changed_nodes:
            nodes_to_execute |= self._downstream_nodes(changed_nodes)
        if start_node:
            nodes_to_execute |= self._downstream_nodes({start_node})

        override_nodes = {node_id for node_id in overrides if node_id in self.node_map}
        if override_nodes:
            nodes_to_execute |= override_nodes
            nodes_to_execute |= self._downstream_nodes(override_nodes)

        if not nodes_to_execute:
            nodes_to_execute = set(self.node_map.keys())

        cached_nodes = set(resume.cached_nodes()) - nodes_to_execute
        return cached_nodes, nodes_to_execute

    def _downstream_nodes(self, start: Iterable[str]) -> Set[str]:
        queue = list(start)
        seen: Set[str] = set()
        while queue:
            node_id = queue.pop(0)
            if node_id in seen:
                continue
            seen.add(node_id)
            for edge in self._edges_by_source.get(node_id, []):
                queue.append(edge.target.node)
        return seen

    def _topological_order(self) -> List[str]:
        sorter = TopologicalSorter()
        for node in self.graph.nodes:
            dependencies = [edge.source.node for edge in self._edges_by_target.get(node.id, [])]
            sorter.add(node.id, *dependencies)
        try:
            return list(sorter.static_order())
        except CycleError as exc:  # pragma: no cover - cycle guard
            raise ExecutionError("Graph contains cycles that cannot be resolved") from exc

    def _default_transmissions(
        self, node_id: str, outputs: Dict[str, Any]
    ) -> List[EdgeTransmission]:
        transmissions: List[EdgeTransmission] = []
        for edge in self._edges_by_source.get(node_id, []):
            if edge.source.port not in outputs:
                continue
            transmissions.append(
                EdgeTransmission(
                    edge_id=edge.id,
                    source=edge.source,
                    target=edge.target,
                    value=outputs[edge.source.port],
                )
            )
        return transmissions

    def outgoing_edges(self, node_id: str) -> List[EdgeSpec]:
        return self._edges_by_source.get(node_id, [])

    async def _emit_event(self, event: Dict[str, Any]) -> None:
        payload = dict(event)
        payload.setdefault("runId", self.run_id)
        payload.update(self.scope)
        await self.sender(payload)
        self.run_state.record_event(payload)


def _namespace_graph(graph: GraphSpec, prefix: str) -> GraphSpec:
    data = graph.model_dump(mode="python")
    for node in data["nodes"]:
        node["id"] = f"{prefix}{node['id']}"
    for edge in data["edges"]:
        edge["id"] = f"{prefix}{edge['id']}"
        edge["source"]["node"] = f"{prefix}{edge['source']['node']}"
        edge["target"]["node"] = f"{prefix}{edge['target']['node']}"
    return GraphSpec.model_validate(data)


def prepare_loop_bindings(graph: GraphSpec, item: Any, outer_inputs: Dict[str, Any]) -> None:
    for node in graph.nodes:
        if node.type != "loopInput":
            continue
        binding = node.config.get("binding", "items")
        if binding == "items":
            value = item
        elif binding.startswith("input:"):
            key = binding.split(":", 1)[1]
            value = outer_inputs.get(key)
        else:
            value = node.config.get("default")
        node.type = "input"
        node.config.setdefault("value", value)

