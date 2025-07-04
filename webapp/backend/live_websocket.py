"""WebSocket endpoint for real-time audio streaming to Gemini Live API"""
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
import os
import logging
from gemini_live_handler import GeminiLiveSession, convert_audio_format

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LiveAudioProcessor:
    """Handles real-time audio streaming via WebSocket"""
    
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.gemini_session = None
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.is_active = False
        
    async def process(self):
        """Main processing loop"""
        await self.websocket.accept()
        
        try:
            # Initialize Gemini Live session if API key available
            if self.api_key:
                try:
                    logger.info(f"Initializing Gemini Live session with API key: {self.api_key[:10]}...")
                    self.gemini_session = GeminiLiveSession(self.api_key)
                    await self.gemini_session.connect()
                    self.is_active = True
                    logger.info("Gemini Live session connected successfully")
                    
                    # Start response handler in background
                    response_task = asyncio.create_task(self._handle_responses())
                except Exception as e:
                    logger.error(f"Failed to connect to Gemini Live API: {e}")
                    await self.websocket.send_json({
                        "type": "error",
                        "message": f"Failed to connect to Gemini Live API: {str(e)}"
                    })
                    return
            else:
                logger.error("GEMINI_API_KEY not configured")
                await self.websocket.send_json({
                    "type": "error",
                    "message": "GEMINI_API_KEY not configured"
                })
            
            # Handle incoming messages
            while True:
                data = await self.websocket.receive_json()
                message_type = data.get("type")
                
                if message_type == "audio_chunk":
                    # Process audio chunk
                    audio_data = data.get("audio")
                    if audio_data and self.gemini_session:
                        # Convert base64 to bytes
                        import base64
                        audio_bytes = base64.b64decode(audio_data)
                        logger.info(f"Received audio chunk of size: {len(audio_bytes)} bytes")
                        
                        # Send to Gemini
                        await self.gemini_session.send_audio_chunk(audio_bytes)
                        
                elif message_type == "audio_complete":
                    # Audio recording completed
                    await self.websocket.send_json({
                        "type": "processing_complete"
                    })
                    
                elif message_type == "stop":
                    break
                    
        except WebSocketDisconnect:
            logger.info("WebSocket disconnected")
        except Exception as e:
            logger.error(f"Error in WebSocket handler: {e}")
            await self.websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        finally:
            self.is_active = False
            if self.gemini_session:
                await self.gemini_session.close()
    
    async def _handle_responses(self):
        """Handle responses from Gemini Live API"""
        if not self.gemini_session:
            return
            
        try:
            async for response in self.gemini_session.receive_responses():
                if response["type"] == "text":
                    await self.websocket.send_json({
                        "type": "text",
                        "content": response["content"],
                        "is_complete": response.get("is_complete", False)
                    })
                elif response["type"] == "turn_complete":
                    await self.websocket.send_json({
                        "type": "turn_complete"
                    })
        except Exception as e:
            logger.error(f"Error handling responses: {e}")


async def websocket_audio_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time audio streaming"""
    processor = LiveAudioProcessor(websocket)
    await processor.process()