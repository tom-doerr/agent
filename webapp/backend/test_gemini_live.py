#!/usr/bin/env python3
"""Test script for Gemini Live API implementation"""
import asyncio
import json
import websockets
import base64
import io
import numpy as np
import soundfile as sf

async def test_gemini_live():
    """Test the Gemini Live API via WebSocket"""
    
    # Generate a test audio signal (1 second of sine wave at 440Hz)
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    frequency = 440  # A4 note
    audio_signal = np.sin(2 * np.pi * frequency * t) * 0.5
    
    # Convert to PCM format
    buffer = io.BytesIO()
    sf.write(buffer, audio_signal, sample_rate, format='RAW', subtype='PCM_16')
    buffer.seek(0)
    pcm_audio = buffer.read()
    
    # Connect to our WebSocket endpoint
    uri = "ws://localhost:8000/ws/audio-live"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket")
            
            # Send audio in chunks
            chunk_size = 16000  # 1 second chunks
            for i in range(0, len(pcm_audio), chunk_size):
                chunk = pcm_audio[i:i+chunk_size]
                audio_base64 = base64.b64encode(chunk).decode('utf-8')
                
                message = {
                    "type": "audio_chunk",
                    "audio": audio_base64
                }
                
                await websocket.send(json.dumps(message))
                print(f"Sent audio chunk {i//chunk_size + 1}")
                await asyncio.sleep(0.1)
            
            # Send completion message
            await websocket.send(json.dumps({"type": "audio_complete"}))
            print("Sent completion message")
            
            # Listen for responses
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)
                    
                    if data["type"] == "text":
                        print(f"Received text: {data['content']}")
                    elif data["type"] == "turn_complete":
                        print("Turn complete")
                        break
                    elif data["type"] == "error":
                        print(f"Error: {data['message']}")
                        break
                    elif data["type"] == "processing_complete":
                        print("Processing complete")
                        
                except asyncio.TimeoutError:
                    print("Timeout waiting for response")
                    break
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_gemini_live())