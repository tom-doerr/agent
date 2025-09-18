"""FastAPI server powering the DSPy visual builder."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .graph_runner import GraphRunner
from .models import RunRequest
from .run_manager import RunManager


FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"

run_manager = RunManager()


def create_app() -> FastAPI:
    app = FastAPI(title="DSPy Visual Builder")

    if FRONTEND_DIR.exists():
        app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    async def index() -> FileResponse:
        index_path = FRONTEND_DIR / "index.html"
        if not index_path.exists():
            raise HTTPException(status_code=404, detail="frontend build not found")
        return FileResponse(index_path)

    @app.get("/api/runs")
    async def list_runs() -> Dict[str, object]:
        runs = []
        for run_id, state in run_manager.all_runs().items():
            runs.append(
                {
                    "runId": run_id,
                    "graphId": state.graph.id,
                    "startedAt": state.started_at.isoformat(),
                    "nodeCount": len(state.node_results),
                }
            )
        return {"runs": runs}

    @app.get("/api/runs/{run_id}")
    async def get_run(run_id: str) -> Dict[str, object]:
        state = run_manager.get(run_id)
        if not state:
            raise HTTPException(status_code=404, detail="run not found")
        return {
            "runId": run_id,
            "graphId": state.graph.id,
            "startedAt": state.started_at.isoformat(),
            "nodes": list(state.node_results.keys()),
            "timeline": state.timeline,
        }

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        await websocket.accept()
        try:
            while True:
                message = await websocket.receive_text()
                payload = json.loads(message)
                request = RunRequest.model_validate(payload)
                run_id = request.run_id or str(uuid.uuid4())
                base_state = None
                if request.base_run_id:
                    base_state = run_manager.get(request.base_run_id)
                    if base_state is None:
                        await websocket.send_json(
                            {
                                "type": "run_error",
                                "runId": run_id,
                                "message": f"Unknown base run {request.base_run_id}",
                            }
                        )
                        continue

                graph = request.graph
                settings = request.settings

                async def sender(event: Dict[str, object]) -> None:
                    await websocket.send_json(event)

                runner = GraphRunner(
                    graph,
                    settings,
                    run_id=run_id,
                    sender=sender,
                    manager=run_manager,
                )

                resume_state = base_state if request.action == "replay" else None
                start_node = request.start_node if request.action == "replay" else None
                try:
                    await runner.run(
                        resume=resume_state,
                        start_node=start_node,
                        overrides=request.overrides,
                    )
                except Exception as exc:  # pragma: no cover - error propagation
                    await websocket.send_json(
                        {
                            "type": "run_error",
                            "runId": run_id,
                            "message": str(exc),
                        }
                    )
        except WebSocketDisconnect:
            return

    return app


app = create_app()

