import pytest
import os
from unittest.mock import patch, AsyncMock, Mock
import json
from gemini_handler import stream_gemini_response, get_gemini_response, transcribe_with_gemini

@pytest.mark.asyncio
class TestGeminiHandler:
    """Test Gemini integration handler"""
    
    @patch('gemini_handler.acompletion')
    async def test_stream_gemini_response(self, mock_acompletion):
        """Test streaming response from Gemini"""
        # Mock streaming response
        mock_chunk1 = Mock()
        mock_chunk1.choices = [Mock(delta=Mock(content="Hello "))]
        
        mock_chunk2 = Mock()
        mock_chunk2.choices = [Mock(delta=Mock(content="world!"))]
        
        async def mock_stream(*args, **kwargs):
            yield mock_chunk1
            yield mock_chunk2
        
        mock_acompletion.return_value = mock_stream()
        
        # Collect events
        events = []
        async for event in stream_gemini_response("Test question"):
            events.append(event)
        
        # Parse events
        parsed_events = []
        for event in events:
            if event.startswith("data: "):
                parsed_events.append(json.loads(event[6:].strip()))
        
        # Verify events
        assert parsed_events[0].get("start") == True
        assert any(e.get("chunk") == "Hello " for e in parsed_events)
        assert any(e.get("chunk") == "world!" for e in parsed_events)
        assert parsed_events[-1].get("done") == True
        
        # Verify API call
        mock_acompletion.assert_called_once()
        call_args = mock_acompletion.call_args
        assert call_args[1]["model"] == "gemini/gemini-2.0-flash-exp"
        assert call_args[1]["stream"] == True
    
    @patch('gemini_handler.acompletion')
    async def test_get_gemini_response(self, mock_acompletion):
        """Test non-streaming response from Gemini"""
        # Mock response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="This is the answer"))]
        mock_acompletion.return_value = mock_response
        
        result = await get_gemini_response("What is Python?")
        
        assert result == "This is the answer"
        
        # Verify API call
        mock_acompletion.assert_called_once()
        call_args = mock_acompletion.call_args
        assert call_args[1]["model"] == "gemini/gemini-2.0-flash-exp"
        assert call_args[1]["stream"] == False  # Not in kwargs means False
    
    @patch('gemini_handler.acompletion')
    async def test_transcribe_with_gemini(self, mock_acompletion):
        """Test audio transcription with Gemini"""
        # Mock response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="This is the transcribed text"))]
        mock_acompletion.return_value = mock_response
        
        audio_content = b"fake audio data"
        result = await transcribe_with_gemini(audio_content, "audio/webm")
        
        assert result == "This is the transcribed text"
        
        # Verify multimodal API call
        mock_acompletion.assert_called_once()
        call_args = mock_acompletion.call_args
        messages = call_args[1]["messages"]
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        
        # Check multimodal content
        content = messages[0]["content"]
        assert isinstance(content, list)
        assert any(item.get("type") == "text" for item in content)
        assert any(item.get("type") == "audio_url" for item in content)
    
    @patch('gemini_handler.acompletion')
    async def test_error_handling_in_streaming(self, mock_acompletion):
        """Test error handling during streaming"""
        # Mock error
        async def mock_error_stream(*args, **kwargs):
            raise Exception("API Error")
        
        mock_acompletion.return_value = mock_error_stream()
        
        events = []
        async for event in stream_gemini_response("Test"):
            events.append(event)
        
        # Should return error event
        parsed_events = [json.loads(e[6:].strip()) for e in events if e.startswith("data: ")]
        error_events = [e for e in parsed_events if "error" in e]
        assert len(error_events) == 1
        assert "API Error" in error_events[0]["error"]
    
    @patch('gemini_handler.acompletion')
    async def test_transcribe_fallback_for_unsupported_audio(self, mock_acompletion):
        """Test fallback when Gemini doesn't support audio"""
        # Mock audio-related error
        async def mock_audio_error(*args, **kwargs):
            raise Exception("Audio format not supported")
        
        mock_acompletion.side_effect = mock_audio_error
        
        audio_content = b"fake audio"
        result = await transcribe_with_gemini(audio_content)
        
        # Should return fallback message
        assert "simulated transcription" in result.lower()

@pytest.mark.integration
class TestGeminiIntegrationWithAPI:
    """Integration tests that require actual Gemini API (skipped by default)"""
    
    @pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="Requires GEMINI_API_KEY")
    @pytest.mark.asyncio
    async def test_real_gemini_streaming(self):
        """Test actual Gemini API streaming"""
        events = []
        async for event in stream_gemini_response("What is 2+2?"):
            events.append(event)
        
        # Should get valid response
        assert len(events) > 2  # At least start, chunk, done
        
        parsed = [json.loads(e[6:].strip()) for e in events if e.startswith("data: ")]
        assert any(e.get("start") for e in parsed)
        assert any("chunk" in e for e in parsed)
        assert any(e.get("done") for e in parsed)
        
        # Response should contain "4" somewhere
        chunks = "".join(e.get("chunk", "") for e in parsed)
        assert "4" in chunks
    
    @pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="Requires GEMINI_API_KEY")
    @pytest.mark.asyncio
    async def test_real_gemini_models(self):
        """Test different Gemini models"""
        models_to_test = [
            "gemini/gemini-2.0-flash-exp",
            "gemini/gemini-1.5-pro"
        ]
        
        for model in models_to_test:
            response = await get_gemini_response("Say hello", model)
            assert len(response) > 0
            assert "hello" in response.lower() or "hi" in response.lower()

class TestGeminiConfiguration:
    """Test Gemini configuration and setup"""
    
    def test_api_key_configuration(self):
        """Test API key configuration"""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            # Import should set GEMINI_API_KEY
            import importlib
            import gemini_handler
            importlib.reload(gemini_handler)
            
            assert os.environ.get("GEMINI_API_KEY") == "test-key"
    
    def test_litellm_verbosity(self):
        """Test litellm verbosity configuration"""
        with patch.dict(os.environ, {"LITELLM_LOG": "DEBUG"}):
            import importlib
            import gemini_handler
            importlib.reload(gemini_handler)
            
            # Should enable verbose mode
            import litellm
            assert litellm.set_verbose == True
    
    @patch('gemini_handler.acompletion')
    async def test_temperature_settings(self, mock_acompletion):
        """Test temperature is set correctly for different operations"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Response"))]
        mock_acompletion.return_value = mock_response
        
        # Test general response (higher temperature)
        await get_gemini_response("Creative question")
        assert mock_acompletion.call_args[1]["temperature"] == 0.7
        
        # Test transcription (lower temperature)
        mock_acompletion.reset_mock()
        await transcribe_with_gemini(b"audio")
        assert mock_acompletion.call_args[1]["temperature"] == 0.3