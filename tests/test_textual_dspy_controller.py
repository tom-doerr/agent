import pytest

from textual_dspy.controller import DSpyProgramController
from textual_dspy.document import ProgramDocument, default_document
from web_dspy_builder.models import EdgeSpec, GraphSpec, NodePorts, NodeSpec, PortReference, RunSettings


@pytest.mark.asyncio
async def test_controller_runs_default_graph():
    controller = DSpyProgramController()
    events = []

    async def listener(event):
        events.append(event)

    controller.add_listener(listener)
    await controller.run()

    event_types = {event["type"] for event in events}
    assert "run_started" in event_types
    assert "run_complete" in event_types
    edge_events = [event for event in events if event["type"] == "edge_data"]
    assert edge_events, "expected edge transmissions from default program"


@pytest.mark.asyncio
async def test_live_override_applies_during_run():
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
                id="edge1",
                source=PortReference(node="input", port="value"),
                target=PortReference(node="py", port="value"),
            ),
            EdgeSpec(
                id="edge2",
                source=PortReference(node="py", port="value"),
                target=PortReference(node="out", port="value"),
            ),
        ],
    )
    document = ProgramDocument(graph=graph, settings=RunSettings())
    controller = DSpyProgramController(document=document)

    async def listener(event):
        if event["type"] == "node_start" and event.get("nodeId") == "py":
            controller.set_override(
                "py",
                {"code": "outputs['value'] = inputs['value'].upper()"},
            )

    controller.add_listener(listener)
    await controller.run()

    # The override should modify the python node output
    transmissions = [event for event in controller.event_history if event["type"] == "edge_data"]
    final_value = next(
        (event["value"] for event in transmissions if event["edgeId"] == "edge2"),
        None,
    )
    assert final_value == "HELLO"


def test_program_document_roundtrip(tmp_path):
    document = default_document()
    target = tmp_path / "program.json"
    document.save(target)
    loaded = ProgramDocument.load(target)
    assert loaded.graph.metadata == document.graph.metadata
    assert loaded.settings.model_dump() == document.settings.model_dump()
