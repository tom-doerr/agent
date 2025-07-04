import pytest
from unittest.mock import Mock, patch, AsyncMock
import numpy as np

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from image_generator import ImageGenerator
from models import ImageProvider, GeneratedImage


@pytest.fixture
def generator():
    return ImageGenerator()


@pytest.mark.asyncio
async def test_generate_openai_image(generator):
    # Test mock mode since no API key is set
    generator.mock_mode = True
    
    result = await generator.generate_image(
        prompt="A beautiful sunset",
        provider=ImageProvider.OPENAI,
        size="1024x1024",
        style="realistic"
    )
    
    assert isinstance(result, GeneratedImage)
    assert result.prompt == "A beautiful sunset"
    assert result.provider == ImageProvider.OPENAI
    assert len(result.latent_vector) == 512
    assert result.metadata["style"] == "realistic"
    assert result.metadata["mock"] is True
    assert result.url.startswith("data:image/png;base64,")


@pytest.mark.asyncio
async def test_generate_replicate_image(generator):
    # Test mock mode
    generator.mock_mode = True
    
    result = await generator.generate_image(
        prompt="A mountain landscape",
        provider=ImageProvider.REPLICATE,
        negative_prompt="blurry, low quality",
        size="512x512"
    )
    
    assert isinstance(result, GeneratedImage)
    assert result.prompt == "A mountain landscape"
    assert result.provider == ImageProvider.OPENAI  # Mock always returns OPENAI
    assert len(result.latent_vector) == 512
    assert result.metadata["mock"] is True
    assert result.url.startswith("data:image/png;base64,")


@pytest.mark.asyncio
async def test_generate_mock_image(generator):
    # Force mock mode
    generator.mock_mode = True
    
    result = await generator.generate_image(
        prompt="Test prompt",
        provider=ImageProvider.MOCK,
        size="1024x1024"
    )
    
    assert isinstance(result, GeneratedImage)
    assert result.prompt == "Test prompt"
    assert result.url.startswith("data:image/png;base64,")
    assert result.metadata["mock"] is True


def test_generate_latent_vector(generator):
    # Test deterministic vector generation
    vector1 = generator._generate_latent_vector("test prompt")
    vector2 = generator._generate_latent_vector("test prompt")
    
    assert len(vector1) == 512
    assert len(vector2) == 512
    assert vector1 == vector2  # Same prompt should give same vector
    
    # Test normalization
    vector_array = np.array(vector1)
    norm = np.linalg.norm(vector_array)
    assert abs(norm - 1.0) < 0.001  # Should be normalized
    
    # Different prompts should give different vectors
    vector3 = generator._generate_latent_vector("different prompt")
    assert vector1 != vector3


@pytest.mark.asyncio
async def test_get_image_embedding(generator):
    embedding = await generator.get_image_embedding("http://example.com/image.png")
    
    assert len(embedding) == 512
    assert isinstance(embedding, list)
    assert all(isinstance(x, float) for x in embedding)
    
    # Should be normalized
    norm = np.linalg.norm(np.array(embedding))
    assert abs(norm - 1.0) < 0.001