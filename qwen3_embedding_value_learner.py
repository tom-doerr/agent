#!/usr/bin/env python3
"""
Qwen3 Vector Embedding Value Learning System with Ridge Regression.

This module implements a text ranking system that:
1. Uses Qwen3 to generate embeddings for text
2. Learns a value function using Ridge regression
3. Can rank any text by its learned value
"""

import json
import numpy as np
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass
import pickle
from pathlib import Path
import logging
from datetime import datetime

from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib

import dspy
from tqdm import tqdm


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RankingExample:
    """A single ranking example with text and score."""
    text: str
    score: float
    metadata: Optional[Dict] = None


class Qwen3Embedder(dspy.Signature):
    """Generate embeddings using Qwen3."""
    text = dspy.InputField(desc="Text to embed")
    embedding = dspy.OutputField(desc="Vector embedding of the text")


class Qwen3EmbeddingValueLearner:
    """Learn to rank text using Qwen3 embeddings and Ridge regression."""
    
    def __init__(
        self,
        model_name: str = "qwen/qwen-2.5-72b-instruct",
        embedding_dim: int = 768,
        ridge_alpha: float = 1.0,
        cache_dir: str = ".qwen3_embeddings",
        api_key: Optional[str] = None,
    ):
        """
        Initialize the embedding value learner.
        
        Args:
            model_name: Qwen model to use for embeddings
            embedding_dim: Dimension of embeddings
            ridge_alpha: Regularization strength for Ridge regression
            cache_dir: Directory to cache embeddings
            api_key: API key for model access
        """
        self.model_name = model_name
        self.embedding_dim = embedding_dim
        self.ridge_alpha = ridge_alpha
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Initialize model
        if api_key:
            self.lm = dspy.LM(
                model=model_name,
                api_key=api_key,
                max_tokens=100,  # Small since we just need embeddings
            )
        else:
            self.lm = dspy.LM(model=model_name)
        
        dspy.configure(lm=self.lm)
        
        # Components
        self.embedder = dspy.ChainOfThought(Qwen3Embedder)
        self.ridge = Ridge(alpha=ridge_alpha)
        self.scaler = StandardScaler()
        self.embedding_cache = {}
        
        # Training data
        self.training_texts = []
        self.training_scores = []
        self.training_embeddings = None
        
    def _get_embedding_vector(self, text: str) -> np.ndarray:
        """
        Get embedding vector for text using Qwen3.
        
        For demonstration, we'll simulate embeddings since Qwen doesn't 
        directly provide embedding vectors. In production, you'd use
        a proper embedding model or extract hidden states.
        """
        # Check cache first
        cache_key = hash(text)
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
        
        # Generate embedding using Qwen3
        # Note: This is a simulation. Real implementation would extract
        # actual embeddings from the model's hidden states
        try:
            # Use the model to generate a representation
            response = self.embedder(text=text)
            
            # Simulate embedding extraction (in practice, you'd extract hidden states)
            # For now, we'll create a deterministic embedding based on text features
            embedding = self._simulate_embedding(text, response.embedding)
            
        except Exception as e:
            logger.warning(f"Failed to get embedding for text, using fallback: {e}")
            embedding = self._fallback_embedding(text)
        
        # Cache the embedding
        self.embedding_cache[cache_key] = embedding
        return embedding
    
    def _simulate_embedding(self, text: str, model_output: str) -> np.ndarray:
        """
        Simulate embedding generation based on text features.
        In production, this would extract actual model embeddings.
        """
        # Create feature vector based on text characteristics
        features = []
        
        # Length features
        features.append(len(text))
        features.append(len(text.split()))
        features.append(len(set(text.split())))  # Unique words
        
        # Character features
        features.append(sum(1 for c in text if c.isupper()))
        features.append(sum(1 for c in text if c.isdigit()))
        features.append(text.count('.'))
        features.append(text.count('!'))
        features.append(text.count('?'))
        
        # Word-level features
        words = text.lower().split()
        if words:
            features.append(np.mean([len(w) for w in words]))
            features.append(np.std([len(w) for w in words]))
        else:
            features.extend([0, 0])
        
        # Sentiment indicators (simple)
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful']
        negative_words = ['bad', 'poor', 'terrible', 'awful', 'horrible']
        features.append(sum(1 for w in words if w in positive_words))
        features.append(sum(1 for w in words if w in negative_words))
        
        # Hash-based features for diversity
        text_hash = hash(text)
        np.random.seed(abs(text_hash) % 2**32)
        hash_features = np.random.randn(self.embedding_dim - len(features))
        
        # Combine all features
        embedding = np.concatenate([features, hash_features])
        
        # Normalize
        embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
        
        return embedding[:self.embedding_dim]
    
    def _fallback_embedding(self, text: str) -> np.ndarray:
        """Generate a simple fallback embedding."""
        # Use a deterministic hash-based embedding
        text_hash = hash(text)
        np.random.seed(abs(text_hash) % 2**32)
        embedding = np.random.randn(self.embedding_dim)
        return embedding / (np.linalg.norm(embedding) + 1e-8)
    
    def add_training_example(self, text: str, score: float, metadata: Optional[Dict] = None):
        """Add a training example."""
        self.training_texts.append(text)
        self.training_scores.append(score)
        
        # Log the example
        logger.info(f"Added training example: score={score:.3f}, text_preview={text[:50]}...")
    
    def add_training_examples(self, examples: List[RankingExample]):
        """Add multiple training examples."""
        for example in examples:
            self.add_training_example(example.text, example.score, example.metadata)
    
    def train(self, validation_split: float = 0.2, cv_folds: int = 5) -> Dict[str, float]:
        """
        Train the Ridge regression model on the embeddings.
        
        Returns:
            Dictionary with training metrics
        """
        if len(self.training_texts) < 2:
            raise ValueError("Need at least 2 training examples")
        
        logger.info(f"Training on {len(self.training_texts)} examples...")
        
        # Generate embeddings for all training texts
        embeddings = []
        for text in tqdm(self.training_texts, desc="Generating embeddings"):
            embedding = self._get_embedding_vector(text)
            embeddings.append(embedding)
        
        self.training_embeddings = np.array(embeddings)
        y = np.array(self.training_scores)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(self.training_embeddings)
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X_scaled, y, test_size=validation_split, random_state=42
        )
        
        # Train Ridge regression
        self.ridge.fit(X_train, y_train)
        
        # Evaluate
        train_pred = self.ridge.predict(X_train)
        val_pred = self.ridge.predict(X_val)
        
        # Cross-validation
        cv_scores = cross_val_score(self.ridge, X_scaled, y, cv=cv_folds, 
                                   scoring='neg_mean_squared_error')
        
        metrics = {
            'train_mse': mean_squared_error(y_train, train_pred),
            'train_r2': r2_score(y_train, train_pred),
            'val_mse': mean_squared_error(y_val, val_pred),
            'val_r2': r2_score(y_val, val_pred),
            'cv_mse_mean': -cv_scores.mean(),
            'cv_mse_std': cv_scores.std(),
            'num_features': self.embedding_dim,
            'ridge_alpha': self.ridge_alpha,
        }
        
        logger.info(f"Training complete. Validation R²: {metrics['val_r2']:.3f}")
        
        return metrics
    
    def predict(self, text: str) -> float:
        """Predict the value/score for a given text."""
        embedding = self._get_embedding_vector(text)
        embedding_scaled = self.scaler.transform(embedding.reshape(1, -1))
        score = self.ridge.predict(embedding_scaled)[0]
        return float(score)
    
    def rank_texts(self, texts: List[str]) -> List[Tuple[str, float]]:
        """
        Rank multiple texts by their predicted scores.
        
        Returns:
            List of (text, score) tuples sorted by score (highest first)
        """
        text_scores = []
        for text in tqdm(texts, desc="Ranking texts"):
            score = self.predict(text)
            text_scores.append((text, score))
        
        # Sort by score (highest first)
        text_scores.sort(key=lambda x: x[1], reverse=True)
        return text_scores
    
    def save_model(self, path: str):
        """Save the trained model and components."""
        model_data = {
            'ridge': self.ridge,
            'scaler': self.scaler,
            'embedding_cache': self.embedding_cache,
            'embedding_dim': self.embedding_dim,
            'ridge_alpha': self.ridge_alpha,
            'training_texts': self.training_texts,
            'training_scores': self.training_scores,
            'training_embeddings': self.training_embeddings,
            'timestamp': datetime.now().isoformat(),
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load a trained model and components."""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.ridge = model_data['ridge']
        self.scaler = model_data['scaler']
        self.embedding_cache = model_data['embedding_cache']
        self.embedding_dim = model_data['embedding_dim']
        self.ridge_alpha = model_data['ridge_alpha']
        self.training_texts = model_data['training_texts']
        self.training_scores = model_data['training_scores']
        self.training_embeddings = model_data['training_embeddings']
        
        logger.info(f"Model loaded from {path}")
    
    def optimize_hyperparameters(
        self, 
        alpha_range: List[float] = [0.01, 0.1, 1.0, 10.0, 100.0],
        cv_folds: int = 5
    ) -> Dict[str, Union[float, Dict]]:
        """
        Optimize Ridge alpha hyperparameter using cross-validation.
        
        Returns:
            Best alpha and performance metrics
        """
        if len(self.training_texts) < cv_folds:
            raise ValueError(f"Need at least {cv_folds} examples for {cv_folds}-fold CV")
        
        # Generate embeddings if not already done
        if self.training_embeddings is None:
            embeddings = []
            for text in tqdm(self.training_texts, desc="Generating embeddings"):
                embedding = self._get_embedding_vector(text)
                embeddings.append(embedding)
            self.training_embeddings = np.array(embeddings)
        
        X_scaled = self.scaler.fit_transform(self.training_embeddings)
        y = np.array(self.training_scores)
        
        best_alpha = None
        best_score = float('-inf')
        results = {}
        
        for alpha in alpha_range:
            ridge = Ridge(alpha=alpha)
            scores = cross_val_score(ridge, X_scaled, y, cv=cv_folds, 
                                   scoring='neg_mean_squared_error')
            mean_score = -scores.mean()
            std_score = scores.std()
            
            results[alpha] = {
                'mean_mse': mean_score,
                'std_mse': std_score,
            }
            
            logger.info(f"Alpha={alpha}: MSE={mean_score:.4f} (±{std_score:.4f})")
            
            if -mean_score > best_score:
                best_score = -mean_score
                best_alpha = alpha
        
        # Retrain with best alpha
        self.ridge_alpha = best_alpha
        self.ridge = Ridge(alpha=best_alpha)
        self.ridge.fit(X_scaled, y)
        
        logger.info(f"Best alpha: {best_alpha}")
        
        return {
            'best_alpha': best_alpha,
            'best_mse': -best_score,
            'all_results': results,
        }


def demo():
    """Demonstrate the Qwen3 embedding value learner."""
    print("Qwen3 Embedding Value Learner Demo")
    print("=" * 50)
    
    # Initialize learner
    learner = Qwen3EmbeddingValueLearner(
        embedding_dim=128,  # Smaller for demo
        ridge_alpha=1.0,
    )
    
    # Add training examples (quality scores from 0-10)
    training_examples = [
        RankingExample("This is an excellent product! Highly recommend.", 9.5),
        RankingExample("Great quality and fast shipping. Very satisfied.", 8.7),
        RankingExample("Good value for money. Works as expected.", 7.2),
        RankingExample("Average product. Nothing special but does the job.", 5.5),
        RankingExample("Disappointed. Quality is poor and overpriced.", 2.3),
        RankingExample("Terrible experience. Product broke after one day.", 1.0),
        RankingExample("Outstanding service and amazing product quality!", 9.8),
        RankingExample("Not bad, but there are better options available.", 4.5),
        RankingExample("Exceeded my expectations. Will buy again!", 9.0),
        RankingExample("Mediocre at best. Many issues with functionality.", 3.5),
    ]
    
    learner.add_training_examples(training_examples)
    
    # Train the model
    print("\nTraining Ridge regression model...")
    metrics = learner.train(validation_split=0.3)
    
    print("\nTraining Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value:.4f}")
    
    # Test ranking
    test_texts = [
        "This product is absolutely fantastic!",
        "Worst purchase ever. Complete waste of money.",
        "It's okay, nothing to write home about.",
        "Incredible quality and great customer service!",
        "Broken on arrival. Very disappointed.",
    ]
    
    print("\nRanking test texts:")
    rankings = learner.rank_texts(test_texts)
    
    for i, (text, score) in enumerate(rankings, 1):
        print(f"{i}. Score: {score:.3f} - {text}")
    
    # Optimize hyperparameters
    print("\nOptimizing Ridge alpha parameter...")
    opt_results = learner.optimize_hyperparameters()
    print(f"Best alpha: {opt_results['best_alpha']}")
    print(f"Best MSE: {opt_results['best_mse']:.4f}")
    
    # Save model
    learner.save_model("qwen3_ranking_model.pkl")
    print("\nModel saved successfully!")


if __name__ == "__main__":
    demo()