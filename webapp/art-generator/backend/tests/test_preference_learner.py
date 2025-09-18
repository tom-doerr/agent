import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import numpy as np
from datetime import datetime
import json
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

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
                created_at=datetime.utcnow(),
                meta_data={"index": i}
            )
            session.add(image)
        await session.commit()
        
        yield session
    
    await engine.dispose()


@pytest.fixture
def learner():
    return PreferenceLearner(embedding_dim=512)


@pytest.fixture
def mock_session():
    """Mock session for unit tests"""
    session = AsyncMock(spec=AsyncSession)
    return session


class TestPreferenceLearner:
    """Comprehensive test suite for PreferenceLearner class"""
    
    @pytest.mark.asyncio
    async def test_init(self, learner):
        """Test initialization"""
        assert learner.embedding_dim == 512
        assert learner.scores == {}
        assert learner.comparison_count == {}
        assert learner.model is None
        assert not learner.is_fitted
    
    @pytest.mark.asyncio
    async def test_add_comparison(self, test_session, learner):
        """Test adding a comparison"""
        await learner.add_comparison(test_session, "test-image-0", "test-image-1")
        
        assert "test-image-0" in learner.scores
        assert "test-image-1" in learner.scores
        assert learner.scores["test-image-0"] > learner.scores["test-image-1"]
        assert learner.comparison_count["test-image-0"] == 1
        assert learner.comparison_count["test-image-1"] == 1
    
    @pytest.mark.asyncio
    async def test_multiple_comparisons(self, test_session, learner):
        """Test multiple comparisons create consistent ranking"""
        # A beats B, A beats C, B beats C
        await learner.add_comparison(test_session, "test-image-0", "test-image-1")
        await learner.add_comparison(test_session, "test-image-0", "test-image-2")
        await learner.add_comparison(test_session, "test-image-1", "test-image-2")
        
        # Expected order: A > B > C
        assert learner.scores["test-image-0"] > learner.scores["test-image-1"]
        assert learner.scores["test-image-1"] > learner.scores["test-image-2"]
    
    @pytest.mark.asyncio
    async def test_adaptive_k_factor(self, test_session, learner):
        """Test adaptive K-factor decreases with more comparisons"""
        initial_scores = []
        
        # Multiple comparisons between same pair
        for i in range(5):
            score_before = learner.scores.get("test-image-0", 0.5)
            await learner.add_comparison(test_session, "test-image-0", "test-image-1")
            score_after = learner.scores["test-image-0"]
            initial_scores.append(abs(score_after - score_before))
        
        # Score changes should decrease due to adaptive K
        assert initial_scores[0] > initial_scores[-1]
    
    @pytest.mark.asyncio
    async def test_add_rating(self, test_session, learner):
        """Test adding absolute rating"""
        await learner.add_rating(test_session, "test-image-0", 0.9)
        
        assert learner.scores["test-image-0"] == pytest.approx(0.9, rel=0.1)
        assert learner.comparison_count["test-image-0"] == 1
    
    @pytest.mark.asyncio
    async def test_add_rating_extreme_values(self, test_session, learner):
        """Test rating with boundary values"""
        await learner.add_rating(test_session, "test-image-0", 0.0)
        await learner.add_rating(test_session, "test-image-1", 1.0)
        
        assert 0.0 <= learner.scores["test-image-0"] <= 0.1
        assert 0.9 <= learner.scores["test-image-1"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_predict_preference_untrained(self, test_session, learner):
        """Test prediction when model is not trained"""
        prediction = await learner.predict_preference(test_session, "test-image-0")
        
        assert isinstance(prediction, PreferencePrediction)
        assert prediction.image_id == "test-image-0"
        assert 0 <= prediction.predicted_score <= 1
        assert prediction.confidence == 0.1  # Low confidence when untrained
        assert not prediction.metadata.get("model_trained", False)
    
    @pytest.mark.asyncio
    async def test_predict_preference_trained(self, test_session, learner):
        """Test prediction with trained model"""
        # Add training data
        for i in range(5):
            await learner.add_rating(test_session, f"test-image-{i}", i / 5)
        
        # Train model
        learner._train_model()
        
        # Make prediction
        prediction = await learner.predict_preference(test_session, "test-image-0")
        
        assert isinstance(prediction, PreferencePrediction)
        assert prediction.image_id == "test-image-0"
        assert 0 <= prediction.predicted_score <= 1
        assert prediction.confidence > 0.1  # Higher confidence after training
        assert prediction.metadata.get("model_trained", False)
    
    @pytest.mark.asyncio
    async def test_predict_missing_image(self, mock_session, learner):
        """Test prediction for non-existent image"""
        mock_session.get.return_value = None
        
        prediction = await learner.predict_preference(mock_session, "missing-image")
        
        assert prediction.predicted_score == 0.5
        assert prediction.confidence == 0.0
        assert prediction.metadata["error"] == "Image not found"
    
    @pytest.mark.asyncio
    async def test_suggest_comparison_pair(self, test_session, learner):
        """Test active learning comparison suggestion"""
        # Add some comparisons
        await learner.add_comparison(test_session, "test-image-0", "test-image-1")
        await learner.add_comparison(test_session, "test-image-0", "test-image-2")
        
        # Get suggestion
        image_ids = [f"test-image-{i}" for i in range(5)]
        pair = await learner.suggest_comparison_pair(test_session, image_ids)
        
        assert len(pair) == 2
        # Should suggest images with fewer comparisons
        assert "test-image-3" in pair or "test-image-4" in pair
    
    @pytest.mark.asyncio
    async def test_suggest_comparison_insufficient_images(self, test_session, learner):
        """Test suggestion with insufficient images"""
        pair = await learner.suggest_comparison_pair(test_session, ["test-image-0"])
        assert pair is None
    
    @pytest.mark.asyncio
    async def test_generate_optimal_direction(self, test_session, learner):
        """Test optimal prompt direction generation"""
        base_embedding = np.random.randn(512)
        
        # Untrained should return normalized random direction
        direction = await learner.generate_optimal_prompt_direction(test_session, base_embedding)
        assert len(direction) == 512
        assert np.abs(np.linalg.norm(direction) - 1.0) < 0.001
        
        # Add training data
        for i in range(5):
            await learner.add_rating(test_session, f"test-image-{i}", i / 5)
        
        # Train model
        learner._train_model()
        
        # Trained should return model-based direction
        direction = await learner.generate_optimal_prompt_direction(test_session, base_embedding)
        assert len(direction) == 512
        assert np.abs(np.linalg.norm(direction) - 1.0) < 0.001
    
    @pytest.mark.asyncio
    async def test_get_ranked_images(self, test_session, learner):
        """Test image ranking"""
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
    async def test_get_ranked_images_empty(self, test_session, learner):
        """Test ranking with empty image list"""
        ranked = await learner.get_ranked_images(test_session, [])
        assert ranked == []
    
    @pytest.mark.asyncio
    async def test_train_model_insufficient_data(self, learner):
        """Test model training with insufficient data"""
        # Add only 2 samples
        learner.scores = {"img1": 0.7, "img2": 0.3}
        learner.embeddings = {
            "img1": np.random.randn(512),
            "img2": np.random.randn(512)
        }
        
        # Should not train with < 3 samples
        learner._train_model()
        assert not learner.is_fitted
        assert learner.model is None
    
    @pytest.mark.asyncio
    async def test_train_model_success(self, learner):
        """Test successful model training"""
        # Add sufficient data
        for i in range(5):
            img_id = f"img_{i}"
            learner.scores[img_id] = 0.5 + i * 0.1
            learner.embeddings[img_id] = np.random.randn(512)
            learner.comparison_count[img_id] = i + 1
        
        # Train model
        learner._train_model()
        
        assert learner.is_fitted
        assert learner.model is not None
        assert hasattr(learner.model, 'predict')
    
    @pytest.mark.asyncio
    async def test_calculate_confidence(self, learner):
        """Test confidence calculation"""
        # No comparisons = low confidence
        conf = learner._calculate_confidence("img1", comparisons=0)
        assert conf == 0.1
        
        # Few comparisons = medium confidence
        conf = learner._calculate_confidence("img1", comparisons=5)
        assert 0.1 < conf < 0.5
        
        # Many comparisons = high confidence
        conf = learner._calculate_confidence("img1", comparisons=20)
        assert conf > 0.5
        
        # With model = higher confidence
        learner.is_fitted = True
        conf_with_model = learner._calculate_confidence("img1", comparisons=5)
        learner.is_fitted = False
        conf_without_model = learner._calculate_confidence("img1", comparisons=5)
        assert conf_with_model > conf_without_model
    
    @pytest.mark.asyncio
    async def test_save_load_state(self, test_session, learner, tmp_path):
        """Test saving and loading state"""
        # Add some data
        await learner.add_rating(test_session, "test-image-0", 0.8)
        await learner.add_comparison(test_session, "test-image-1", "test-image-2")
        
        # Train model
        for i in range(5):
            learner.embeddings[f"test-image-{i}"] = np.random.randn(512)
        learner._train_model()
        
        # Save state
        state_file = tmp_path / "state.json"
        learner.save_state(str(state_file))
        
        # Create new learner and load state
        new_learner = PreferenceLearner(embedding_dim=512)
        new_learner.load_state(str(state_file))
        
        assert new_learner.scores == learner.scores
        assert new_learner.comparison_count == learner.comparison_count
        assert new_learner.is_fitted == learner.is_fitted
        assert new_learner.model is not None
    
    @pytest.mark.asyncio
    async def test_save_state_nonexistent_directory(self, learner, tmp_path):
        """Test saving state to non-existent directory"""
        state_file = tmp_path / "nonexistent" / "state.json"
        learner.save_state(str(state_file))
        assert state_file.exists()
    
    @pytest.mark.asyncio
    async def test_load_state_missing_file(self, learner):
        """Test loading state from missing file"""
        # Should not raise error
        learner.load_state("nonexistent_file.json")
        assert learner.scores == {}
        assert learner.comparison_count == {}
    
    @pytest.mark.asyncio
    async def test_elo_calculation_draw(self, learner):
        """Test ELO calculation internals"""
        # Test expected score calculation
        expected = learner._expected_score(1500, 1500)
        assert expected == pytest.approx(0.5)
        
        expected = learner._expected_score(1600, 1400)
        assert expected > 0.5
        
        expected = learner._expected_score(1400, 1600)
        assert expected < 0.5
    
    @pytest.mark.asyncio
    async def test_embedding_storage(self, test_session, learner):
        """Test embedding storage during operations"""
        await learner.add_rating(test_session, "test-image-0", 0.8)
        
        assert "test-image-0" in learner.embeddings
        assert len(learner.embeddings["test-image-0"]) == 512
        assert isinstance(learner.embeddings["test-image-0"], np.ndarray)