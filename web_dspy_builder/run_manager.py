"""State management for graph runs."""

from __future__ import annotations

from typing import Dict, Optional

from .models import NodeCache, RunState


class RunManager:
    """In-memory registry of graph run states."""

    def __init__(self) -> None:
        self._runs: Dict[str, RunState] = {}

    def register(self, run_state: RunState) -> None:
        """Register a new run state."""

        self._runs[run_state.run_id] = run_state

    def get(self, run_id: str) -> Optional[RunState]:
        """Retrieve the stored state for a run if it exists."""

        return self._runs.get(run_id)

    def update_node(self, run_id: str, node_cache: NodeCache) -> None:
        """Store the execution results for a node."""

        run_state = self._runs.get(run_id)
        if not run_state:
            return
        run_state.node_results[node_cache.node_id] = node_cache

    def forget(self, run_id: str) -> None:
        """Remove a run from memory."""

        self._runs.pop(run_id, None)

    def all_runs(self) -> Dict[str, RunState]:
        """Return a copy of all known runs."""

        return dict(self._runs)

