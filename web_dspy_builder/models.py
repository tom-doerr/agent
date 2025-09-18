"""Pydantic models and dataclasses for the DSPy graph runner."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class PortReference(BaseModel):
    """Reference to a specific port on a node."""

    node: str
    port: str


class EdgeSpec(BaseModel):
    """Serialized edge definition."""

    id: str
    source: PortReference
    target: PortReference


class NodePorts(BaseModel):
    """Definition of input and output ports for a node."""

    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)


class NodeSpec(BaseModel):
    """Serialized representation of a node in the DSPy graph."""

    id: str
    type: str
    label: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    ports: NodePorts = Field(default_factory=NodePorts)

    class Config:
        arbitrary_types_allowed = True

    def signature(self) -> str:
        """Return a stable signature used to detect node changes."""

        payload = {
            "type": self.type,
            "label": self.label,
            "config": self.config,
            "ports": self.ports.model_dump(mode="python"),
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()


class GraphSpec(BaseModel):
    """Full graph specification received from the UI."""

    id: Optional[str] = None
    nodes: List[NodeSpec]
    edges: List[EdgeSpec]
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def node_map(self) -> Dict[str, NodeSpec]:
        return {node.id: node for node in self.nodes}

    def edges_from(self, node_id: str) -> List[EdgeSpec]:
        return [edge for edge in self.edges if edge.source.node == node_id]

    def edges_to(self, node_id: str) -> List[EdgeSpec]:
        return [edge for edge in self.edges if edge.target.node == node_id]


class LLMSettings(BaseModel):
    """Configuration for the language model used during execution."""

    engine: Literal["mock", "dspy", "openrouter", "openai", "ollama"] = "mock"
    model: Optional[str] = None
    temperature: float = 0.0
    max_tokens: int = 2048
    params: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("temperature")
    @classmethod
    def clamp_temperature(cls, value: float) -> float:  # noqa: D401
        """Ensure temperatures stay inside the allowed range."""

        return max(0.0, min(value, 2.0))

    @field_validator("max_tokens")
    @classmethod
    def clamp_max_tokens(cls, value: int) -> int:  # noqa: D401
        """Restrict max tokens to a sane range."""

        return max(16, min(value, 100000))


class RunSettings(BaseModel):
    """Top level settings for a graph run."""

    llm: LLMSettings = Field(default_factory=LLMSettings)
    allow_cache_reuse: bool = True


class RunRequest(BaseModel):
    """Incoming request to execute or replay a graph."""

    action: Literal["run", "replay"] = "run"
    graph: GraphSpec
    settings: RunSettings = Field(default_factory=RunSettings)
    run_id: Optional[str] = None
    base_run_id: Optional[str] = None
    start_node: Optional[str] = None
    overrides: Dict[str, Any] = Field(default_factory=dict)


@dataclass
class EdgeTransmission:
    """A single transmission on an edge."""

    edge_id: str
    source: PortReference
    target: PortReference
    value: Any
    iteration: Optional[int] = None
    cached: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_event(self) -> Dict[str, Any]:
        return {
            "type": "edge_data",
            "edgeId": self.edge_id,
            "source": self.source.model_dump(mode="python"),
            "target": self.target.model_dump(mode="python"),
            "value": self.value,
            "iteration": self.iteration,
            "cached": self.cached,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class NodeCache:
    """Cached execution information for a node."""

    node_id: str
    outputs: Dict[str, Any]
    transmissions: List[EdgeTransmission]
    signature: str
    started_at: datetime
    completed_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_event(self) -> Dict[str, Any]:
        return {
            "type": "node_cached",
            "nodeId": self.node_id,
            "outputs": self.outputs,
            "metadata": self.metadata,
            "startedAt": self.started_at.isoformat(),
            "completedAt": self.completed_at.isoformat(),
        }


@dataclass
class RunState:
    """Stored state for a previous run."""

    run_id: str
    graph: GraphSpec
    settings: RunSettings
    started_at: datetime
    node_results: Dict[str, NodeCache] = field(default_factory=dict)
    timeline: List[Dict[str, Any]] = field(default_factory=list)

    def record_event(self, event: Dict[str, Any]) -> None:
        self.timeline.append(event)

    def node_signature(self, node_id: str) -> Optional[str]:
        cache = self.node_results.get(node_id)
        return cache.signature if cache else None

    def cached_nodes(self) -> Iterable[str]:
        return self.node_results.keys()

