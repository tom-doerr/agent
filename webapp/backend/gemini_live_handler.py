"""Lightweight helpers for live audio streaming.

The real-time Gemini Live API is still experimental, so this module keeps a
simple interface that can run in MOCK_MODE without external dependencies.
"""
from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
from typing import Any, AsyncGenerator, Dict, Optional

logger = logging.getLogger(__name__)

MOCK_MODE = os.getenv("MOCK_MODE", "1").lower() in {"1", "true", "yes", "on"}
DEFAULT_LIVE_MODEL = os.getenv("DEFAULT_LIVE_MODEL", "gemini-2.0-flash-exp")


class GeminiLiveSession:
    """Container for managing Gemini Live configuration."""

    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_LIVE_MODEL) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model = model
        self.mock_mode = MOCK_MODE or not self.api_key

    async def send_audio(self, audio_chunk: bytes) -> Dict[str, Any]:
        """Pretend to send audio to Gemini Live and return a response payload."""
        if self.mock_mode:
            # Provide deterministic mock data for the UI.
            await asyncio.sleep(0)
            return {
                "type": "mock-transcript",
                "text": "[mock live transcript chunk]",
                "bytes": len(audio_chunk),
            }

        raise RuntimeError("Real-time Gemini Live streaming is not configured")


async def convert_audio_format(audio_data: bytes, input_format: str = "webm") -> bytes:
    """Placeholder that simply returns the provided audio for now."""
    await asyncio.sleep(0)
    return audio_data


async def stream_audio_to_gemini(
    audio_stream: AsyncGenerator[bytes, None],
    api_key: Optional[str] = None,
    model: str = DEFAULT_LIVE_MODEL,
) -> AsyncGenerator[Dict[str, Any], None]:
    """Stream audio chunks to Gemini Live and yield incremental results."""
    session = GeminiLiveSession(api_key=api_key, model=model)
    async for chunk in audio_stream:
        if not chunk:
            continue
        result = await session.send_audio(chunk)
        yield result


async def test_live_api() -> Dict[str, Any]:
    """Simple diagnostic hook for manual testing."""
    sample = base64.b64encode(b"sample").decode()
    session = GeminiLiveSession()
    payload = await session.send_audio(base64.b64decode(sample))
    return {"session_mock": session.mock_mode, "payload": payload}


async def run() -> None:
    """Entrypoint helper for manual execution."""
    result = await test_live_api()
    logger.info("Live API test result: %s", json.dumps(result))


__all__ = [
    "GeminiLiveSession",
    "convert_audio_format",
    "stream_audio_to_gemini",
    "test_live_api",
    "run",
]
