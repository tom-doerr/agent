import pytest
import json
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from main import app, generate_response, TEXT_MODELS, AUDIO_MODELS

class TestStreamingEndpoints:
    """Test streaming functionality"""
    
    def test_get_models_endpoint(self):
        """Test /models endpoint returns available models"""
        client = TestClient(app)
        response = client.get("/models")
        
        assert response.status_code == 200
        data = response.json()
        assert "text_models" in data
        assert "audio_models" in data
        assert "gemini-flash" in data["text_models"]
        assert "gemini-flash" in data["audio_models"]
    
    def test_root_endpoint_with_config(self):
        """Test root endpoint returns full configuration"""
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "text_models" in data
        assert "audio_models" in data
        assert "config" in data
        assert "mock_mode" in data["config"]
        assert "available_endpoints" in data["config"]
    
    def test_stream_with_model_parameter(self):
        """Test streaming with model parameter"""
        client = TestClient(app)
        
        with client as c:
            # Test with mock model
            with c.stream("GET", "/stream/Hello?model=mock") as response:
                assert response.status_code == 200
                assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
                
                events = []
                for line in response.iter_lines():
                    if line.startswith(b"data: "):
                        events.append(json.loads(line[6:]))
                
                # Should have start event with model info
                assert any(e.get("start") and e.get("model") == "mock" for e in events)
                # Should have chunks with token stats
                chunks = [e for e in events if "chunk" in e]
                assert len(chunks) > 0
                assert all("tokens" in c and "tokens_per_sec" in c for c in chunks)
                # Should have done event with final stats
                done_events = [e for e in events if e.get("done")]
                assert len(done_events) == 1
                assert "total_tokens" in done_events[0]
                assert "total_time" in done_events[0]
                assert "avg_tokens_per_sec" in done_events[0]

@pytest.mark.asyncio
class TestStreamingLogic:
    """Test streaming generation logic"""
    
    async def test_generate_response_mock_model(self):
        """Test generate_response with mock model"""
        events = []
        async for event in generate_response("Test question", "mock"):
            events.append(event)
        
        # Parse events
        parsed_events = []
        for event in events:
            if event.startswith("data: "):
                parsed_events.append(json.loads(event[6:].strip()))
        
        # Verify event structure
        assert parsed_events[0].get("start") == True
        assert parsed_events[0].get("model") == "mock"
        
        # Check chunks have stats
        chunks = [e for e in parsed_events if "chunk" in e]
        assert len(chunks) > 0
        for chunk in chunks:
            assert "tokens" in chunk
            assert "tokens_per_sec" in chunk
            assert chunk["tokens_per_sec"] >= 0
        
        # Check final stats
        done_event = next(e for e in parsed_events if e.get("done"))
        assert done_event["total_tokens"] > 0
        assert done_event["total_time"] > 0
        assert done_event["avg_tokens_per_sec"] > 0
    
    @patch('main.stream_gemini_response')
    async def test_generate_response_gemini_model(self, mock_stream):
        """Test generate_response with Gemini model"""
        # Mock Gemini streaming
        async def mock_gemini_stream(*args):
            yield 'data: {"start": true}\n\n'
            yield 'data: {"chunk": "Hello "}\n\n'
            yield 'data: {"chunk": "world"}\n\n'
            yield 'data: {"done": true}\n\n'
        
        mock_stream.return_value = mock_gemini_stream()
        
        events = []
        async for event in generate_response("Test", "gemini-flash"):
            events.append(event)
        
        # Should have called Gemini handler
        mock_stream.assert_called_once()
        assert len(events) > 0
    
    async def test_token_counting_accuracy(self):
        """Test token counting and timing accuracy"""
        start_time = asyncio.get_event_loop().time()
        
        events = []
        async for event in generate_response("Count tokens", "mock"):
            events.append(event)
        
        end_time = asyncio.get_event_loop().time()
        elapsed = end_time - start_time
        
        # Parse final stats
        parsed_events = [json.loads(e[6:].strip()) for e in events if e.startswith("data: ")]
        done_event = next(e for e in parsed_events if e.get("done"))
        
        # Verify timing is reasonable
        assert abs(done_event["total_time"] - elapsed) < 0.5  # Within 0.5 seconds
        
        # Verify token count matches actual tokens
        chunks = [e for e in parsed_events if "chunk" in e]
        actual_tokens = sum(len(c["chunk"].split()) for c in chunks)
        assert done_event["total_tokens"] >= actual_tokens  # At least word count

@pytest.mark.asyncio
class TestTranscriptionWithModels:
    """Test transcription with different models"""
    
    def test_transcribe_with_model_parameter(self):
        """Test transcription endpoint with model parameter"""
        client = TestClient(app)
        
        # Test with mock model
        audio_content = b"fake audio data"
        files = {"audio": ("test.webm", audio_content, "audio/webm")}
        
        response = client.post("/transcribe?model=mock", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "text" in data
    
    @patch('main.transcribe_with_gemini')
    async def test_transcribe_with_gemini_model(self, mock_transcribe):
        """Test transcription with Gemini model"""
        mock_transcribe.return_value = "Transcribed text from Gemini"
        
        client = TestClient(app)
        audio_content = b"fake audio data"
        files = {"audio": ("test.webm", audio_content, "audio/webm")}
        
        response = client.post("/transcribe?model=gemini-flash", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["text"] == "Transcribed text from Gemini"
        assert data["model"] == "gemini-flash"
        
        # Verify Gemini handler was called
        mock_transcribe.assert_called_once()

class TestModelSelection:
    """Test model selection logic"""
    
    def test_invalid_model_fallback(self):
        """Test fallback when invalid model is specified"""
        client = TestClient(app)
        
        # Test streaming with invalid model
        with client as c:
            with c.stream("GET", "/stream/Test?model=invalid-model") as response:
                assert response.status_code == 200
                # Should still work, likely falling back
        
        # Test transcription with invalid model
        files = {"audio": ("test.webm", b"data", "audio/webm")}
        response = client.post("/transcribe?model=invalid-model", files=files)
        assert response.status_code == 200
    
    def test_model_list_consistency(self):
        """Test that model lists are consistent"""
        assert "gemini-flash" in TEXT_MODELS
        assert "gemini-flash" in AUDIO_MODELS
        assert "mock" in TEXT_MODELS
        assert "mock" in AUDIO_MODELS
        
        # Gemini models should use proper paths
        assert TEXT_MODELS["gemini-flash"].startswith("gemini/")
        assert TEXT_MODELS["gemini-pro"].startswith("gemini/")