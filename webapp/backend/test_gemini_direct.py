#!/usr/bin/env python3
"""Direct test of Gemini Live API WebSocket connection"""
import asyncio
import websockets
import json
import os
import base64

async def test_gemini_direct():
    """Test direct connection to Gemini Live API"""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not set")
        return
        
    url = f"wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key={api_key}"
    
    try:
        print(f"Connecting to Gemini Live API...")
        
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
                            "text": "You are a helpful assistant. Please respond to audio input with text."
                        }]
                    }
                }
            }
            
            await websocket.send(json.dumps(setup_message))
            print("Sent setup message")
            
            # Wait for setup response
            response = await websocket.recv()
            print(f"Setup response: {response}")
            
            # Send a simple text message to test
            test_message = {
                "client_content": {
                    "turns": [{
                        "role": "user",
                        "parts": [{
                            "text": "Hello, can you hear me? Please respond with 'Yes, I can hear you!'"
                        }]
                    }],
                    "turn_complete": True
                }
            }
            
            await websocket.send(json.dumps(test_message))
            print("Sent test message")
            
            # Listen for responses
            for i in range(5):
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    print(f"Response {i+1}: {response}")
                    
                    # Parse and check for text response
                    data = json.loads(response)
                    if "serverContent" in data:
                        if "parts" in data["serverContent"]:
                            for part in data["serverContent"]["parts"]:
                                if "text" in part:
                                    print(f"Text response: {part['text']}")
                                    
                except asyncio.TimeoutError:
                    print("Timeout waiting for response")
                    break
                    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gemini_direct())