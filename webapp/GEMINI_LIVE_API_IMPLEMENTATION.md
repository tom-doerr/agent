# Gemini Live API Implementation

This document describes the implementation of real-time audio streaming using Google's Gemini Live API.

## Overview

The Gemini Live API enables real-time, bidirectional audio streaming with the Gemini 2.0 Flash model. This implementation provides:

- WebSocket-based real-time audio streaming
- Live transcription and response generation
- Browser-based audio recording with device selection
- React frontend with live feedback

## Architecture

### Backend Components

1. **`gemini_live_handler.py`**
   - Manages WebSocket connection to Gemini Live API
   - Handles audio format conversion (WebM to PCM 16kHz)
   - Processes API responses and extracts text

2. **`live_websocket.py`**
   - FastAPI WebSocket endpoint (`/ws/audio-live`)
   - Manages client connections
   - Routes audio between browser and Gemini API

3. **`main.py`**
   - Added `/audio-stream` endpoint for batch audio processing
   - Added `/ws/audio-live` WebSocket endpoint for real-time streaming

### Frontend Components

1. **`LiveAudioRecorder.js`**
   - Real-time audio recording component
   - WebSocket client for streaming audio chunks
   - Live transcription display
   - Microphone device selection

2. **`App.js`**
   - Integrated both batch and live audio recording options
   - Model selection for audio processing

## Key Features

### Real-Time Streaming
- Audio is streamed in 100ms chunks for low latency
- Uses WebSocket for bidirectional communication
- Supports continuous conversation flow

### Audio Format
- Input: WebM/Opus from browser MediaRecorder
- Converted to: PCM 16kHz, 16-bit for Gemini API
- Uses `librosa` for audio format conversion

### API Configuration
- Model: `gemini-2.0-flash-exp` (experimental model with Live API support)
- WebSocket URL: `wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent`
- Authentication via API key in URL parameter

## Usage

### Environment Setup
```bash
# Set in .env file
GEMINI_API_KEY=your_api_key_here
```

### Starting the Application
```bash
docker compose up -d
```

### Using Live Audio Streaming
1. Navigate to http://localhost:3000
2. Select a microphone from the dropdown
3. Click "Start Live Stream" to begin real-time audio streaming
4. Speak into the microphone
5. View real-time transcription and responses
6. Click "Stop Live Stream" to end the session

## Message Format

### Setup Message
```json
{
  "setup": {
    "model": "models/gemini-2.0-flash-exp",
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
```

### Audio Chunk Message
```json
{
  "realtimeInput": {
    "mediaChunks": [{
      "data": "base64_encoded_pcm_audio",
      "mimeType": "audio/pcm;rate=16000"
    }]
  }
}
```

### Response Format
```json
{
  "serverContent": {
    "modelTurn": {
      "parts": [{
        "text": "Response text from model"
      }]
    },
    "turnComplete": true
  }
}
```

## Testing

### Direct API Test
```bash
python test_gemini_direct.py  # Tests text input
python test_gemini_audio.py   # Tests audio streaming
```

### WebSocket Test
```bash
python test_gemini_live.py    # Tests full WebSocket flow
```

## Limitations

1. Maximum 15 minutes for audio sessions
2. 3 concurrent sessions per API key
3. 4M tokens per minute rate limit
4. Currently in experimental/preview phase

## Future Enhancements

1. Add support for voice output (audio responses)
2. Implement interruption handling
3. Add support for video streaming
4. Integrate function calling and tools
5. Add session persistence and history