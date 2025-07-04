import pytest
import numpy as np
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from preference_learner import PreferenceLearner
from database import Base, ImageRecord
from models import PreferencePrediction

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_session():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Add test images
        for i in range(5):
            image = ImageRecord(
                id=f"test-image-{i}",
                url=f"http://example.com/image{i}.png",
                prompt=f"Test prompt {i}",
                provider="openai",
                latent_vector=np.random.randn(512).tolist(),
                created_at=datetime.utcnow()
            )
            session.add(image)
        await session.commit()
        
        yield session
    
    await engine.dispose()


@pytest.fixture
def learner():
    return PreferenceLearner(embedding_dim=512)


@pytest.mark.asyncio
async def test_add_comparison(test_session, learner):
    await learner.add_comparison(test_session, "test-image-0", "test-image-1")
    
    assert "test-image-0" in learner.scores
    assert "test-image-1" in learner.scores
    assert learner.scores["test-image-0"] > learner.scores["test-image-1"]
    assert learner.comparison_count["test-image-0"] == 1
    assert learner.comparison_count["test-image-1"] == 1


@pytest.mark.asyncio
async def test_add_rating(test_session, learner):
    await learner.add_rating(test_session, "test-image-0", 0.9)
    
    assert learner.scores["test-image-0"] == pytest.approx(0.9, rel=0.1)
    assert learner.comparison_count["test-image-0"] == 1


@pytest.mark.asyncio
async def test_predict_preference_untrained(test_session, learner):
    prediction = await learner.predict_preference(test_session, "test-image-0")
    
    assert isinstance(prediction, PreferencePrediction)
    assert prediction.image_id == "test-image-0"
    assert 0 <= prediction.predicted_score <= 1
    assert prediction.confidence == 0.1  # Low confidence when untrained


@pytest.mark.asyncio
async def test_predict_preference_trained(test_session, learner):
    # Add some training data
    for i in range(5):
        await learner.add_rating(test_session, f"test-image-{i}", i / 5)
    
    # Make prediction
    prediction = await learner.predict_preference(test_session, "test-image-0")
    
    assert isinstance(prediction, PreferencePrediction)
    assert prediction.image_id == "test-image-0"
    assert 0 <= prediction.predicted_score <= 1
    assert prediction.confidence > 0.1  # Higher confidence after training


@pytest.mark.asyncio
async def test_generate_optimal_direction(test_session, learner):
    base_embedding = np.random.randn(512)
    
    # Untrained should return normalized random direction
    direction = await learner.generate_optimal_prompt_direction(test_session, base_embedding)
    assert len(direction) == 512
    assert np.abs(np.linalg.norm(direction) - 1.0) < 0.001
    
    # Add training data
    for i in range(5):
        await learner.add_rating(test_session, f"test-image-{i}", i / 5)
    
    # Trained should return model coefficients
    direction = await learner.generate_optimal_prompt_direction(test_session, base_embedding)
    assert len(direction) == 512
    assert np.abs(np.linalg.norm(direction) - 1.0) < 0.001


@pytest.mark.asyncio
async def test_get_ranked_images(test_session, learner):
    image_ids = [f"test-image-{i}" for i in range(5)]
    
    # Add preferences
    await learner.add_rating(test_session, "test-image-0", 0.9)
    await learner.add_rating(test_session, "test-image-1", 0.7)
    await learner.add_rating(test_session, "test-image-2", 0.5)
    await learner.add_rating(test_session, "test-image-3", 0.3)
    await learner.add_rating(test_session, "test-image-4", 0.1)
    
    ranked = await learner.get_ranked_images(test_session, image_ids)
    
    assert len(ranked) == 5
    assert ranked[0][0] == "test-image-0"  # Highest score first
    assert ranked[-1][0] == "test-image-4"  # Lowest score last
    
    # Scores should be in descending order
    scores = [score for _, score in ranked]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.asyncio
async def test_save_load_state(test_session, learner, tmp_path):
    # Add some data
    await learner.add_rating(test_session, "test-image-0", 0.8)
    await learner.add_comparison(test_session, "test-image-1", "test-image-2")
    
    # Save state
    state_file = tmp_path / "state.json"
    learner.save_state(str(state_file))
    
    # Create new learner and load state
    new_learner = PreferenceLearner(embedding_dim=512)
    new_learner.load_state(str(state_file))
    
    assert new_learner.scores == learner.scores
    assert new_learner.comparison_count == learner.comparison_count
    assert new_learner.is_fitted == learner.is_fitted