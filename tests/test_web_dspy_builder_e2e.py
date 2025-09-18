"""End-to-end tests for the DSPy visual builder server."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

import pytest
from fastapi.testclient import TestClient

from web_dspy_builder import server
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


@pytest.fixture()
def builder_client(monkeypatch: pytest.MonkeyPatch) -> Tuple[TestClient, RunManager]:
    """Provide a FastAPI test client with an isolated run manager."""

    manager = RunManager()
    monkeypatch.setattr(server, "run_manager", manager)
    app = server.create_app()
    with TestClient(app) as client:
        yield client, manager


def _linear_graph(initial_value: str = "hello") -> GraphSpec:
    """Create a simple linear graph with python processing."""

    return GraphSpec(
        id="linear",
        nodes=[
            NodeSpec(
                id="input",
                type="input",
                config={"value": initial_value},
                ports=NodePorts(outputs=["value"]),
            ),
            NodeSpec(
                id="transform",
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
                target=PortReference(node="transform", port="value"),
            ),
            EdgeSpec(
                id="e2",
                source=PortReference(node="transform", port="value"),
                target=PortReference(node="out", port="value"),
            ),
        ],
    )


def _drain_events(websocket) -> List[Dict[str, Any]]:
    """Read events until the server reports completion or an error."""

    events: List[Dict[str, Any]] = []
    while True:
        event = websocket.receive_json()
        events.append(event)
        if event["type"] in {"run_complete", "run_error"}:
            break
    return events


def test_builder_serves_frontend_assets(builder_client: Tuple[TestClient, RunManager]) -> None:
    """The FastAPI server should expose the built frontend assets."""

    client, _ = builder_client

    index_response = client.get("/")
    assert index_response.status_code == 200
    assert "<!DOCTYPE html>" in index_response.text
    assert "DSPy" in index_response.text

    script_response = client.get("/static/app.js")
    assert script_response.status_code == 200
    assert 'LiteGraph.registerNodeType("dspy/python"' in script_response.text

    css_response = client.get("/static/styles.css")
    assert css_response.status_code == 200
    assert "#graph-canvas" in css_response.text


def test_websocket_linear_run_records_events(
    builder_client: Tuple[TestClient, RunManager]
) -> None:
    """Executing a graph through the WebSocket produces streamed events and records the run."""

    client, _ = builder_client
    run_id = "linear-run"
    graph = _linear_graph()
    settings = RunSettings(llm=LLMSettings(engine="mock", model="e2e"))

    with client.websocket_connect("/ws") as websocket:
        websocket.send_json(
            {
                "action": "run",
                "run_id": run_id,
                "graph": graph.model_dump(mode="json"),
                "settings": settings.model_dump(mode="json"),
            }
        )
        events = _drain_events(websocket)

    assert events[0]["type"] == "run_started"
    complete_event = events[-1]
    assert complete_event["type"] == "run_complete"
    assert complete_event["outputs"]["out"]["value"] == "hello"

    node_starts = {
        event["nodeId"]
        for event in events
        if event["type"] == "node_start"
    }
    assert node_starts == {"input", "transform", "out"}

    runs_response = client.get("/api/runs")
    runs_payload = runs_response.json()
    run_ids = {entry["runId"] for entry in runs_payload["runs"]}
    assert run_id in run_ids

    detail_response = client.get(f"/api/runs/{run_id}")
    detail_payload = detail_response.json()
    assert detail_payload["runId"] == run_id
    assert len(detail_payload["timeline"]) == len(events)


def test_websocket_replay_reuses_cache_and_applies_overrides(
    builder_client: Tuple[TestClient, RunManager]
) -> None:
    """A replay can reuse caches while overriding nodes and starting mid-graph."""

    client, _ = builder_client
    base_run_id = "base-run"
    replay_run_id = "replay-run"

    graph = _linear_graph("first")

    with client.websocket_connect("/ws") as websocket:
        websocket.send_json(
            {
                "action": "run",
                "run_id": base_run_id,
                "graph": graph.model_dump(mode="json"),
                "settings": RunSettings().model_dump(mode="json"),
            }
        )
        base_events = _drain_events(websocket)

    assert base_events[-1]["outputs"]["out"]["value"] == "first"

    overrides = {
        "transform": {"code": "outputs['value'] = inputs['value'].upper()"}
    }

    with client.websocket_connect("/ws") as websocket:
        websocket.send_json(
            {
                "action": "replay",
                "run_id": replay_run_id,
                "base_run_id": base_run_id,
                "start_node": "transform",
                "graph": graph.model_dump(mode="json"),
                "settings": RunSettings().model_dump(mode="json"),
                "overrides": overrides,
            }
        )
        replay_events = _drain_events(websocket)

    cached_nodes = {
        event["nodeId"]
        for event in replay_events
        if event["type"] == "node_cached"
    }
    assert "input" in cached_nodes
    assert "transform" not in cached_nodes

    replay_complete = replay_events[-1]
    assert replay_complete["outputs"]["out"]["value"] == "FIRST"

    detail_payload = client.get(f"/api/runs/{replay_run_id}").json()
    assert detail_payload["graphId"] == graph.id
    assert detail_payload["nodes"] == ["transform", "out"]
    assert "input" not in detail_payload["nodes"]
    assert any(event["type"] == "run_complete" for event in detail_payload["timeline"])
