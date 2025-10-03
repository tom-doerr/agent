"""Utility helpers for handling audio uploads."""
from __future__ import annotations

import os
from typing import Dict

from fastapi import HTTPException, UploadFile

# Default to mock mode so the stack works without external services.
MOCK_MODE = os.getenv("MOCK_MODE", "1").lower() in {"1", "true", "yes", "on"}


async def transcribe_audio(audio_file: UploadFile, model: str | None = None) -> Dict[str, str]:
    """Return a transcription payload for an uploaded audio file.

    When MOCK_MODE is enabled, the transcription is simulated so that the
    frontend can be developed without contacting external APIs.
    """
    if audio_file is None:
        raise HTTPException(status_code=400, detail="No audio file provided")

    contents = await audio_file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded audio file is empty")

    mime_type = audio_file.content_type or "audio/webm"

    if MOCK_MODE:
        return {
            "model": model or "mock",
            "mime_type": mime_type,
            "text": "[mock transcription] audio captured successfully",
        }

    try:
        from gemini_handler import transcribe_with_gemini  # deferred import

        text = transcribe_with_gemini(contents, mime_type=mime_type, model=model)
        return {"model": model or "gemini-flash", "mime_type": mime_type, "text": text}
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive fallback
        raise HTTPException(status_code=502, detail=f"Transcription failed: {exc}") from exc


__all__ = ["transcribe_audio", "MOCK_MODE"]
