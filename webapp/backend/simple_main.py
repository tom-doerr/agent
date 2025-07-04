from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio
import json
from typing import AsyncGenerator

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Simple Streaming API"}

async def generate_response(question: str) -> AsyncGenerator[str, None]:
    """Generate streaming response"""
    answer = f"This is a simple response to: {question}"
    
    # Yield initial event
    yield f"data: {json.dumps({'start': True})}\n\n"
    
    # Simulate streaming by yielding chunks
    words = answer.split()
    for i, word in enumerate(words):
        chunk = word + (" " if i < len(words) - 1 else "")
        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        await asyncio.sleep(0.1)
    
    yield f"data: {json.dumps({'done': True})}\n\n"

@app.get("/stream/{question}")
async def stream_answer(question: str):
    """Stream response via SSE"""
    return StreamingResponse(
        generate_response(question),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)