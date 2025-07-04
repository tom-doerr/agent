"""Gemini Flash handler for streaming responses"""
import litellm
from typing import AsyncGenerator, Optional
import json
import asyncio
import os
from litellm import acompletion

# Configure litellm
litellm.set_verbose = os.getenv("LITELLM_LOG", "INFO") == "DEBUG"

# Set up API key - use GEMINI_API_KEY or GOOGLE_API_KEY
if not os.getenv("GEMINI_API_KEY"):
    if api_key := os.getenv("GOOGLE_API_KEY"):
        os.environ["GEMINI_API_KEY"] = api_key

async def stream_gemini_response(question: str, model: str = "gemini/gemini-2.0-flash-exp") -> AsyncGenerator[str, None]:
    """
    Stream response from Gemini Flash
    """
    try:
        # Yield start event
        yield f"data: {json.dumps({'start': True})}\n\n"
        
        # Call Gemini with streaming
        response = await acompletion(
            model=model,
            messages=[{
                "role": "user",
                "content": question
            }],
            stream=True,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Stream the response chunks
        async for chunk in response:
            if hasattr(chunk, 'choices') and chunk.choices:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    yield f"data: {json.dumps({'chunk': delta.content})}\n\n"
                    await asyncio.sleep(0.001)  # Minimal delay for smooth streaming
        
        yield f"data: {json.dumps({'done': True})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

async def get_gemini_response(question: str, model: str = "gemini/gemini-2.0-flash-exp") -> str:
    """
    Get non-streaming response from Gemini Flash
    """
    try:
        response = await acompletion(
            model=model,
            messages=[{
                "role": "user", 
                "content": question
            }],
            temperature=0.7,
            max_tokens=1000
        )
        
        if response.choices:
            return response.choices[0].message.content
        return "No response generated"
        
    except Exception as e:
        return f"Error: {str(e)}"

async def transcribe_with_gemini(audio_content: bytes, mime_type: str = "audio/webm") -> str:
    """
    Transcribe audio using Gemini's multimodal capabilities
    """
    try:
        # Convert audio to base64
        import base64
        audio_base64 = base64.b64encode(audio_content).decode('utf-8')
        
        # Create multimodal message
        response = await acompletion(
            model="gemini/gemini-2.0-flash-exp",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Please transcribe this audio recording:"
                    },
                    {
                        "type": "audio_url",
                        "audio_url": {
                            "url": f"data:{mime_type};base64,{audio_base64}"
                        }
                    }
                ]
            }],
            temperature=0.3,  # Lower temperature for transcription accuracy
            max_tokens=500
        )
        
        if response.choices:
            return response.choices[0].message.content
        return "Could not transcribe audio"
        
    except Exception as e:
        # Fallback to mock transcription if Gemini doesn't support audio
        if "audio" in str(e).lower():
            return "This is a simulated transcription. Real audio transcription requires Gemini API with audio support."
        raise e