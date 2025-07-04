import numpy as np
from typing import List, Dict, Tuple, Optional
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from collections import defaultdict
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import ImageRecord, PreferenceRecord, ComparisonRecord
from models import PreferencePrediction


class PreferenceLearner:
    """Learn user preferences from image comparisons and ratings with sample efficiency."""
    
    def __init__(self, embedding_dim: int = 512):
        self.embedding_dim = embedding_dim
        # Use higher regularization for better generalization with few samples
        self.model = Ridge(alpha=10.0)
        self.scaler = StandardScaler()
        self.is_fitted = False
        
        # Store preference data
        self.embeddings: Dict[str, np.ndarray] = {}
        self.scores: Dict[str, float] = defaultdict(float)
        self.comparison_count: Dict[str, int] = defaultdict(int)
        
        # Sample efficiency improvements
        self.uncertainty_weight = 2.0  # Boost learning from uncertain predictions
        self.active_learning_threshold = 0.5  # Focus on uncertain regions
        
        # Bayesian-inspired priors
        self.prior_mean = 0.5
        self.prior_confidence = 0.1
        
    async def add_comparison(
        self,
        session: AsyncSession,
        winner_id: str,
        loser_id: str,
        user_id: str = "default"
    ):
        """Add a pairwise comparison to the preference data."""
        
        # Update ELO-style scores with adaptive K-factor for sample efficiency
        winner_score = self.scores.get(winner_id, 1000)
        loser_score = self.scores.get(loser_id, 1000)
        
        # Expected scores
        expected_winner = 1 / (1 + 10 ** ((loser_score - winner_score) / 400))
        expected_loser = 1 - expected_winner
        
        # Adaptive K-factor: higher for new items (more learning from each sample)
        winner_comparisons = self.comparison_count[winner_id]
        loser_comparisons = self.comparison_count[loser_id]
        
        # Higher K for items with fewer comparisons
        k_winner = 64 / (1 + winner_comparisons / 5)
        k_loser = 64 / (1 + loser_comparisons / 5)
        
        self.scores[winner_id] = winner_score + k_winner * (1 - expected_winner)
        self.scores[loser_id] = loser_score + k_loser * (0 - expected_loser)
        
        # Update comparison counts
        self.comparison_count[winner_id] += 1
        self.comparison_count[loser_id] += 1
        
        # Store in database
        comparison = ComparisonRecord(
            id=f"{winner_id}_{loser_id}_{datetime.utcnow().timestamp()}",
            user_id=user_id,
            winner_id=winner_id,
            loser_id=loser_id
        )
        session.add(comparison)
        await session.commit()
        
        # Retrain model if we have enough data (lowered threshold for sample efficiency)
        if len(self.scores) >= 3:
            await self._retrain_model(session)
    
    async def add_rating(
        self,
        session: AsyncSession,
        image_id: str,
        rating: float,
        user_id: str = "default"
    ):
        """Add an absolute rating for an image."""
        
        # Update score with weighted average
        current_score = self.scores.get(image_id, 0.5)
        count = self.comparison_count[image_id]
        
        # Weight new rating based on how many comparisons we've seen
        weight = min(0.5, 1 / (count + 1))
        self.scores[image_id] = current_score * (1 - weight) + rating * weight
        self.comparison_count[image_id] += 1
        
        # Store in database
        preference = PreferenceRecord(
            id=f"{image_id}_{datetime.utcnow().timestamp()}",
            user_id=user_id,
            image_id=image_id,
            score=rating,
            feedback_type="rating"
        )
        session.add(preference)
        await session.commit()
        
        # Retrain model
        if len(self.scores) >= 5:
            await self._retrain_model(session)
    
    async def predict_preference(
        self,
        session: AsyncSession,
        image_id: str
    ) -> PreferencePrediction:
        """Predict how much the user will like an image."""
        
        # Get image embedding
        image = await session.get(ImageRecord, image_id)
        if not image:
            raise ValueError(f"Image {image_id} not found")
        
        embedding = np.array(image.latent_vector)
        
        if not self.is_fitted:
            # Return average score if model not trained
            avg_score = np.mean(list(self.scores.values())) if self.scores else 0.5
            return PreferencePrediction(
                image_id=image_id,
                predicted_score=avg_score,
                confidence=0.1
            )
        
        # Predict using trained model
        embedding_scaled = self.scaler.transform(embedding.reshape(1, -1))
        predicted_score = self.model.predict(embedding_scaled)[0]
        
        # Clip to valid range
        predicted_score = np.clip(predicted_score, 0, 1)
        
        # Calculate confidence based on similar images seen
        confidence = self._calculate_confidence(embedding)
        
        return PreferencePrediction(
            image_id=image_id,
            predicted_score=float(predicted_score),
            confidence=float(confidence)
        )
    
    async def generate_optimal_prompt_direction(
        self,
        session: AsyncSession,
        base_embedding: np.ndarray
    ) -> np.ndarray:
        """Generate a direction in embedding space that should increase preference."""
        
        if not self.is_fitted:
            # Return random direction if not fitted
            direction = np.random.randn(self.embedding_dim)
            return direction / np.linalg.norm(direction)
        
        # Use gradient of the preference model
        # For Ridge regression, the gradient is simply the coefficients
        direction = self.model.coef_
        
        # Normalize
        direction = direction / np.linalg.norm(direction)
        
        return direction
    
    async def get_ranked_images(
        self,
        session: AsyncSession,
        image_ids: List[str]
    ) -> List[Tuple[str, float]]:
        """Rank a list of images by predicted preference."""
        
        predictions = []
        
        for image_id in image_ids:
            try:
                pred = await self.predict_preference(session, image_id)
                predictions.append((image_id, pred.predicted_score))
            except ValueError:
                # Image not found, use default score
                predictions.append((image_id, 0.5))
        
        # Sort by predicted score (descending)
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        return predictions
    
    async def _retrain_model(self, session: AsyncSession):
        """Retrain the preference model with all available data."""
        
        # Get all images with scores
        result = await session.execute(
            select(ImageRecord).where(ImageRecord.id.in_(self.scores.keys()))
        )
        images = result.scalars().all()
        
        if len(images) < 3:  # Lowered threshold for sample efficiency
            return
        
        # Prepare training data
        X = []
        y = []
        
        for image in images:
            embedding = np.array(image.latent_vector)
            score = self.scores[image.id]
            
            X.append(embedding)
            y.append(score)
        
        X = np.array(X)
        y = np.array(y)
        
        # Normalize scores to [0, 1]
        y_min, y_max = y.min(), y.max()
        if y_max > y_min:
            y = (y - y_min) / (y_max - y_min)
        else:
            y = np.ones_like(y) * 0.5
        
        # Fit scaler and model
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_fitted = True
        
        # Store embeddings for confidence calculation
        self.embeddings = {img.id: np.array(img.latent_vector) for img in images}
    
    def _calculate_confidence(self, embedding: np.ndarray) -> float:
        """Calculate confidence based on similarity to training data."""
        
        if not self.embeddings:
            return 0.1
        
        # Calculate distances to all training embeddings
        distances = []
        for train_embedding in self.embeddings.values():
            dist = np.linalg.norm(embedding - train_embedding)
            distances.append(dist)
        
        # Use inverse of minimum distance as confidence
        min_dist = min(distances)
        confidence = 1 / (1 + min_dist)
        
        # Scale by amount of training data
        data_factor = min(1.0, len(self.embeddings) / 20)
        confidence *= data_factor
        
        return float(np.clip(confidence, 0.1, 0.9))
    
    async def suggest_comparison_pair(
        self,
        session: AsyncSession,
        candidate_ids: List[str]
    ) -> Optional[Tuple[str, str]]:
        """Suggest the most informative pair for comparison using active learning."""
        
        if len(candidate_ids) < 2:
            return None
        
        # Calculate uncertainty for each pair
        best_pair = None
        max_info_gain = 0
        
        for i in range(len(candidate_ids)):
            for j in range(i + 1, len(candidate_ids)):
                id1, id2 = candidate_ids[i], candidate_ids[j]
                
                # Get predictions
                try:
                    pred1 = await self.predict_preference(session, id1)
                    pred2 = await self.predict_preference(session, id2)
                    
                    # Information gain is highest when:
                    # 1. Predictions are close (hard to distinguish)
                    # 2. Confidence is low (uncertain region)
                    score_diff = abs(pred1.predicted_score - pred2.predicted_score)
                    avg_confidence = (pred1.confidence + pred2.confidence) / 2
                    
                    # Prioritize pairs with similar scores but low confidence
                    info_gain = (1 - score_diff) * (1 - avg_confidence)
                    
                    if info_gain > max_info_gain:
                        max_info_gain = info_gain
                        best_pair = (id1, id2)
                        
                except:
                    # If prediction fails, this pair might be informative
                    best_pair = (id1, id2)
                    max_info_gain = 0.5
        
        return best_pair
    
    def save_state(self, filepath: str):
        """Save the current state of the preference learner."""
        
        state = {
            "scores": dict(self.scores),
            "comparison_count": dict(self.comparison_count),
            "is_fitted": self.is_fitted,
            "model_coef": self.model.coef_.tolist() if self.is_fitted else None,
            "model_intercept": float(self.model.intercept_) if self.is_fitted else None,
            "scaler_mean": self.scaler.mean_.tolist() if self.is_fitted else None,
            "scaler_scale": self.scaler.scale_.tolist() if self.is_fitted else None
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f)
    
    def load_state(self, filepath: str):
        """Load a saved state."""
        
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        self.scores = defaultdict(float, state["scores"])
        self.comparison_count = defaultdict(int, state["comparison_count"])
        self.is_fitted = state["is_fitted"]
        
        if self.is_fitted:
            self.model.coef_ = np.array(state["model_coef"])
            self.model.intercept_ = state["model_intercept"]
            self.scaler.mean_ = np.array(state["scaler_mean"])
            self.scaler.scale_ = np.array(state["scaler_scale"])