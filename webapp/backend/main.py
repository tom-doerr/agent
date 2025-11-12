"""FastAPI entrypoint for the DSPy web backend."""
from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, File, HTTPException, Query, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from audio_handler import MOCK_MODE as AUDIO_MOCK_MODE
from audio_handler import transcribe_audio
from gemini_handler import (
    MOCK_MODE as GEMINI_MOCK_MODE,
    DEFAULT_AUDIO_MODEL,
    get_gemini_response,
    stream_gemini_response,
)
from live_websocket import websocket_audio_endpoint

MOCK_MODE = AUDIO_MOCK_MODE or GEMINI_MOCK_MODE

TEXT_MODELS = {
    "gemini-flash": "gemini/gemini-2.0-flash-exp",
    "gemini-flash-thinking": "gemini/gemini-2.0-flash-thinking-exp",
    "gemini-pro": "gemini/gemini-1.5-pro",
    "deepseek-r1": "ollama/deepseek-r1:8b",
    "mock": "mock",
}

AUDIO_MODELS = {
    "gemini-flash": DEFAULT_AUDIO_MODEL,
    "gemini-pro": "gemini/gemini-1.5-pro",
    "mock": "mock",
}

ALLOW_ORIGINS = [
    os.getenv("FRONTEND_ORIGIN", "http://localhost:3000"),
    "*" if os.getenv("ALLOW_ANY_ORIGIN", "0") == "1" else None,
]
ALLOW_ORIGINS = [origin for origin in ALLOW_ORIGINS if origin]


class Question(BaseModel):
    question: str
    model: str | None = None


def ensure_supported_model(name: str | None, *, fallback: str, supported: dict[str, str]) -> str:
    if not name:
        return fallback
    if name not in supported:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported model '{name}'. Available: {', '.join(supported)}",
        )
    return name


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    yield


app = FastAPI(title="DSPy Web Backend", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok", "mock": str(MOCK_MODE).lower()}


@app.get("/models")
async def get_models() -> dict[str, list[str]]:
    return {"text": list(TEXT_MODELS.keys()), "audio": list(AUDIO_MODELS.keys())}


@app.post("/audio-stream")
async def audio_stream_endpoint(
    audio: UploadFile = File(...),
    model: str = Query("gemini-flash", description="Model to use for audio processing"),
) -> dict[str, str]:
    resolved = ensure_supported_model(model, fallback="gemini-flash", supported=AUDIO_MODELS)
    resolved_backend = AUDIO_MODELS[resolved]
    result = await transcribe_audio(audio, model=resolved_backend)
    result.setdefault("model", resolved)
    return result


@app.post("/generate")
async def generate_response(question: Question) -> dict[str, str]:
    resolved_key = ensure_supported_model(question.model, fallback="gemini-flash", supported=TEXT_MODELS)
    resolved_model = TEXT_MODELS[resolved_key]
    answer = get_gemini_response(question.question, model=resolved_model)
    return {"answer": answer, "model": resolved_key}


async def _stream(question: str, model_key: str) -> StreamingResponse:
    resolved_model = TEXT_MODELS[model_key]

    async def event_stream() -> AsyncGenerator[str, None]:
        async for chunk in stream_gemini_response(question, model=resolved_model):
            yield chunk
            await asyncio.sleep(0)

    return StreamingResponse(event_stream(), media_type="text/plain")


@app.post("/stream")
async def stream_answer(question: Question) -> StreamingResponse:
    resolved_key = ensure_supported_model(question.model, fallback="gemini-flash", supported=TEXT_MODELS)
    return await _stream(question.question, resolved_key)


@app.get("/stream/{question}")
async def stream_answer_from_path(
    question: str,
    model: str = Query("gemini-flash", description="Model to use for text generation"),
) -> StreamingResponse:
    resolved_key = ensure_supported_model(model, fallback="gemini-flash", supported=TEXT_MODELS)
    return await _stream(question, resolved_key)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            payload = await websocket.receive_json()
            question = payload.get("question")
            model_name = ensure_supported_model(payload.get("model"), fallback="gemini-flash", supported=TEXT_MODELS)
            if not question:
                await websocket.send_json({"event": "error", "detail": "Missing question"})
                continue

            async for chunk in stream_gemini_response(question, model=TEXT_MODELS[model_name]):
                await websocket.send_text(chunk)
            await websocket.send_json({"event": "done"})
    except WebSocketDisconnect:
        return


@app.websocket("/ws/audio-live")
async def websocket_audio_live(websocket: WebSocket) -> None:
    await websocket_audio_endpoint(websocket)
