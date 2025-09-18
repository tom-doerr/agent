"""Program document utilities for the Textual DSPy builder."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from web_dspy_builder.models import (
    EdgeSpec,
    GraphSpec,
    LLMSettings,
    NodePorts,
    NodeSpec,
    PortReference,
    RunSettings,
)


@dataclass
class ProgramDocument:
    """Container for a graph specification and run settings."""

    graph: GraphSpec
    settings: RunSettings
    path: Optional[Path] = None

    def to_dict(self) -> Dict[str, object]:
        """Serialize the document to a python dictionary."""

        return {
            "graph": self.graph.model_dump(mode="python"),
            "settings": self.settings.model_dump(mode="python"),
        }

    def save(self, path: Path) -> None:
        """Persist the document as JSON to ``path``."""

        path = Path(path)
        path.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True))
        self.path = path

    @classmethod
    def load(cls, path: Path) -> "ProgramDocument":
        """Load a document from disk."""

        path = Path(path)
        payload = json.loads(path.read_text())
        graph = GraphSpec.model_validate(payload["graph"])
        settings = RunSettings.model_validate(payload.get("settings", {}))
        return cls(graph=graph, settings=settings, path=path)


_DEF_OBSERVATION = "The user observes an interesting scenario that needs reasoning."
_DEF_GOALS = "Summarise the situation and outline a plan."
_DEF_MEMORY = "No prior episodic memory."


def _default_cognition_graph() -> GraphSpec:
    """Return a default cognition program graph."""

    nodes = [
        NodeSpec(
            id="input_observation",
            type="input",
            label="Observation",
            config={"value": _DEF_OBSERVATION},
            ports=NodePorts(outputs=["value"]),
        ),
        NodeSpec(
            id="input_goals",
            type="input",
            label="Goals",
            config={"value": _DEF_GOALS},
            ports=NodePorts(outputs=["value"]),
        ),
        NodeSpec(
            id="input_memory",
            type="input",
            label="Episodic Memory",
            config={"value": _DEF_MEMORY},
            ports=NodePorts(outputs=["value"]),
        ),
        NodeSpec(
            id="typed_cognition",
            type="cognition",
            label="Typed Cognition Agent",
            config={
                "observation": _DEF_OBSERVATION,
                "goals": _DEF_GOALS,
                "episodic_memory": _DEF_MEMORY,
                "constraints": "",
                "utility_def": "",
                "prior_belief": "",
                "attention_results": "",
                "system_events": "",
            },
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
            id="output_summary",
            type="output",
            label="Summary",
            config={},
            ports=NodePorts(inputs=["decision", "update"]),
        ),
    ]
    edges = [
        EdgeSpec(
            id="edge_obs",
            source=PortReference(node="input_observation", port="value"),
            target=PortReference(node="typed_cognition", port="observation"),
        ),
        EdgeSpec(
            id="edge_goals",
            source=PortReference(node="input_goals", port="value"),
            target=PortReference(node="typed_cognition", port="goals"),
        ),
        EdgeSpec(
            id="edge_memory",
            source=PortReference(node="input_memory", port="value"),
            target=PortReference(node="typed_cognition", port="episodic_memory"),
        ),
        EdgeSpec(
            id="edge_decision",
            source=PortReference(node="typed_cognition", port="decision"),
            target=PortReference(node="output_summary", port="decision"),
        ),
        EdgeSpec(
            id="edge_update",
            source=PortReference(node="typed_cognition", port="update"),
            target=PortReference(node="output_summary", port="update"),
        ),
    ]
    return GraphSpec(
        id="typed-cognition-default",
        nodes=nodes,
        edges=edges,
        metadata={"title": "Typed Cognition Agent"},
    )


def default_document() -> ProgramDocument:
    """Return a program document seeded with the cognition graph."""

    return ProgramDocument(
        graph=_default_cognition_graph(),
        settings=RunSettings(llm=LLMSettings(engine="mock", model="gpt-4o-mini")),
    )
