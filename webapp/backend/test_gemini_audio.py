#!/usr/bin/env python3
"""Test sending audio to Gemini Live API"""
import asyncio
import websockets
import json
import os
import base64
import numpy as np
import io
import soundfile as sf

async def test_audio_streaming():
    """Test audio streaming to Gemini Live API"""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not set")
        return
        
    url = f"wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key={api_key}"
    
    # Generate test audio: "Hello" spoken pattern (simplified)
    sample_rate = 16000
    duration = 2.0
    
    # Create a simple audio pattern that resembles speech
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Simulate speech with varying frequencies and amplitudes
    audio_signal = np.zeros_like(t)
    
    # "Hello" pattern (very simplified)
    # H sound (0-0.3s)
    audio_signal[0:int(0.3*sample_rate)] = 0.3 * np.sin(2 * np.pi * 300 * t[0:int(0.3*sample_rate)])
    # E sound (0.3-0.6s)  
    audio_signal[int(0.3*sample_rate):int(0.6*sample_rate)] = 0.5 * np.sin(2 * np.pi * 400 * t[0:int(0.3*sample_rate)])
    # L sound (0.6-0.9s)
    audio_signal[int(0.6*sample_rate):int(0.9*sample_rate)] = 0.4 * np.sin(2 * np.pi * 250 * t[0:int(0.3*sample_rate)])
    # L sound (0.9-1.2s)
    audio_signal[int(0.9*sample_rate):int(1.2*sample_rate)] = 0.4 * np.sin(2 * np.pi * 250 * t[0:int(0.3*sample_rate)])
    # O sound (1.2-1.5s)
    audio_signal[int(1.2*sample_rate):int(1.5*sample_rate)] = 0.5 * np.sin(2 * np.pi * 350 * t[0:int(0.3*sample_rate)])
    
    # Add some noise to make it more realistic
    noise = np.random.normal(0, 0.02, len(audio_signal))
    audio_signal += noise
    
    # Convert to 16-bit PCM
    audio_signal = np.clip(audio_signal, -1, 1)
    audio_signal = (audio_signal * 32767).astype(np.int16)
    
    try:
        print("Connecting to Gemini Live API...")
        
        async with websockets.connect(url) as websocket:
            print("Connected successfully!")
            
            # Send setup message
            setup_message = {
                "setup": {
                    "model": "models/gemini-2.0-flash-exp",
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 1000,
                        "responseModalities": ["TEXT"]
                    },
                    "systemInstruction": {
                        "parts": [{
                            "text": "You are a helpful assistant. Listen to the audio and transcribe what you hear, then respond appropriately."
                        }]
                    }
                }
            }
            
            await websocket.send(json.dumps(setup_message))
            print("Sent setup message")
            
            # Wait for setup response
            response = await websocket.recv()
            print(f"Setup response: {response}")
            
            # Send audio in chunks via realtimeInput
            chunk_size = 16000  # 1 second chunks
            for i in range(0, len(audio_signal), chunk_size):
                chunk = audio_signal[i:i+chunk_size]
                
                # Convert to bytes
                chunk_bytes = chunk.tobytes()
                audio_base64 = base64.b64encode(chunk_bytes).decode('utf-8')
                
                audio_message = {
                    "realtimeInput": {
                        "mediaChunks": [{
                            "data": audio_base64,
                            "mimeType": "audio/pcm;rate=16000"
                        }]
                    }
                }
                
                await websocket.send(json.dumps(audio_message))
                print(f"Sent audio chunk {i//chunk_size + 1}")
                await asyncio.sleep(0.1)
            
            # The API will detect end of audio automatically
            print("Finished sending audio chunks")
            
            # Listen for responses
            full_response = ""
            for i in range(10):
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)
                    
                    if "serverContent" in data:
                        content = data["serverContent"]
                        if "modelTurn" in content and "parts" in content["modelTurn"]:
                            for part in content["modelTurn"]["parts"]:
                                if "text" in part:
                                    text = part["text"]
                                    full_response += text
                                    print(f"Response text: {text}")
                        
                        if "turnComplete" in content and content["turnComplete"]:
                            print("Turn complete")
                            break
                            
                except asyncio.TimeoutError:
                    print("Timeout waiting for response")
                    break
            
            print(f"\nFull response: {full_response}")
                    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_audio_streaming())