"""Gemini Live API handler for real-time audio streaming"""
import asyncio
import websockets
import json
import base64
import os
from typing import AsyncGenerator, Optional, Dict, Any
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class GeminiLiveSession:
    """Manages a WebSocket connection to Gemini Live API"""
    
    WEBSOCKET_URL = "wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent"
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp"):
        self.api_key = api_key
        self.model = model
        self.websocket = None
        self.session_active = False
        
    async def connect(self):
        """Establish WebSocket connection with authentication"""
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            # Construct URL with API key
            url = f"{self.WEBSOCKET_URL}?key={self.api_key}"
            logger.info(f"Connecting to Gemini Live API at: {self.WEBSOCKET_URL[:50]}...")
            
            # Connect to WebSocket (headers handled via URL parameter)
            self.websocket = await websockets.connect(url)
            self.session_active = True
            logger.info("WebSocket connection established")
            
            # Send initial setup message for Gemini Live API
            setup_message = {
                "setup": {
                    "model": f"models/{self.model}",
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 1000,
                        "responseModalities": ["TEXT"]
                    },
                    "systemInstruction": {
                        "parts": [{
                            "text": "You are a helpful assistant that processes audio input and provides text responses."
                        }]
                    }
                }
            }
            
            await self.websocket.send(json.dumps(setup_message))
            logger.info(f"Connected to Gemini Live API with model: {self.model}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Gemini Live API: {e}")
            raise
    
    async def send_audio_chunk(self, audio_data: bytes, mime_type: str = "audio/pcm;rate=16000"):
        """Send audio chunk to the API"""
        if not self.session_active:
            raise Exception("Session not active")
        
        # Encode audio data to base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Use the correct message format for Gemini Live API
        message = {
            "realtimeInput": {
                "mediaChunks": [{
                    "data": audio_base64,
                    "mimeType": mime_type
                }]
            }
        }
        
        await self.websocket.send(json.dumps(message))
    
    async def receive_responses(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Receive and yield responses from the API"""
        if not self.session_active:
            return
        
        try:
            while self.session_active:
                message = await self.websocket.recv()
                data = json.loads(message)
                
                # Handle different message types
                if "serverContent" in data:
                    content = data["serverContent"]
                    
                    # Check for model turn with parts
                    if "modelTurn" in content and "parts" in content["modelTurn"]:
                        for part in content["modelTurn"]["parts"]:
                            if "text" in part:
                                yield {
                                    "type": "text",
                                    "content": part["text"],
                                    "is_complete": False
                                }
                    
                    # Check for turn complete
                    if "turnComplete" in content and content["turnComplete"]:
                        yield {
                            "type": "turn_complete"
                        }
                
                elif "toolCall" in data:
                    # Handle tool calls if needed
                    yield {
                        "type": "tool_call",
                        "content": data["toolCall"]
                    }
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
            self.session_active = False
        except Exception as e:
            logger.error(f"Error receiving responses: {e}")
            self.session_active = False
    
    async def close(self):
        """Close the WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            self.session_active = False
            logger.info("Closed Gemini Live API connection")


async def stream_audio_to_gemini(
    audio_stream: AsyncGenerator[bytes, None],
    api_key: str,
    model: str = "gemini-2.0-flash-exp"
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Stream audio to Gemini Live API and yield text responses
    
    Args:
        audio_stream: Async generator yielding audio chunks
        api_key: Gemini API key
        model: Model to use (default: gemini-2.0-flash)
        
    Yields:
        Dict with response data
    """
    session = GeminiLiveSession(api_key, model)
    
    try:
        # Connect to API
        await session.connect()
        
        # Create tasks for sending and receiving
        async def send_audio():
            async for chunk in audio_stream:
                await session.send_audio_chunk(chunk)
        
        # Start sending audio in background
        send_task = asyncio.create_task(send_audio())
        
        # Yield responses as they come
        async for response in session.receive_responses():
            yield response
            
        # Wait for sending to complete
        await send_task
        
    finally:
        await session.close()


def convert_audio_format(audio_data: bytes, input_format: str = "webm") -> bytes:
    """
    Convert audio to PCM format required by Gemini
    
    Args:
        audio_data: Raw audio data
        input_format: Input format (webm, mp3, etc.)
        
    Returns:
        PCM audio data at 16kHz
    """
    import io
    import librosa
    import soundfile as sf
    
    # Load audio using librosa
    audio_io = io.BytesIO(audio_data)
    y, sr = librosa.load(audio_io, sr=16000, mono=True)
    
    # Convert to PCM
    buffer = io.BytesIO()
    sf.write(buffer, y, 16000, format="RAW", subtype="PCM_16")
    buffer.seek(0)
    
    return buffer.read()


# Example usage for testing
async def test_live_api():
    """Test the Live API with a sample audio file"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not set")
        return
    
    # Simulate audio chunks
    async def mock_audio_stream():
        # In real usage, this would be actual audio chunks
        for i in range(5):
            yield b"mock_audio_chunk_" + str(i).encode()
            await asyncio.sleep(0.1)
    
    async for response in stream_audio_to_gemini(mock_audio_stream(), api_key):
        print(f"Response: {response}")


if __name__ == "__main__":
    asyncio.run(test_live_api())