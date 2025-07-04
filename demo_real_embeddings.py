#!/usr/bin/env python3
"""Demo using real Qwen3 embeddings (requires transformers)"""

from qwen3_embedding_real import Qwen3RealEmbeddingLearner, RankingExample

# Create learner with real embeddings
learner = Qwen3RealEmbeddingLearner(
    model_name="Qwen/Qwen3-Embedding-0.6B",  # Or use a smaller model
    ridge_alpha=1.0,
    cache_dir=".qwen3_cache"
)

# Training data - can be any scored items
data = [
    RankingExample("This product is amazing! Best purchase ever.", score=1.0),
    RankingExample("Good quality, reasonable price.", score=0.7),
    RankingExample("It's okay, nothing special.", score=0.5),
    RankingExample("Broken on arrival. Very disappointed.", score=0.1),
]

# Train
print("Training on examples...")
metrics = learner.fit(data)
print(f"R² score: {metrics['r2']:.3f}")

# Predict on new reviews
new_reviews = [
    "Excellent quality, highly recommend!",
    "Terrible experience, would not buy again.",
    "Average product, works as expected.",
]

print("\nValue predictions:")
for review in new_reviews:
    value = learner.predict_value(review)
    print(f"{value:.3f} - {review[:50]}...")

# You can also get embeddings directly
embedding = learner.get_embedding("Sample text")
print(f"\nEmbedding shape: {embedding.shape}")