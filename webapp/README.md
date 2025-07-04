# DSPy Streaming Webapp

A React + FastAPI application demonstrating real-time streaming responses from DSPy with audio input support.

## Features
- Real-time streaming responses using Server-Sent Events (SSE)
- Audio recording and transcription support
- WebSocket support for bidirectional communication
- Docker Compose setup for easy deployment
- Comprehensive test suite (unit, integration, e2e)

## Quick Start

```bash
# Start all services
docker compose up

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Audio Features
The application supports direct audio input:
1. Click the microphone button to start recording
2. Speak your question
3. Click stop to end recording
4. Audio is transcribed and populated in the question field
5. Submit to get streaming response

See [docs/audio-features.md](docs/audio-features.md) for detailed audio documentation.

## Architecture

### Frontend (React)
- `App.js`: Main component with SSE streaming
- `AudioRecorder.js`: Audio recording component
- Modern, responsive UI with real-time updates

### Backend (FastAPI)
- `main.py`: API endpoints for streaming and transcription
- `audio_handler.py`: Audio processing logic
- Mock mode for testing without Ollama

## Development

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Local Development
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm start
```

### Running Tests

```bash
# All tests in Docker
make test-all

# Specific test suites
docker compose run --rm backend pytest -v
docker compose run --rm frontend npm test
docker compose --profile e2e up e2e-tests

# Audio-specific tests
docker compose --profile tests up audio-tests
```

## Environment Variables

### Backend
- `OLLAMA_BASE_URL`: Ollama server URL (default: http://localhost:11434)
- `LITELLM_LOG`: Logging level for audio transcription

### Frontend
- `REACT_APP_API_URL`: Backend API URL (default: http://localhost:8000)
- `REACT_APP_ENABLE_AUDIO`: Enable audio features (default: true)

## API Endpoints

- `GET /`: Health check
- `GET /stream/{question}`: SSE streaming endpoint
- `POST /transcribe`: Audio transcription endpoint
- `WS /ws`: WebSocket endpoint

## Deployment

### Production Build
```bash
# Build production images
docker compose -f docker-compose.yml -f docker-compose.prod.yml build

# Run in production mode
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Troubleshooting

### Common Issues
1. **Streaming timeout**: Check OLLAMA_BASE_URL configuration
2. **Audio not working**: Ensure microphone permissions are granted
3. **CORS errors**: Verify frontend/backend URLs match configuration

### Debug Mode
```bash
# Run with debug logging
LITELLM_LOG=DEBUG docker compose up
```

## Contributing
1. Create feature branch
2. Add tests for new features
3. Ensure all tests pass
4. Submit pull request

## License
MIT