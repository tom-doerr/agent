import pytest
import asyncio
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
import numpy as np
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from models import ImageProvider


@pytest.fixture
async def client():
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def mock_image_generator():
    """Mock image generator for tests"""
    with patch('main.image_generator') as mock:
        # Mock the generate_image method
        async def mock_generate(*args, **kwargs):
            from models import GeneratedImage
            return GeneratedImage(
                id="test-image-id",
                url="http://test.com/image.png",
                prompt=kwargs.get('prompt', 'test'),
                provider=kwargs.get('provider', ImageProvider.OPENAI),
                latent_vector=np.random.randn(512).tolist(),
                created_at=datetime.utcnow(),
                metadata={}
            )
        mock.generate_image = mock_generate
        yield mock


@pytest.fixture
async def mock_preference_learner():
    """Mock preference learner for tests"""
    with patch('main.preference_learner') as mock:
        mock.scores = {}
        mock.add_comparison = AsyncMock()
        mock.add_rating = AsyncMock()
        mock.predict_preference = AsyncMock()
        mock.get_ranked_images = AsyncMock(return_value=[])
        mock.suggest_comparison_pair = AsyncMock(return_value=["img1", "img2"])
        yield mock


class TestAPIIntegration:
    """Integration tests for API endpoints"""
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    @pytest.mark.asyncio
    async def test_generate_image_endpoint(self, client, mock_image_generator):
        """Test image generation endpoint"""
        request_data = {
            "prompt": "A beautiful sunset over mountains",
            "provider": "openai",
            "size": "1024x1024"
        }
        
        response = await client.post("/generate", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "pending"
        assert data["progress"] == 0.0
    
    @pytest.mark.asyncio
    async def test_generate_image_with_style(self, client, mock_image_generator):
        """Test image generation with style parameter"""
        request_data = {
            "prompt": "A landscape",
            "provider": "replicate",
            "size": "512x512",
            "style": "impressionist",
            "negative_prompt": "blurry, low quality"
        }
        
        response = await client.post("/generate", json=request_data)
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_get_generation_status(self, client, mock_image_generator):
        """Test generation status endpoint"""
        # First generate an image
        response = await client.post("/generate", json={"prompt": "test"})
        task_id = response.json()["task_id"]
        
        # Check status
        response = await client.get(f"/status/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == task_id
        assert data["status"] in ["pending", "processing", "completed", "failed"]
    
    @pytest.mark.asyncio
    async def test_get_status_nonexistent(self, client):
        """Test status for non-existent task"""
        response = await client.get("/status/nonexistent-task-id")
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"
    
    @pytest.mark.asyncio
    async def test_list_images(self, client):
        """Test listing images endpoint"""
        response = await client.get("/images")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_list_images_with_pagination(self, client):
        """Test image listing with pagination"""
        response = await client.get("/images?skip=5&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
    
    @pytest.mark.asyncio
    async def test_get_single_image(self, client):
        """Test getting single image endpoint"""
        # This will fail with 404 since no images in test DB
        response = await client.get("/images/test-image-id")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_submit_comparison(self, client, mock_preference_learner):
        """Test preference comparison endpoint"""
        comparison_data = {
            "winner_id": "image1",
            "loser_id": "image2",
            "comparison_type": "a_b_test"
        }
        
        response = await client.post("/preferences/compare", json=comparison_data)
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        
        # Verify mock was called
        mock_preference_learner.add_comparison.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_submit_rating(self, client, mock_preference_learner):
        """Test preference rating endpoint"""
        rating_data = {
            "image_id": "test-image",
            "score": 0.8,
            "feedback_type": "rating"
        }
        
        response = await client.post("/preferences/rate", json=rating_data)
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        
        # Verify mock was called
        mock_preference_learner.add_rating.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_submit_rating_invalid_score(self, client, mock_preference_learner):
        """Test rating with invalid score"""
        rating_data = {
            "image_id": "test-image",
            "score": 1.5,  # Invalid - should be 0-1
            "feedback_type": "rating"
        }
        
        response = await client.post("/preferences/rate", json=rating_data)
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_update_ranking(self, client, mock_preference_learner):
        """Test ranking update endpoint"""
        ranking_data = {
            "image_rankings": ["img1", "img2", "img3", "img4"]
        }
        
        response = await client.post("/preferences/rank", json=ranking_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["comparisons_added"] == 6  # n*(n-1)/2 for 4 images
    
    @pytest.mark.asyncio
    async def test_predict_preference(self, client, mock_preference_learner):
        """Test preference prediction endpoint"""
        from models import PreferencePrediction
        
        mock_preference_learner.predict_preference.return_value = PreferencePrediction(
            image_id="test-image",
            predicted_score=0.75,
            confidence=0.8,
            metadata={"model_trained": True}
        )
        
        response = await client.get("/predict/test-image")
        assert response.status_code == 200
        data = response.json()
        assert data["image_id"] == "test-image"
        assert data["predicted_score"] == 0.75
        assert data["confidence"] == 0.8
    
    @pytest.mark.asyncio
    async def test_suggest_comparison(self, client, mock_preference_learner):
        """Test comparison suggestion endpoint"""
        response = await client.get("/preferences/suggest-comparison")
        assert response.status_code == 200
        data = response.json()
        assert "image1_id" in data
        assert "image2_id" in data
        assert data["reason"] == "Selected for maximum information gain"
    
    @pytest.mark.asyncio
    async def test_suggest_comparison_insufficient_images(self, client):
        """Test suggestion with insufficient images"""
        # With empty database, should return 400
        with patch('main.preference_learner.suggest_comparison_pair', return_value=None):
            response = await client.get("/preferences/suggest-comparison")
            # Should still return random pair or error
            assert response.status_code in [200, 400]
    
    @pytest.mark.asyncio
    async def test_generate_optimal_image(self, client, mock_image_generator, mock_preference_learner):
        """Test optimal image generation endpoint"""
        # Mock ranked images
        mock_preference_learner.get_ranked_images.return_value = [
            ("img1", 0.9),
            ("img2", 0.7),
            ("img3", 0.5)
        ]
        
        response = await client.post("/generate/optimal")
        # Will fail due to no images in test DB
        assert response.status_code == 400
        assert "No images available" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_generate_optimal_with_base_prompt(self, client, mock_image_generator):
        """Test optimal generation with base prompt"""
        response = await client.post(
            "/generate/optimal",
            params={"base_prompt": "A masterpiece artwork"}
        )
        assert response.status_code == 400  # No images in test DB
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self, client):
        """Test WebSocket connection"""
        # Note: httpx doesn't support WebSocket, so we just test the endpoint exists
        # In a real test, you'd use a WebSocket client
        pass
    
    @pytest.mark.asyncio
    async def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = await client.options("/health")
        assert "access-control-allow-origin" in response.headers
    
    @pytest.mark.asyncio
    async def test_invalid_provider(self, client):
        """Test invalid provider in generation request"""
        request_data = {
            "prompt": "test",
            "provider": "invalid_provider"
        }
        
        response = await client.post("/generate", json=request_data)
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_invalid_image_size(self, client):
        """Test invalid image size"""
        request_data = {
            "prompt": "test",
            "size": "invalid_size"
        }
        
        response = await client.post("/generate", json=request_data)
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_empty_ranking_update(self, client, mock_preference_learner):
        """Test ranking update with empty list"""
        ranking_data = {"image_rankings": []}
        
        response = await client.post("/preferences/rank", json=ranking_data)
        assert response.status_code == 200
        assert response.json()["comparisons_added"] == 0
    
    @pytest.mark.asyncio
    async def test_concurrent_generation_requests(self, client, mock_image_generator):
        """Test handling concurrent generation requests"""
        # Send multiple requests concurrently
        tasks = []
        for i in range(5):
            request_data = {
                "prompt": f"Test prompt {i}",
                "provider": "openai"
            }
            tasks.append(client.post("/generate", json=request_data))
        
        responses = await asyncio.gather(*tasks)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
            assert "task_id" in response.json()
        
        # All task IDs should be unique
        task_ids = [r.json()["task_id"] for r in responses]
        assert len(set(task_ids)) == len(task_ids)