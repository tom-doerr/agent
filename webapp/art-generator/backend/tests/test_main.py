import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import asyncio
from unittest.mock import Mock, patch, AsyncMock

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import Base, get_session
from models import GenerationRequest, ImageProvider

# Test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def test_db():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async def override_get_session():
        async with async_session() as session:
            yield session
    
    app.dependency_overrides[get_session] = override_get_session
    
    yield engine
    
    await engine.dispose()
    app.dependency_overrides.clear()


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(test_db, client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_generate_image_endpoint(client):
    with patch('main.image_generator.generate_image') as mock_generate:
        mock_generate.return_value = AsyncMock(
            id="test-id",
            url="http://example.com/image.png",
            prompt="test prompt",
            provider=ImageProvider.OPENAI,
            latent_vector=[0.1] * 512,
            created_at="2024-01-01T00:00:00",
            metadata={}
        )
        
        request_data = {
            "prompt": "test prompt",
            "provider": "openai",
            "size": "1024x1024"
        }
        
        response = await client.post("/generate", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_get_images(client):
    response = await client.get("/images")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_submit_comparison(client):
    comparison_data = {
        "winner_id": "image1",
        "loser_id": "image2",
        "comparison_type": "a_b_test"
    }
    
    with patch('main.preference_learner.add_comparison') as mock_add:
        mock_add.return_value = AsyncMock()
        
        response = await client.post("/preferences/compare", json=comparison_data)
        assert response.status_code == 200
        assert response.json()["status"] == "success"


@pytest.mark.asyncio
async def test_submit_rating(client):
    rating_data = {
        "image_id": "test-image",
        "score": 0.8,
        "feedback_type": "rating"
    }
    
    with patch('main.preference_learner.add_rating') as mock_add:
        mock_add.return_value = AsyncMock()
        
        response = await client.post("/preferences/rate", json=rating_data)
        assert response.status_code == 200
        assert response.json()["status"] == "success"


@pytest.mark.asyncio
async def test_update_ranking(client):
    ranking_data = {
        "image_rankings": ["image1", "image2", "image3"]
    }
    
    with patch('main.preference_learner.add_comparison') as mock_add:
        mock_add.return_value = AsyncMock()
        
        response = await client.post("/preferences/rank", json=ranking_data)
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["comparisons_added"] == 3  # 3 choose 2


@pytest.mark.asyncio
async def test_predict_preference(client):
    with patch('main.preference_learner.predict_preference') as mock_predict:
        mock_predict.return_value = AsyncMock(
            image_id="test-image",
            predicted_score=0.75,
            confidence=0.8
        )
        
        response = await client.get("/predict/test-image")
        assert response.status_code == 200
        data = response.json()
        assert data["image_id"] == "test-image"
        assert data["predicted_score"] == 0.75
        assert data["confidence"] == 0.8


@pytest.mark.asyncio
async def test_generate_optimal_no_images(client):
    response = await client.post("/generate/optimal")
    assert response.status_code == 400
    assert "No images available" in response.json()["detail"]