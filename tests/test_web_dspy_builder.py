import asyncio
from typing import Dict, List

import pytest

from web_dspy_builder.graph_runner import GraphRunner
from web_dspy_builder.models import (
    EdgeSpec,
    GraphSpec,
    LLMSettings,
    NodePorts,
    NodeSpec,
    PortReference,
    RunSettings,
)
from web_dspy_builder.run_manager import RunManager


@pytest.mark.asyncio
async def test_graph_runner_executes_linear_graph():
    graph = GraphSpec(
        nodes=[
            NodeSpec(
                id="in1",
                type="input",
                label="Input",
                config={"value": "hello"},
                ports=NodePorts(outputs=["value"]),
            ),
            NodeSpec(
                id="py1",
                type="python",
                label="Python",
                config={"code": "outputs['upper'] = inputs['value'].upper()"},
                ports=NodePorts(inputs=["value"], outputs=["upper"]),
            ),
            NodeSpec(
                id="out1",
                type="output",
                label="Output",
                config={},
                ports=NodePorts(inputs=["upper"]),
            ),
        ],
        edges=[
            EdgeSpec(
                id="e1",
                source=PortReference(node="in1", port="value"),
                target=PortReference(node="py1", port="value"),
            ),
            EdgeSpec(
                id="e2",
                source=PortReference(node="py1", port="upper"),
                target=PortReference(node="out1", port="upper"),
            ),
        ],
    )
    settings = RunSettings(llm=LLMSettings(engine="mock", model="test"))
    events: List[Dict[str, object]] = []
    manager = RunManager()

    async def sender(event: Dict[str, object]) -> None:
        events.append(event)

    runner = GraphRunner(graph, settings, run_id="run-1", sender=sender, manager=manager)
    result = await runner.run()

    assert result.final_outputs["out1"]["upper"] == "HELLO"
    event_types = [event["type"] for event in events]
    assert "run_started" in event_types
    assert "run_complete" in event_types


@pytest.mark.asyncio
async def test_replay_reuses_cache_when_possible():
    base_graph = GraphSpec(
        nodes=[
            NodeSpec(
                id="input",
                type="input",
                config={"value": "first"},
                ports=NodePorts(outputs=["value"]),
            ),
            NodeSpec(
                id="py",
                type="python",
                config={"code": "outputs['value'] = inputs['value'] + '!'"},
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
                target=PortReference(node="py", port="value"),
            ),
            EdgeSpec(
                id="e2",
                source=PortReference(node="py", port="value"),
                target=PortReference(node="out", port="value"),
            ),
        ],
    )
    settings = RunSettings()
    manager = RunManager()
    events: List[Dict[str, object]] = []

    async def sender(event: Dict[str, object]) -> None:
        events.append(event)

    runner1 = GraphRunner(base_graph, settings, "base", sender, manager)
    await runner1.run()

    # Modify only the input node value
    modified_graph = GraphSpec(
        nodes=[
            NodeSpec(
                id="input",
                type="input",
                config={"value": "second"},
                ports=NodePorts(outputs=["value"]),
            ),
            base_graph.node_map()["py"],
            base_graph.node_map()["out"],
        ],
        edges=base_graph.edges,
    )

    events.clear()
    runner2 = GraphRunner(modified_graph, settings, "replay", sender, manager)
    await runner2.run(resume=runner1.run_state)

    cached_events = [event for event in events if event["type"] == "node_cached"]
    assert not cached_events, "Modified graph should not reuse caches when node signature changes"


@pytest.mark.asyncio
async def test_loop_node_executes_body_for_each_item():
    loop_body = GraphSpec(
        nodes=[
            NodeSpec(
                id="loop_in",
                type="loopInput",
                config={"binding": "items"},
                ports=NodePorts(outputs=["item"]),
            ),
            NodeSpec(
                id="py",
                type="python",
                config={"code": "outputs['upper'] = inputs['item'].upper()"},
                ports=NodePorts(inputs=["item"], outputs=["upper"]),
            ),
            NodeSpec(
                id="loop_out",
                type="loopOutput",
                config={"target": "results"},
                ports=NodePorts(inputs=["upper"]),
            ),
        ],
        edges=[
            EdgeSpec(
                id="be1",
                source=PortReference(node="loop_in", port="item"),
                target=PortReference(node="py", port="item"),
            ),
            EdgeSpec(
                id="be2",
                source=PortReference(node="py", port="upper"),
                target=PortReference(node="loop_out", port="upper"),
            ),
        ],
    )

    graph = GraphSpec(
        nodes=[
            NodeSpec(
                id="items",
                type="input",
                config={"value": ["red", "green", "blue"]},
                ports=NodePorts(outputs=["items"]),
            ),
            NodeSpec(
                id="loop",
                type="loop",
                config={
                    "bodyGraph": loop_body.model_dump(),
                    "loopOutputs": [
                        {"node": "loop_out", "port": "upper", "target": "results"}
                    ],
                },
                ports=NodePorts(inputs=["items"], outputs=["results"]),
            ),
            NodeSpec(
                id="collector",
                type="output",
                config={},
                ports=NodePorts(inputs=["results"]),
            ),
        ],
        edges=[
            EdgeSpec(
                id="ce1",
                source=PortReference(node="items", port="items"),
                target=PortReference(node="loop", port="items"),
            ),
            EdgeSpec(
                id="ce2",
                source=PortReference(node="loop", port="results"),
                target=PortReference(node="collector", port="results"),
            ),
        ],
    )

    events: List[Dict[str, object]] = []
    settings = RunSettings()
    manager = RunManager()

    async def sender(event: Dict[str, object]) -> None:
        events.append(event)

    runner = GraphRunner(graph, settings, "loop-run", sender, manager)
    result = await runner.run()

    assert result.final_outputs["collector"]["results"] == ["RED", "GREEN", "BLUE"]
    iterations = [
        event
        for event in events
        if event["type"] == "edge_data" and event.get("iteration") is not None
    ]
    assert len(iterations) == 3



@pytest.mark.asyncio
async def test_overrides_trigger_reexecution_and_propagation():
    graph = GraphSpec(
        nodes=[
            NodeSpec(
                id="input",
                type="input",
                config={"value": "first"},
                ports=NodePorts(outputs=["value"]),
            ),
            NodeSpec(
                id="py",
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
                target=PortReference(node="py", port="value"),
            ),
            EdgeSpec(
                id="e2",
                source=PortReference(node="py", port="value"),
                target=PortReference(node="out", port="value"),
            ),
        ],
    )

    settings = RunSettings()
    manager = RunManager()
    events: List[Dict[str, object]] = []

    async def sender(event: Dict[str, object]) -> None:
        events.append(event)

    runner1 = GraphRunner(graph, settings, "first", sender, manager)
    await runner1.run()

    events.clear()
    runner2 = GraphRunner(graph, settings, "override", sender, manager)
    overrides = {"py": {"code": "outputs['value'] = inputs['value'].upper()"}}
    result = await runner2.run(resume=runner1.run_state, overrides=overrides)

    assert result.final_outputs["out"]["value"] == "FIRST"

    cached_nodes = [event["nodeId"] for event in events if event["type"] == "node_cached"]
    assert "input" in cached_nodes
    assert "py" not in cached_nodes

    started_nodes = [event["nodeId"] for event in events if event["type"] == "node_start"]
    assert started_nodes.count("py") == 1
    assert started_nodes.count("out") == 1

