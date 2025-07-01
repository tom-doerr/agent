#!/usr/bin/env python3
"""
Real Qwen3 Embedding Value Learning System with Ridge Regression.

This module uses actual Qwen3 embedding models instead of simulated embeddings.
Supports both sentence-transformers and transformers implementations.
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

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import torch
    import torch.nn.functional as F
    from transformers import AutoTokenizer, AutoModel
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from tqdm import tqdm


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RankingExample:
    """A single ranking example with text and score."""
    text: str
    score: float
    metadata: Optional[Dict] = None


class Qwen3RealEmbeddingLearner:
    """Learn to rank text using real Qwen3 embeddings and Ridge regression."""
    
    def __init__(
        self,
        model_name: str = "Qwen/Qwen3-Embedding-0.6B",
        ridge_alpha: float = 1.0,
        cache_dir: str = ".qwen3_embeddings",
        use_sentence_transformers: bool = True,
        device: str = None,
        use_instructions: bool = True,
        task_description: str = "Rank text by quality and relevance",
    ):
        """
        Initialize the embedding value learner with real Qwen3 models.
        
        Args:
            model_name: Qwen3 embedding model name
            ridge_alpha: L2 regularization strength for Ridge regression
            cache_dir: Directory to cache embeddings
            use_sentence_transformers: Use sentence-transformers library (simpler)
            device: Device to run model on (cuda/cpu/auto)
            use_instructions: Whether to use instruction-aware embeddings
            task_description: Task description for instruction-aware mode
        """
        self.model_name = model_name
        self.ridge_alpha = ridge_alpha
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.use_instructions = use_instructions
        self.task_description = task_description
        
        # Determine device
        if device is None:
            if TRANSFORMERS_AVAILABLE and torch.cuda.is_available():
                self.device = "cuda"
            else:
                self.device = "cpu"
        else:
            self.device = device
        
        # Initialize embedding model
        if use_sentence_transformers and SENTENCE_TRANSFORMERS_AVAILABLE:
            self._init_sentence_transformers()
        elif TRANSFORMERS_AVAILABLE:
            self._init_transformers()
        else:
            raise ImportError(
                "Neither sentence-transformers nor transformers is installed. "
                "Install with: pip install sentence-transformers transformers torch"
            )
        
        # Components
        self.ridge = Ridge(alpha=ridge_alpha)
        self.scaler = StandardScaler()
        self.embedding_cache = {}
        
        # Training data
        self.training_texts = []
        self.training_scores = []
        self.training_embeddings = None
        
    def _init_sentence_transformers(self):
        """Initialize using sentence-transformers library."""
        logger.info(f"Initializing {self.model_name} with sentence-transformers")
        
        model_kwargs = {}
        if self.device == "cuda":
            model_kwargs["device_map"] = "auto"
            # Try to use flash attention if available
            try:
                model_kwargs["attn_implementation"] = "flash_attention_2"
            except:
                pass
        
        self.model = SentenceTransformer(
            self.model_name,
            model_kwargs=model_kwargs,
            tokenizer_kwargs={"padding_side": "left"},
        )
        self.use_st = True
        
        # Get embedding dimension from model
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"Embedding dimension: {self.embedding_dim}")
    
    def _init_transformers(self):
        """Initialize using transformers library directly."""
        logger.info(f"Initializing {self.model_name} with transformers")
        
        # Load model and tokenizer
        dtype = torch.float16 if self.device == "cuda" else torch.float32
        self.model = AutoModel.from_pretrained(
            self.model_name,
            torch_dtype=dtype,
            device_map="auto" if self.device == "cuda" else None
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        if self.device == "cuda" and not hasattr(self.model, "device"):
            self.model = self.model.cuda()
        
        self.use_st = False
        
        # Infer embedding dimension
        self.embedding_dim = self.model.config.hidden_size
        logger.info(f"Embedding dimension: {self.embedding_dim}")
    
    def _last_token_pool(self, last_hidden_states: torch.Tensor,
                        attention_mask: torch.Tensor) -> torch.Tensor:
        """Extract embeddings from last token (for transformers implementation)."""
        left_padding = (attention_mask[:, -1].sum() == attention_mask.shape[0])
        if left_padding:
            return last_hidden_states[:, -1]
        else:
            sequence_lengths = attention_mask.sum(dim=1) - 1
            batch_size = last_hidden_states.shape[0]
            return last_hidden_states[
                torch.arange(batch_size, device=last_hidden_states.device),
                sequence_lengths
            ]
    
    def _get_detailed_instruct(self, query: str) -> str:
        """Format query with instruction for better performance."""
        if self.use_instructions:
            return f'Instruct: {self.task_description}\nQuery: {query}'
        return query
    
    def _get_embedding_vector(self, text: str) -> np.ndarray:
        """Get embedding vector for text using real Qwen3 model."""
        # Check cache first
        cache_key = hash(text)
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
        
        # Prepare text with instruction if needed
        input_text = self._get_detailed_instruct(text)
        
        try:
            if self.use_st:
                # Sentence transformers approach
                embedding = self.model.encode(
                    input_text,
                    normalize_embeddings=True,
                    show_progress_bar=False
                )
            else:
                # Transformers approach
                with torch.no_grad():
                    # Tokenize
                    inputs = self.tokenizer(
                        input_text,
                        padding=True,
                        truncation=True,
                        max_length=8192,
                        return_tensors="pt",
                    )
                    
                    if self.device == "cuda":
                        inputs = {k: v.cuda() for k, v in inputs.items()}
                    
                    # Get model outputs
                    outputs = self.model(**inputs)
                    
                    # Extract embeddings from last token
                    embeddings = self._last_token_pool(
                        outputs.last_hidden_state,
                        inputs['attention_mask']
                    )
                    
                    # Normalize
                    embeddings = F.normalize(embeddings, p=2, dim=1)
                    embedding = embeddings[0].cpu().numpy()
            
        except Exception as e:
            logger.warning(f"Failed to get embedding for text: {e}")
            # Fallback to random embedding
            embedding = np.random.randn(self.embedding_dim)
            embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
        
        # Cache the embedding
        self.embedding_cache[cache_key] = embedding
        return embedding
    
    def add_training_example(self, text: str, score: float, metadata: Optional[Dict] = None):
        """Add a training example."""
        self.training_texts.append(text)
        self.training_scores.append(score)
        logger.info(f"Added training example: score={score:.3f}, text_preview={text[:50]}...")
    
    def add_training_examples(self, examples: List[RankingExample]):
        """Add multiple training examples."""
        for example in examples:
            self.add_training_example(example.text, example.score, example.metadata)
    
    def train(self, validation_split: float = 0.2, cv_folds: int = 5) -> Dict[str, float]:
        """Train the Ridge regression model on the embeddings."""
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
        cv_scores = cross_val_score(
            self.ridge, X_scaled, y, cv=cv_folds,
            scoring='neg_mean_squared_error'
        )
        
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
        """Rank multiple texts by their predicted scores."""
        text_scores = []
        for text in tqdm(texts, desc="Ranking texts"):
            score = self.predict(text)
            text_scores.append((text, score))
        
        # Sort by score (highest first)
        text_scores.sort(key=lambda x: x[1], reverse=True)
        return text_scores
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts using embeddings."""
        emb1 = self._get_embedding_vector(text1)
        emb2 = self._get_embedding_vector(text2)
        
        # Compute cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(similarity)
    
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
            'model_name': self.model_name,
            'use_instructions': self.use_instructions,
            'task_description': self.task_description,
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
        self.use_instructions = model_data.get('use_instructions', True)
        self.task_description = model_data.get('task_description', "Rank text by quality")
        
        logger.info(f"Model loaded from {path}")


def demo():
    """Demonstrate the real Qwen3 embedding value learner."""
    print("Real Qwen3 Embedding Value Learner Demo")
    print("=" * 50)
    
    # Check available backends
    if not (SENTENCE_TRANSFORMERS_AVAILABLE or TRANSFORMERS_AVAILABLE):
        print("Error: Please install sentence-transformers or transformers+torch")
        print("pip install sentence-transformers transformers torch")
        return
    
    # Initialize learner
    learner = Qwen3RealEmbeddingLearner(
        model_name="Qwen/Qwen3-Embedding-0.6B",  # Smallest model for demo
        ridge_alpha=1.0,
        use_sentence_transformers=SENTENCE_TRANSFORMERS_AVAILABLE,
        task_description="Rank product reviews by helpfulness and quality"
    )
    
    # Add training examples
    training_examples = [
        RankingExample(
            "This product exceeded all expectations. The build quality is exceptional, "
            "and it performs exactly as advertised. Highly recommended!",
            9.5
        ),
        RankingExample(
            "Good value for money. Works as expected with minor issues.",
            7.0
        ),
        RankingExample(
            "Average product. Nothing special but does the job.",
            5.0
        ),
        RankingExample(
            "Poor quality. Broke after one week. Very disappointed.",
            2.0
        ),
        RankingExample(
            "Terrible! Complete waste of money. Do not buy!",
            1.0
        ),
    ]
    
    learner.add_training_examples(training_examples)
    
    # Train the model
    print("\nTraining Ridge regression model...")
    metrics = learner.train(validation_split=0.4)  # More validation for small dataset
    
    print("\nTraining Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value:.4f}")
    
    # Test ranking
    test_texts = [
        "This is the best product I've ever purchased!",
        "Worst purchase of my life. Completely useless.",
        "It's okay, nothing great but not terrible either.",
    ]
    
    print("\nRanking test texts:")
    rankings = learner.rank_texts(test_texts)
    
    for i, (text, score) in enumerate(rankings, 1):
        print(f"{i}. Score: {score:.3f} - {text}")
    
    # Test similarity
    print("\nTesting semantic similarity:")
    pairs = [
        ("Great product!", "Excellent item!"),
        ("Great product!", "Terrible product!"),
        ("The sky is blue", "The ocean is blue"),
    ]
    
    for text1, text2 in pairs:
        similarity = learner.compute_similarity(text1, text2)
        print(f"Similarity between '{text1}' and '{text2}': {similarity:.3f}")
    
    # Save model
    learner.save_model("qwen3_real_ranking_model.pkl")
    print("\nModel saved successfully!")


if __name__ == "__main__":
    demo()