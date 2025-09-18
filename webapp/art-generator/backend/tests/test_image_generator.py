import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import numpy as np
from datetime import datetime
import base64
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from image_generator import ImageGenerator
from models import ImageProvider, GeneratedImage


@pytest.fixture
def mock_openai_client():
    mock = AsyncMock()
    mock.images.generate = AsyncMock()
    return mock


@pytest.fixture
def image_generator(mock_openai_client):
    with patch('openai.AsyncOpenAI', return_value=mock_openai_client):
        with patch.dict('os.environ', {
            'OPENAI_API_KEY': 'test-key',
            'REPLICATE_API_TOKEN': 'test-token'
        }):
            generator = ImageGenerator()
            generator.openai_client = mock_openai_client
            return generator


class TestImageGenerator:
    """Test suite for ImageGenerator class"""
    
    @pytest.mark.asyncio
    async def test_init_with_api_keys(self):
        """Test initialization with API keys"""
        with patch.dict('os.environ', {
            'OPENAI_API_KEY': 'test-openai-key',
            'REPLICATE_API_TOKEN': 'test-replicate-token'
        }):
            generator = ImageGenerator()
            assert generator.openai_key == 'test-openai-key'
            assert generator.replicate_token == 'test-replicate-token'
            assert not generator.mock_mode
    
    @pytest.mark.asyncio
    async def test_init_mock_mode(self):
        """Test initialization in mock mode when no API keys"""
        with patch.dict('os.environ', {}, clear=True):
            generator = ImageGenerator()
            assert generator.mock_mode
            assert generator.openai_client is None
    
    @pytest.mark.asyncio
    async def test_generate_openai_image(self, image_generator, mock_openai_client):
        """Test OpenAI image generation"""
        # Mock response
        mock_response = Mock()
        mock_response.data = [Mock(url='https://example.com/image.png')]
        mock_openai_client.images.generate.return_value = mock_response
        
        # Generate image
        result = await image_generator.generate_image(
            prompt="A beautiful sunset",
            provider=ImageProvider.OPENAI,
            size="1024x1024"
        )
        
        # Assertions
        assert isinstance(result, GeneratedImage)
        assert result.url == 'https://example.com/image.png'
        assert result.prompt == "A beautiful sunset"
        assert result.provider == ImageProvider.OPENAI
        assert len(result.latent_vector) == 512
        mock_openai_client.images.generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_with_latent_vector(self, image_generator, mock_openai_client):
        """Test image generation with provided latent vector"""
        # Mock response
        mock_response = Mock()
        mock_response.data = [Mock(url='https://example.com/image.png')]
        mock_openai_client.images.generate.return_value = mock_response
        
        # Custom latent vector
        latent_vector = np.random.randn(512).tolist()
        
        # Generate image
        result = await image_generator.generate_image(
            prompt="A landscape",
            provider=ImageProvider.OPENAI,
            latent_vector=latent_vector
        )
        
        # Check that prompt was modified based on latent vector
        call_args = mock_openai_client.images.generate.call_args
        modified_prompt = call_args[1]['prompt']
        assert "A landscape" in modified_prompt
        # Should have style modifiers added
        assert any(modifier in modified_prompt for modifier in [
            'bright', 'dark', 'warm', 'cool', 'detailed', 'minimalist'
        ])
    
    @pytest.mark.asyncio
    async def test_generate_replicate_image(self, image_generator):
        """Test Replicate image generation"""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock the async client instance
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            # Mock prediction creation
            mock_instance.post.return_value.json.return_value = {
                'id': 'test-prediction-id'
            }
            
            # Mock prediction status check
            mock_instance.get.return_value.json.side_effect = [
                {'status': 'processing'},
                {'status': 'succeeded', 'output': ['https://replicate.com/image.png']}
            ]
            
            # Generate image
            result = await image_generator.generate_image(
                prompt="A futuristic city",
                provider=ImageProvider.REPLICATE,
                negative_prompt="blurry, low quality"
            )
            
            # Assertions
            assert isinstance(result, GeneratedImage)
            assert result.url == 'https://replicate.com/image.png'
            assert result.provider == ImageProvider.REPLICATE
            assert result.metadata['negative_prompt'] == "blurry, low quality"
    
    @pytest.mark.asyncio
    async def test_generate_mock_image(self):
        """Test mock image generation"""
        with patch.dict('os.environ', {}, clear=True):
            generator = ImageGenerator()
            
            result = await generator.generate_image(
                prompt="Test prompt",
                provider=ImageProvider.OPENAI,
                size="512x512",
                style="artistic"
            )
            
            # Assertions
            assert isinstance(result, GeneratedImage)
            assert result.url.startswith('data:image/png;base64,')
            assert result.prompt == "Test prompt"
            assert result.metadata['mock'] is True
            assert result.metadata['style'] == "artistic"
            
            # Decode and check image
            base64_data = result.url.split(',')[1]
            image_data = base64.b64decode(base64_data)
            assert len(image_data) > 0
    
    @pytest.mark.asyncio
    async def test_generate_local_image(self, image_generator):
        """Test local model image generation"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            # Mock successful SD WebUI response
            mock_instance.post.return_value.status_code = 200
            mock_instance.post.return_value.json.return_value = {
                'images': ['base64encodedimage']
            }
            
            result = await image_generator.generate_image(
                prompt="A mountain landscape",
                provider=ImageProvider.LOCAL,
                size="768x768"
            )
            
            assert isinstance(result, GeneratedImage)
            assert result.url == "data:image/png;base64,base64encodedimage"
            assert result.provider == ImageProvider.LOCAL
    
    @pytest.mark.asyncio
    async def test_generate_local_fallback_to_mock(self, image_generator):
        """Test local model falling back to mock when unavailable"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            # Mock failed SD WebUI response
            mock_instance.post.side_effect = Exception("Connection error")
            
            result = await image_generator.generate_image(
                prompt="A forest",
                provider=ImageProvider.LOCAL
            )
            
            # Should fallback to mock
            assert result.url.startswith('data:image/png;base64,')
            assert result.metadata['mock'] is True
    
    def test_generate_latent_vector(self, image_generator):
        """Test latent vector generation"""
        vector1 = image_generator._generate_latent_vector("test prompt")
        vector2 = image_generator._generate_latent_vector("test prompt")
        vector3 = image_generator._generate_latent_vector("different prompt")
        
        # Same prompt should generate same vector
        assert vector1 == vector2
        # Different prompt should generate different vector
        assert vector1 != vector3
        # Vector should be normalized
        assert abs(np.linalg.norm(vector1) - 1.0) < 0.001
        # Vector should have correct dimension
        assert len(vector1) == 512
    
    def test_modify_prompt_from_latent(self, image_generator):
        """Test prompt modification based on latent vector"""
        base_prompt = "A landscape"
        
        # Test bright, warm, detailed, artistic
        latent_bright = np.ones(64) * 0.6
        modified = image_generator._modify_prompt_from_latent(base_prompt, latent_bright.tolist())
        assert "bright" in modified
        assert "warm colors" in modified
        assert "highly detailed" in modified
        assert "artistic" in modified
        
        # Test dark, cool, minimalist, photorealistic
        latent_dark = np.ones(64) * -0.6
        modified = image_generator._modify_prompt_from_latent(base_prompt, latent_dark.tolist())
        assert "dark" in modified
        assert "cool colors" in modified
        assert "minimalist" in modified
        assert "photorealistic" in modified
        
        # Test neutral (no modifications)
        latent_neutral = np.zeros(64)
        modified = image_generator._modify_prompt_from_latent(base_prompt, latent_neutral.tolist())
        assert modified == base_prompt
    
    @pytest.mark.asyncio
    async def test_get_image_embedding(self, image_generator):
        """Test image embedding generation"""
        embedding = await image_generator.get_image_embedding("https://example.com/image.jpg")
        
        assert isinstance(embedding, list)
        assert len(embedding) == 512
        assert abs(np.linalg.norm(embedding) - 1.0) < 0.001
    
    @pytest.mark.asyncio
    async def test_check_local_model(self):
        """Test local model availability check"""
        with patch('requests.get') as mock_get:
            # Test successful check
            mock_get.return_value.status_code = 200
            generator = ImageGenerator()
            assert generator._check_local_model()
            
            # Test failed check
            mock_get.side_effect = Exception("Connection error")
            generator = ImageGenerator()
            assert not generator._check_local_model()
    
    @pytest.mark.asyncio
    async def test_error_handling_openai(self, image_generator, mock_openai_client):
        """Test error handling for OpenAI generation"""
        mock_openai_client.images.generate.side_effect = Exception("API Error")
        
        with pytest.raises(Exception) as exc_info:
            await image_generator.generate_image(
                prompt="Test",
                provider=ImageProvider.OPENAI
            )
        assert "API Error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_replicate_generation_failure(self, image_generator):
        """Test Replicate generation failure handling"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            # Mock prediction creation
            mock_instance.post.return_value.json.return_value = {
                'id': 'test-prediction-id'
            }
            
            # Mock failed prediction
            mock_instance.get.return_value.json.return_value = {
                'status': 'failed',
                'error': 'Model error'
            }
            
            with pytest.raises(Exception) as exc_info:
                await image_generator.generate_image(
                    prompt="Test",
                    provider=ImageProvider.REPLICATE
                )
            assert "Model error" in str(exc_info.value)