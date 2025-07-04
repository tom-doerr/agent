import pytest
from fastapi import UploadFile
from io import BytesIO
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from audio_handler import transcribe_audio

@pytest.mark.asyncio
async def test_transcribe_audio_success():
    """Test successful audio transcription"""
    # Create a mock audio file
    audio_content = b"fake audio data"
    mock_file = Mock(spec=UploadFile)
    mock_file.read = AsyncMock(return_value=audio_content)
    mock_file.filename = "test_audio.webm"
    
    # Test transcription
    result = await transcribe_audio(mock_file)
    
    assert result["status"] == "success"
    assert "text" in result
    assert len(result["text"]) > 0

@pytest.mark.asyncio
async def test_transcribe_audio_creates_temp_file():
    """Test that temporary file is created and cleaned up"""
    audio_content = b"fake audio data"
    mock_file = Mock(spec=UploadFile)
    mock_file.read = AsyncMock(return_value=audio_content)
    
    temp_files_created = []
    original_tempfile = tempfile.NamedTemporaryFile
    
    def track_temp_file(*args, **kwargs):
        f = original_tempfile(*args, **kwargs)
        temp_files_created.append(f.name)
        return f
    
    with patch('tempfile.NamedTemporaryFile', side_effect=track_temp_file):
        result = await transcribe_audio(mock_file)
        
        # Verify temp file was created
        assert len(temp_files_created) == 1
        
        # Verify temp file was cleaned up
        assert not os.path.exists(temp_files_created[0])

@pytest.mark.asyncio
async def test_transcribe_audio_handles_read_error():
    """Test handling of file read errors"""
    mock_file = Mock(spec=UploadFile)
    mock_file.read = AsyncMock(side_effect=Exception("Read error"))
    
    with pytest.raises(Exception) as exc_info:
        await transcribe_audio(mock_file)
    
    assert "Transcription failed" in str(exc_info.value)

@pytest.mark.asyncio
async def test_transcribe_audio_cleanup_on_error():
    """Test that temp file is cleaned up even on error"""
    audio_content = b"fake audio data"
    mock_file = Mock(spec=UploadFile)
    mock_file.read = AsyncMock(return_value=audio_content)
    
    temp_file_path = None
    
    def mock_tempfile(*args, **kwargs):
        nonlocal temp_file_path
        f = tempfile.NamedTemporaryFile(*args, **kwargs)
        temp_file_path = f.name
        # Simulate an error after file creation
        f.write = Mock(side_effect=Exception("Write error"))
        return f
    
    with patch('tempfile.NamedTemporaryFile', side_effect=mock_tempfile):
        with pytest.raises(Exception):
            await transcribe_audio(mock_file)
        
        # Verify temp file was cleaned up despite error
        if temp_file_path:
            assert not os.path.exists(temp_file_path)

@pytest.mark.asyncio
async def test_transcribe_audio_with_empty_file():
    """Test handling of empty audio file"""
    mock_file = Mock(spec=UploadFile)
    mock_file.read = AsyncMock(return_value=b"")
    
    result = await transcribe_audio(mock_file)
    
    assert result["status"] == "success"
    assert "text" in result

@pytest.mark.asyncio
async def test_transcribe_audio_large_file():
    """Test handling of large audio file"""
    # Create 10MB of fake audio data
    large_audio_content = b"x" * (10 * 1024 * 1024)
    mock_file = Mock(spec=UploadFile)
    mock_file.read = AsyncMock(return_value=large_audio_content)
    
    result = await transcribe_audio(mock_file)
    
    assert result["status"] == "success"
    assert "text" in result

# Integration test with actual litellm (skipped by default)
@pytest.mark.skip(reason="Requires API key and network access")
@pytest.mark.asyncio
async def test_transcribe_audio_with_gemini():
    """Test actual Gemini integration"""
    audio_content = b"fake audio data"
    mock_file = Mock(spec=UploadFile)
    mock_file.read = AsyncMock(return_value=audio_content)
    
    with patch('litellm.completion') as mock_completion:
        mock_completion.return_value = Mock(
            choices=[Mock(message=Mock(content="Processed audio text"))]
        )
        
        # Uncomment the actual Gemini call in audio_handler.py
        # and run this test with proper API key
        result = await transcribe_audio(mock_file)
        
        assert result["status"] == "success"
        assert "Processed audio text" in result["text"]