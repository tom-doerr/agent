from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict

import pytest

from web_dspy_builder.graph_runner import (
    ExecutionError,
    GraphRunner,
    _namespace_graph,
    prepare_loop_bindings,
)
from web_dspy_builder.models import (
    EdgeSpec,
    GraphSpec,
    NodeCache,
    NodePorts,
    NodeSpec,
    PortReference,
    RunSettings,
    RunState,
)
from web_dspy_builder.run_manager import RunManager


async def _noop_sender(event: Dict[str, object]) -> None:
    return None


def _linear_graph() -> GraphSpec:
    return GraphSpec(
        nodes=[
            NodeSpec(
                id="input",
                type="input",
                config={"value": "seed"},
                ports=NodePorts(outputs=["value"]),
            ),
            NodeSpec(
                id="middle",
                type="python",
                config={"code": "outputs['value'] = inputs['value']"},
                ports=NodePorts(inputs=["value"], outputs=["value"]),
            ),
            NodeSpec(
                id="out",
                type="output",
                config={},
                ports=NodePorts(inputs=["value"]),
            ),
        ],
        edges=[
            EdgeSpec(
                id="e1",
                source=PortReference(node="input", port="value"),
                target=PortReference(node="middle", port="value"),
            ),
            EdgeSpec(
                id="e2",
                source=PortReference(node="middle", port="value"),
                target=PortReference(node="out", port="value"),
            ),
        ],
    )


def _resume_state(graph: GraphSpec, settings: RunSettings) -> RunState:
    now = datetime.now(timezone.utc)
    state = RunState(
        run_id="previous",
        graph=graph,
        settings=settings,
        started_at=now,
    )
    for node in graph.nodes:
        state.node_results[node.id] = NodeCache(
            node_id=node.id,
            outputs={},
            transmissions=[],
            signature=node.signature(),
            started_at=now,
            completed_at=now,
        )
    return state


def test_plan_execution_respects_start_node() -> None:
    graph = _linear_graph()
    settings = RunSettings()
    runner = GraphRunner(graph, settings, "plan", _noop_sender, RunManager())
    resume = _resume_state(graph, settings)

    cached_nodes, nodes_to_execute = runner._plan_execution(
        resume, start_node="middle", overrides={}
    )

    assert nodes_to_execute == {"middle", "out"}
    assert cached_nodes == {"input"}


def test_plan_execution_reacts_to_overrides() -> None:
    graph = _linear_graph()
    settings = RunSettings()
    runner = GraphRunner(graph, settings, "plan", _noop_sender, RunManager())
    resume = _resume_state(graph, settings)

    cached_nodes, nodes_to_execute = runner._plan_execution(
        resume, start_node=None, overrides={"middle": {"code": "change"}}
    )

    assert nodes_to_execute == {"middle", "out"}
    assert cached_nodes == {"input"}


def test_plan_execution_detects_signature_changes() -> None:
    graph = _linear_graph()
    settings = RunSettings()
    runner = GraphRunner(graph, settings, "plan", _noop_sender, RunManager())
    resume = _resume_state(graph, settings)
    resume.node_results["input"].signature = "altered"

    cached_nodes, nodes_to_execute = runner._plan_execution(
        resume, start_node=None, overrides={}
    )

    assert nodes_to_execute == {"input", "middle", "out"}
    assert cached_nodes == set()


def test_plan_execution_raises_for_unknown_start_node() -> None:
    graph = _linear_graph()
    settings = RunSettings()
    runner = GraphRunner(graph, settings, "plan", _noop_sender, RunManager())
    resume = _resume_state(graph, settings)

    with pytest.raises(ExecutionError):
        runner._plan_execution(resume, start_node="missing", overrides={})


def test_namespace_graph_adds_prefix_without_mutating_original() -> None:
    body = GraphSpec(
        nodes=[
            NodeSpec(
                id="input",
                type="input",
                ports=NodePorts(outputs=["value"]),
            ),
            NodeSpec(
                id="sink",
                type="output",
                ports=NodePorts(inputs=["value"]),
            ),
        ],
        edges=[
            EdgeSpec(
                id="edge",
                source=PortReference(node="input", port="value"),
                target=PortReference(node="sink", port="value"),
            )
        ],
    )

    namespaced = _namespace_graph(body, "loop::")

    assert body.nodes[0].id == "input"
    assert namespaced.nodes[0].id == "loop::input"
    assert namespaced.nodes[1].id == "loop::sink"
    assert namespaced.edges[0].id == "loop::edge"
    assert namespaced.edges[0].source.node == "loop::input"
    assert namespaced.edges[0].target.node == "loop::sink"


def test_prepare_loop_bindings_uses_items_and_outer_inputs() -> None:
    loop_graph = GraphSpec(
        nodes=[
            NodeSpec(
                id="from_items",
                type="loopInput",
                config={"binding": "items"},
                ports=NodePorts(outputs=["value"]),
            ),
            NodeSpec(
                id="from_outer",
                type="loopInput",
                config={"binding": "input:shared"},
                ports=NodePorts(outputs=["value"]),
            ),
            NodeSpec(
                id="fallback",
                type="loopInput",
                config={"binding": "something", "default": "fallback"},
                ports=NodePorts(outputs=["value"]),
            ),
        ],
        edges=[],
    )

    prepare_loop_bindings(loop_graph, item="current", outer_inputs={"shared": "outer"})
    nodes = loop_graph.node_map()

    assert nodes["from_items"].type == "input"
    assert nodes["from_items"].config["value"] == "current"
    assert nodes["from_outer"].config["value"] == "outer"
    assert nodes["fallback"].config["value"] == "fallback"


@pytest.mark.asyncio
async def test_loop_node_without_body_returns_items_list() -> None:
    graph = GraphSpec(
        nodes=[
            NodeSpec(
                id="items",
                type="input",
                config={"value": ("a", "b")},
                ports=NodePorts(outputs=["items"]),
            ),
            NodeSpec(
                id="loop",
                type="loop",
                config={},
                ports=NodePorts(inputs=["items"], outputs=["items"]),
            ),
            NodeSpec(
                id="collector",
                type="output",
                config={},
                ports=NodePorts(inputs=["items"]),
            ),
        ],
        edges=[
            EdgeSpec(
                id="edge_in",
                source=PortReference(node="items", port="items"),
                target=PortReference(node="loop", port="items"),
            ),
            EdgeSpec(
                id="edge_out",
                source=PortReference(node="loop", port="items"),
                target=PortReference(node="collector", port="items"),
            ),
        ],
    )

    events: list[Dict[str, object]] = []

    async def sender(event: Dict[str, object]) -> None:
        events.append(event)

    runner = GraphRunner(graph, RunSettings(), "loop-simple", sender, RunManager())
    result = await runner.run()

    assert result.final_outputs["collector"]["items"] == ["a", "b"]
    assert any(event["type"] == "node_end" and event["nodeId"] == "loop" for event in events)


@pytest.mark.asyncio
async def test_loop_node_requires_output_mapping_when_body_provided() -> None:
    body = GraphSpec(
        nodes=[
            NodeSpec(
                id="source",
                type="loopInput",
                config={"binding": "items"},
                ports=NodePorts(outputs=["item"]),
            ),
            NodeSpec(
                id="sink",
                type="loopOutput",
                ports=NodePorts(inputs=["item"]),
            ),
        ],
        edges=[
            EdgeSpec(
                id="edge",
                source=PortReference(node="source", port="item"),
                target=PortReference(node="sink", port="item"),
            )
        ],
    )

    graph = GraphSpec(
        nodes=[
            NodeSpec(
                id="items",
                type="input",
                config={"value": [1, 2]},
                ports=NodePorts(outputs=["items"]),
            ),
            NodeSpec(
                id="loop",
                type="loop",
                config={"bodyGraph": body.model_dump()},
                ports=NodePorts(inputs=["items"], outputs=["results"]),
            ),
            NodeSpec(
                id="out",
                type="output",
                config={},
                ports=NodePorts(inputs=["results"]),
            ),
        ],
        edges=[
            EdgeSpec(
                id="edge_in",
                source=PortReference(node="items", port="items"),
                target=PortReference(node="loop", port="items"),
            ),
            EdgeSpec(
                id="edge_out",
                source=PortReference(node="loop", port="results"),
                target=PortReference(node="out", port="results"),
            ),
        ],
    )

    runner = GraphRunner(graph, RunSettings(), "loop-error", _noop_sender, RunManager())

    with pytest.raises(ExecutionError):
        await runner.run()
