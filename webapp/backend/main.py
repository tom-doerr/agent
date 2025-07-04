from fastapi import FastAPI, WebSocket, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import dspy
from typing import AsyncGenerator, Optional
import json
import asyncio
import os
import base64
from contextlib import asynccontextmanager
from audio_handler import transcribe_audio
from gemini_handler import stream_gemini_response, get_gemini_response, transcribe_with_gemini

# Global flag for mock mode
MOCK_MODE = True

# Available models
TEXT_MODELS = {
    "gemini-flash": "gemini/gemini-2.0-flash-exp",
    "gemini-flash-thinking": "gemini/gemini-2.0-flash-thinking-exp",
    "gemini-pro": "gemini/gemini-1.5-pro",
    "deepseek-r1": "ollama/deepseek-r1:8b",
    "mock": "mock"
}

AUDIO_MODELS = {
    "gemini-flash": "gemini/gemini-2.0-flash-exp",
    "gemini-pro": "gemini/gemini-1.5-pro",
    "mock": "mock"
}

# Initialize DSPy
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup DSPy on startup
    global MOCK_MODE
    import os
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        lm = dspy.LM("ollama/deepseek-r1:8b", base_url=ollama_url)
        dspy.configure(lm=lm)
        MOCK_MODE = False
    except Exception as e:
        print(f"Warning: Could not connect to Ollama: {e}")
        MOCK_MODE = True
    yield

app = FastAPI(lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple DSPy signature
class Question(dspy.Signature):
    """Answer questions helpfully."""
    question = dspy.InputField()
    answer = dspy.OutputField()

# Create predictor
qa_predictor = dspy.Predict(Question)

@app.get("/")
async def root():
    return {
        "message": "DSPy Streaming API",
        "text_models": list(TEXT_MODELS.keys()),
        "audio_models": list(AUDIO_MODELS.keys()),
        "config": {
            "mock_mode": MOCK_MODE,
            "available_endpoints": ["/stream", "/transcribe", "/ws", "/models"]
        }
    }

@app.get("/models")
async def get_models():
    """Get available models"""
    return {
        "text_models": TEXT_MODELS,
        "audio_models": AUDIO_MODELS
    }

@app.post("/audio-stream")
async def audio_stream_endpoint(
    audio: UploadFile = File(...),
    model: str = Query("gemini-flash", description="Model to use for audio processing")
):
    """Handle audio input using Gemini Live API"""
    from gemini_live_handler import convert_audio_format, stream_audio_to_gemini
    
    content = await audio.read()
    api_key = os.getenv("GEMINI_API_KEY")
    
    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive", 
        "X-Accel-Buffering": "no",
        "Access-Control-Allow-Origin": "*",
    }
    
    async def generate_audio_response():
        yield f"data: {json.dumps({'start': True, 'model': model})}\\n\\n"
        
        if not api_key or model == "mock":
            # Mock response
            response = f"I received your audio input ({len(content)/1024:.1f}KB). To use Gemini Live API, set GEMINI_API_KEY."
            words = response.split()
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                yield f"data: {json.dumps({'chunk': chunk})}\\n\\n"
                await asyncio.sleep(0.05)
        else:
            try:
                # Convert audio to PCM format
                pcm_audio = convert_audio_format(content, "webm")
                
                # Create async generator for audio
                async def audio_generator():
                    # Split audio into chunks for streaming
                    chunk_size = 16000  # 1 second of audio at 16kHz
                    for i in range(0, len(pcm_audio), chunk_size):
                        yield pcm_audio[i:i+chunk_size]
                        await asyncio.sleep(0.1)  # Small delay between chunks
                
                # Stream to Gemini Live API
                async for response in stream_audio_to_gemini(
                    audio_generator(),
                    api_key,
                    model="gemini-2.0-flash"
                ):
                    if response["type"] == "text":
                        # Stream the text response
                        text = response["content"]
                        words = text.split()
                        for word in words:
                            yield f"data: {json.dumps({'chunk': word + ' '})}\\n\\n"
                            await asyncio.sleep(0.01)
                    elif response["type"] == "turn_complete":
                        # Model finished responding
                        yield f"data: {json.dumps({'turn_complete': True})}\\n\\n"
                        
            except Exception as e:
                error_msg = f"Error processing audio with Gemini Live API: {str(e)}"
                yield f"data: {json.dumps({'error': error_msg})}\\n\\n"
        
        yield f"data: {json.dumps({'done': True})}\\n\\n"
    
    return StreamingResponse(
        generate_audio_response(),
        media_type="text/event-stream",
        headers=headers
    )

async def generate_response(question: str, model: str = "gemini-flash") -> AsyncGenerator[str, None]:
    """Generate streaming response"""
    import time
    start_time = time.time()
    total_tokens = 0
    
    try:
        # Yield initial event with model info
        yield f"data: {json.dumps({'start': True, 'model': model})}\n\n"
        
        if model == "mock" or (model == "deepseek-r1" and MOCK_MODE):
            # Mock response
            answer = f"This is a mock response to: {question}. Using model: {model}"
            words = answer.split()
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                total_tokens += 1
                elapsed = time.time() - start_time
                tokens_per_sec = total_tokens / elapsed if elapsed > 0 else 0
                yield f"data: {json.dumps({'chunk': chunk, 'tokens': total_tokens, 'tokens_per_sec': round(tokens_per_sec, 2)})}\n\n"
                await asyncio.sleep(0.01)
        elif model.startswith("gemini"):
            # Check if API key is available
            if not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
                yield f"data: {json.dumps({'error': 'Gemini API key not configured. Please set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.'})}\\n\\n"
                return
            
            # Use Gemini streaming
            model_path = TEXT_MODELS.get(model, "gemini/gemini-2.0-flash-exp")
            try:
                async for event in stream_gemini_response(question, model_path):
                    if "chunk" in event:
                        total_tokens += len(event.split())  # Approximate token count
                        elapsed = time.time() - start_time
                        tokens_per_sec = total_tokens / elapsed if elapsed > 0 else 0
                        data = json.loads(event.split("data: ")[1])
                        data['tokens'] = total_tokens
                        data['tokens_per_sec'] = round(tokens_per_sec, 2)
                        yield f"data: {json.dumps(data)}\n\n"
                    else:
                        yield event
            except Exception as e:
                if "API_KEY_INVALID" in str(e) or "API key not valid" in str(e):
                    yield f"data: {json.dumps({'error': 'Invalid Gemini API key. Please check your GEMINI_API_KEY or GOOGLE_API_KEY.'})}\\n\\n"
                else:
                    yield f"data: {json.dumps({'error': f'Gemini API error: {str(e)}'})}\\n\\n"
        else:
            # Use DSPy with Ollama
            try:
                result = qa_predictor(question=question)
                answer = result.answer
            except Exception as e:
                answer = f"Error processing question: {str(e)}"
            
            words = answer.split()
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                total_tokens += 1
                elapsed = time.time() - start_time
                tokens_per_sec = total_tokens / elapsed if elapsed > 0 else 0
                yield f"data: {json.dumps({'chunk': chunk, 'tokens': total_tokens, 'tokens_per_sec': round(tokens_per_sec, 2)})}\n\n"
                await asyncio.sleep(0.01)
        
        # Final stats
        elapsed = time.time() - start_time
        yield f"data: {json.dumps({'done': True, 'total_tokens': total_tokens, 'total_time': round(elapsed, 2), 'avg_tokens_per_sec': round(total_tokens/elapsed, 2) if elapsed > 0 else 0})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

@app.get("/stream/{question}")
async def stream_answer(
    question: str,
    model: str = Query("gemini-flash", description="Model to use for text generation")
):
    """Stream response via SSE"""
    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
        "Access-Control-Allow-Origin": "*",
    }
    return StreamingResponse(
        generate_response(question, model),
        media_type="text/event-stream",
        headers=headers
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time streaming"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            request = json.loads(data)
            
            if request.get("type") == "question":
                question = request.get("question", "")
                
                # Process with DSPy
                result = qa_predictor(question=question)
                answer = result.answer
                
                # Stream response word by word
                words = answer.split()
                for i, word in enumerate(words):
                    chunk = word + (" " if i < len(words) - 1 else "")
                    await websocket.send_json({
                        "type": "chunk",
                        "content": chunk
                    })
                    await asyncio.sleep(0.05)
                
                await websocket.send_json({
                    "type": "complete",
                    "content": answer
                })
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    finally:
        await websocket.close()

@app.websocket("/ws/audio-live")
async def websocket_audio_live(websocket: WebSocket):
    """WebSocket endpoint for real-time audio streaming with Gemini Live API"""
    from live_websocket import websocket_audio_endpoint
    await websocket_audio_endpoint(websocket)