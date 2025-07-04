import pytest
from fastapi.testclient import TestClient
from main import app
import json
import asyncio

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "DSPy Streaming API"}

def test_stream_endpoint():
    """Test SSE streaming endpoint"""
    with client as c:
        with c.stream("GET", "/stream/What is Python") as response:
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
            
            # Collect streamed data
            chunks = []
            for line in response.iter_lines():
                if line.startswith(b"data: "):
                    data = json.loads(line[6:])
                    if "chunk" in data:
                        chunks.append(data["chunk"])
                    elif data.get("done"):
                        break
            
            # Should have received some response
            assert len(chunks) > 0
            full_response = "".join(chunks)
            assert len(full_response) > 0

def test_stream_empty_question():
    """Test streaming with empty question"""
    with client as c:
        with c.stream("GET", "/stream/") as response:
            # Should still work but with minimal response
            assert response.status_code == 200

@pytest.mark.asyncio
async def test_websocket():
    """Test WebSocket endpoint"""
    with client.websocket_connect("/ws") as websocket:
        # Send a question
        websocket.send_json({
            "type": "question",
            "question": "What is FastAPI?"
        })
        
        # Collect response chunks
        chunks = []
        while True:
            data = websocket.receive_json()
            if data["type"] == "chunk":
                chunks.append(data["content"])
            elif data["type"] == "complete":
                break
            elif data["type"] == "error":
                pytest.fail(f"Received error: {data['message']}")
        
        # Verify we got a response
        assert len(chunks) > 0
        full_response = "".join(chunks)
        assert len(full_response) > 0

@pytest.mark.asyncio
async def test_websocket_error_handling():
    """Test WebSocket error handling"""
    with client.websocket_connect("/ws") as websocket:
        # Send invalid message
        websocket.send_text("invalid json")
        
        # Should receive error response
        data = websocket.receive_json()
        assert data["type"] == "error"

def test_cors_headers():
    """Test CORS headers are set correctly"""
    response = client.get("/", headers={"Origin": "http://localhost:3000"})
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert response.headers["access-control-allow-credentials"] == "true"

def test_transcribe_endpoint():
    """Test audio transcription endpoint"""
    # Create a fake audio file
    audio_content = b"fake audio data"
    files = {"audio": ("test.webm", audio_content, "audio/webm")}
    
    response = client.post("/transcribe", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "text" in data
    assert len(data["text"]) > 0

def test_transcribe_endpoint_no_file():
    """Test transcription endpoint without file"""
    response = client.post("/transcribe")
    
    assert response.status_code == 422  # Unprocessable Entity

def test_transcribe_endpoint_empty_file():
    """Test transcription endpoint with empty file"""
    files = {"audio": ("empty.webm", b"", "audio/webm")}
    
    response = client.post("/transcribe", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_transcribe_endpoint_large_file():
    """Test transcription endpoint with large file"""
    # Create 5MB file (reasonable test size)
    large_content = b"x" * (5 * 1024 * 1024)
    files = {"audio": ("large.webm", large_content, "audio/webm")}
    
    response = client.post("/transcribe", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"