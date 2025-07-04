# Audio Features Documentation

## Overview
The DSPy webapp supports direct audio input for questions using the Web Audio API and audio transcription capabilities.

## Features
- **Web Audio Recording**: Browser-based audio recording using MediaRecorder API
- **Audio Transcription**: Backend service for converting audio to text
- **Seamless Integration**: Transcribed text automatically populates the question field

## Architecture

### Frontend (React)
- `AudioRecorder.js`: Component handling audio recording
- Uses Web Audio API and MediaRecorder
- Sends audio as WebM format to backend

### Backend (FastAPI)
- `/transcribe` endpoint: Handles audio file uploads
- `audio_handler.py`: Processes audio files
- Currently uses mock transcription (ready for Gemini 2.5 Flash integration)

## Usage

### Basic Setup
```bash
# Run with Docker Compose
docker compose up

# Run with audio-specific configuration
docker compose -f docker-compose.yml -f docker-compose.audio.yml up
```

### Testing Audio Features
```bash
# Run audio unit tests
docker compose run --rm backend pytest test_audio_handler.py -v

# Run audio integration tests
docker compose run --rm frontend npm test AudioRecorder.test.js

# Run audio e2e tests
docker compose --profile audio-test up audio-integration-test
```

## Configuration

### Environment Variables
- `REACT_APP_ENABLE_AUDIO`: Enable/disable audio features (frontend)
- `LITELLM_LOG`: Set to DEBUG for audio transcription debugging
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to Google Cloud credentials (if using real Speech-to-Text)

### Gemini 2.5 Flash Integration
To enable real transcription with Gemini 2.5 Flash:

1. Set up API credentials
2. Update `audio_handler.py` to use litellm:
```python
response = litellm.completion(
    model="gemini/gemini-2.5-flash",
    messages=[{
        "role": "user",
        "content": f"Transcribe this audio: {audio_base64}"
    }]
)
```

## Browser Requirements
- Modern browser with Web Audio API support
- Microphone permissions must be granted
- HTTPS connection (or localhost) required

## Security Considerations
- Audio files are temporarily stored and immediately deleted after processing
- No audio data is permanently stored
- Microphone permissions are requested only when needed

## Troubleshooting

### Common Issues
1. **Microphone Access Denied**: Check browser permissions
2. **No Audio Input**: Verify microphone is connected and working
3. **Transcription Fails**: Check backend logs and API credentials

### Debug Mode
Enable debug logging:
```bash
docker compose -f docker-compose.yml -f docker-compose.audio.yml up
```

## Future Enhancements
- Real-time streaming transcription
- Multiple language support
- Audio quality indicators
- Voice activity detection
- Noise cancellation