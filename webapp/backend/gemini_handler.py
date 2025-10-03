"""Thin wrappers around LiteLLM for Gemini interactions."""
from __future__ import annotations

import asyncio
import os
from typing import AsyncGenerator, Optional

try:
    import litellm
except ImportError as exc:  # pragma: no cover - dependency should exist
    raise RuntimeError("litellm must be installed to use gemini_handler") from exc

MOCK_MODE = os.getenv("MOCK_MODE", "1").lower() in {"1", "true", "yes", "on"}
DEFAULT_MODEL = os.getenv("DEFAULT_TEXT_MODEL", "gemini/gemini-2.0-flash-exp")
DEFAULT_AUDIO_MODEL = os.getenv("DEFAULT_AUDIO_MODEL", "gemini/gemini-2.0-flash-exp")

_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if _API_KEY:
    os.environ.setdefault("GOOGLE_API_KEY", _API_KEY)

_set_verbose = getattr(litellm, "set_verbose", None)
if callable(_set_verbose):
    _set_verbose(os.getenv("LITELLM_LOG", "INFO").upper() == "DEBUG")


def _resolve_model(model: Optional[str], default: str) -> str:
    return model or default


def get_gemini_response(question: str, model: Optional[str] = None) -> str:
    """Return a single response for the provided question."""
    if MOCK_MODE or not _API_KEY:
        return f"[mock response] {question}" if question else "[mock response]"

    response = litellm.completion(
        model=_resolve_model(model, DEFAULT_MODEL),
        messages=[{"role": "user", "content": question}],
    )
    choice = response.get("choices", [{}])[0]
    message = choice.get("message", {})
    return message.get("content", "")


async def stream_gemini_response(
    question: str,
    model: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """Yield chunks while streaming a Gemini response."""
    if MOCK_MODE or not _API_KEY:
        yield f"[mock stream] {question}"
        return

    stream = await litellm.acompletion(
        model=_resolve_model(model, DEFAULT_MODEL),
        messages=[{"role": "user", "content": question}],
        stream=True,
    )

    async for chunk in stream:
        for choice in chunk.get("choices", []):
            delta = choice.get("delta") or {}
            content = delta.get("content")
            if content:
                yield content
        await asyncio.sleep(0)


def transcribe_with_gemini(
    audio_content: bytes,
    mime_type: str = "audio/webm",
    model: Optional[str] = None,
) -> str:
    """Transcribe audio bytes using Gemini via LiteLLM."""
    if MOCK_MODE or not _API_KEY:
        return "[mock transcription]"

    # LiteLLM currently proxies speech-to-text through the Chat Completions
    # endpoint using the audio tool. This keeps the implementation minimal.
    response = litellm.completion(
        model=_resolve_model(model, DEFAULT_AUDIO_MODEL),
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_audio",
                        "input_audio": {"data": audio_content, "mime_type": mime_type},
                    }
                ],
            }
        ],
    )
    choice = response.get("choices", [{}])[0]
    message = choice.get("message", {})
    content = message.get("content")
    if isinstance(content, list):
        # Gemini audio responses arrive as structured content blocks.
        texts = [item.get("text", "") for item in content if isinstance(item, dict)]
        return " ".join(part for part in texts if part)
    return content or ""


__all__ = [
    "DEFAULT_MODEL",
    "DEFAULT_AUDIO_MODEL",
    "MOCK_MODE",
    "get_gemini_response",
    "stream_gemini_response",
    "transcribe_with_gemini",
]
