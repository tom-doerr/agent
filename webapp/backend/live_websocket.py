"""WebSocket utilities for real-time audio debugging."""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict

from fastapi import WebSocket, WebSocketDisconnect

from gemini_live_handler import (
    GeminiLiveSession,
    convert_audio_format,
    stream_audio_to_gemini,
)

logger = logging.getLogger(__name__)

MOCK_MODE = os.getenv("MOCK_MODE", "1").lower() in {"1", "true", "yes", "on"}


class LiveAudioProcessor:
    """Coordinates audio chunks received over the WebSocket."""

    def __init__(self, session: GeminiLiveSession) -> None:
        self.session = session

    async def emit_mock_transcript(self, websocket: WebSocket, size: int) -> None:
        await websocket.send_json({"event": "transcript", "text": "[mock chunk]", "bytes": size})

    async def forward_to_gemini(self, websocket: WebSocket, chunk: bytes) -> None:
        async def single_chunk_stream():
            yield chunk

        async for result in stream_audio_to_gemini(single_chunk_stream(), api_key=self.session.api_key, model=self.session.model):
            await websocket.send_json({"event": "transcript", **result})


async def websocket_audio_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    session = GeminiLiveSession()
    processor = LiveAudioProcessor(session)
    await websocket.send_json({"event": "ready", "mock": session.mock_mode})

    try:
        while True:
            message = await websocket.receive()
            data = message.get("text")
            chunk = message.get("bytes")

            if data is not None:
                try:
                    payload: Dict[str, Any] = json.loads(data)
                except json.JSONDecodeError:
                    await websocket.send_json({"event": "error", "detail": "Invalid JSON payload"})
                    continue

                if payload.get("type") == "ping":
                    await websocket.send_json({"event": "pong"})
                elif payload.get("type") == "stop":
                    await websocket.send_json({"event": "stopped"})
                    break
                else:
                    await websocket.send_json({"event": "ack", "payload": payload})

            if chunk:
                converted = await convert_audio_format(chunk)
                if session.mock_mode:
                    await processor.emit_mock_transcript(websocket, len(converted))
                else:  # pragma: no cover - requires external service
                    await processor.forward_to_gemini(websocket, converted)

    except WebSocketDisconnect:
        logger.debug("Audio websocket disconnected")
    finally:
        await websocket.close()


__all__ = ["LiveAudioProcessor", "websocket_audio_endpoint"]
