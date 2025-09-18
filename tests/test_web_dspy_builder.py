import asyncio
from typing import Any, Dict, List

import pytest

import cognition_typed_dspy as cognition

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


@pytest.mark.asyncio
async def test_live_override_applies_during_execution():
    graph = GraphSpec(
        nodes=[
            NodeSpec(
                id="input",
                type="input",
                config={"value": "hello"},
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

    overrides: Dict[str, Dict[str, Any]] = {}
    events: List[Dict[str, Any]] = []
    settings = RunSettings()
    manager = RunManager()

    async def sender(event: Dict[str, Any]) -> None:
        events.append(event)
        if event["type"] == "node_start" and event.get("nodeId") == "py":
            overrides["py"] = {
                "code": "outputs['value'] = inputs['value'].upper()",
            }

    runner = GraphRunner(graph, settings, "live-override", sender, manager)
    result = await runner.run(overrides=overrides)

    assert result.final_outputs["out"]["value"] == "HELLO"
    assert any(event["type"] == "edge_data" for event in events)


@pytest.mark.asyncio
async def test_cognition_node_executor_serialises_structured_outputs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: List[Dict[str, Any]] = []
    settings = RunSettings()
    manager = RunManager()

    calls: List[Dict[str, Any]] = []
    stub_outputs = {
        "percept": cognition.Percept(facts=["fact"], uncertainties=["unknown"]),
        "belief": cognition.Belief(
            entities=["entity"],
            assumptions=["assumption"],
            epistemic=0.5,
            aleatoric=0.25,
        ),
        "affect": cognition.Affect(
            confidence=0.9,
            surprise=0.1,
            risk=0.2,
            budget_spend=5.0,
            budget_cap=10.0,
        ),
        "plans": [cognition.Plan(id="plan-1", steps=["step one"])],
        "scored": [
            cognition.ScoredPlan(
                id="plan-1",
                EV=1.5,
                risk=0.3,
                confidence=0.8,
                rationale="solid",
            )
        ],
        "decision": cognition.Decision(
            choice="execute",
            plan_id="plan-1",
            action_tool="tool",
            action_args={"foo": "bar"},
            idempotency_key="key-1",
        ),
        "verification": cognition.Verification(checks=["check"], all_passed=True),
        "outcome": cognition.Outcome(
            reward=2.0,
            policy_violations=0,
            risk_flag=False,
            notes="ok",
        ),
        "update": cognition.UpdateNote(note="remember"),
    }

    class DummyAgent:
        def forward(self, **kwargs: Any) -> Dict[str, Any]:  # pragma: no cover - simple stub
            calls.append(dict(kwargs))
            return stub_outputs

    monkeypatch.setattr(cognition, "CognitionAgent", DummyAgent)

    graph = GraphSpec(
        nodes=[
            NodeSpec(
                id="source",
                type="input",
                config={"value": "signal"},
                ports=NodePorts(outputs=["observation"]),
            ),
            NodeSpec(
                id="cognition",
                type="cognition",
                config={
                    "episodic_memory": "history",
                    "goals": "achieve",
                    "constraints": "bounded",
                    "utility_def": "utility",
                    "prior_belief": "baseline",
                    "attention_results": "attention",
                    "system_events": "none",
                },
                ports=NodePorts(
                    inputs=["observation"],
                    outputs=["decision", "percept"],
                ),
            ),
            NodeSpec(
                id="sink",
                type="output",
                config={},
                ports=NodePorts(inputs=["decision"]),
            ),
        ],
        edges=[
            EdgeSpec(
                id="e1",
                source=PortReference(node="source", port="observation"),
                target=PortReference(node="cognition", port="observation"),
            ),
            EdgeSpec(
                id="e2",
                source=PortReference(node="cognition", port="decision"),
                target=PortReference(node="sink", port="decision"),
            ),
        ],
    )

    async def sender(event: Dict[str, Any]) -> None:
        events.append(event)

    runner = GraphRunner(graph, settings, "cog-run", sender, manager)
    result = await runner.run()

    assert calls and calls[0]["observation"] == "signal"
    assert calls[0]["goals"] == "achieve"

    cognition_outputs = result.node_outputs["cognition"]
    assert cognition_outputs["decision"]["choice"] == "execute"
    assert cognition_outputs["percept"]["facts"] == ["fact"]
    assert cognition_outputs["plans"][0]["id"] == "plan-1"

    metadata = runner.run_state.node_results["cognition"].metadata
    assert metadata["inputs"]["constraints"] == "bounded"

    assert result.final_outputs["sink"]["decision"]["choice"] == "execute"


@pytest.mark.asyncio
async def test_cognition_executor_fallback_on_error(monkeypatch: pytest.MonkeyPatch) -> None:
    events: List[Dict[str, Any]] = []

    def failing_forward(self, **kwargs):  # noqa: ANN001 - signature fixed by monkeypatch
        raise RuntimeError("lm unavailable")

    monkeypatch.setattr(cognition.CognitionAgent, "forward", failing_forward)

    cognition_config = {
        "observation": "Offline observation",
        "goals": "Offline goals",
        "episodic_memory": "Offline memory",
        "constraints": "",
        "utility_def": "",
        "prior_belief": "",
        "attention_results": "",
        "system_events": "",
    }

    graph = GraphSpec(
        nodes=[
            NodeSpec(
                id="obs",
                type="input",
                config={"value": cognition_config["observation"]},
                ports=NodePorts(outputs=["value"]),
            ),
            NodeSpec(
                id="cog",
                type="cognition",
                config=cognition_config,
                ports=NodePorts(
                    inputs=[
                        "observation",
                        "goals",
                        "episodic_memory",
                        "constraints",
                        "utility_def",
                        "prior_belief",
                        "attention_results",
                        "system_events",
                    ],
                    outputs=[
                        "percept",
                        "belief",
                        "affect",
                        "plans",
                        "scored",
                        "decision",
                        "verification",
                        "outcome",
                        "update",
                    ],
                ),
            ),
            NodeSpec(
                id="summary",
                type="output",
                config={},
                ports=NodePorts(inputs=["decision", "update"]),
            ),
        ],
        edges=[
            EdgeSpec(
                id="edge_obs",
                source=PortReference(node="obs", port="value"),
                target=PortReference(node="cog", port="observation"),
            ),
            EdgeSpec(
                id="edge_dec",
                source=PortReference(node="cog", port="decision"),
                target=PortReference(node="summary", port="decision"),
            ),
            EdgeSpec(
                id="edge_upd",
                source=PortReference(node="cog", port="update"),
                target=PortReference(node="summary", port="update"),
            ),
        ],
    )

    settings = RunSettings()
    manager = RunManager()

    async def sender(event: Dict[str, Any]) -> None:
        events.append(event)

    runner = GraphRunner(graph, settings, "fallback", sender, manager)
    result = await runner.run()

    summary = result.final_outputs["summary"]
    assert summary["decision"]["choice"] == "execute"
    assert summary["update"]["note"]

    node_end_events = [
        event for event in events if event["type"] == "node_end" and event.get("nodeId") == "cog"
    ]
    assert node_end_events and node_end_events[0]["metadata"].get("fallback") is True

    edge_values = [
        event["value"]
        for event in events
        if event["type"] == "edge_data" and event.get("edgeId") == "edge_dec"
    ]
    assert edge_values and edge_values[0]["choice"] == "execute"

