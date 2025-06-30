# Qwen3 Embedding Value Learner Documentation

## Overview

The Qwen3 Embedding Value Learner is a sophisticated text ranking system that combines the power of Qwen3 language models with Ridge regression to learn value functions for text. This system enables you to:

- Generate high-quality embeddings for any text using Qwen3
- Learn to predict scores/values for texts based on training examples
- Rank texts by their learned values
- Optimize the model using cross-validation
- Save and load trained models for production use

## Table of Contents

1. [Architecture](#architecture)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [API Reference](#api-reference)
5. [Training Pipeline](#training-pipeline)
6. [Model Optimization](#model-optimization)
7. [Production Usage](#production-usage)
8. [Performance Considerations](#performance-considerations)
9. [Examples](#examples)
10. [Troubleshooting](#troubleshooting)

## Architecture

### System Components

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Input Text    │────▶│ Qwen3 Embedder   │────▶│ Ridge Regressor │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │                           │
                               ▼                           ▼
                        ┌──────────────┐           ┌──────────────┐
                        │  Embedding   │           │ Predicted    │
                        │    Cache     │           │   Score      │
                        └──────────────┘           └──────────────┘
```

### Key Features

1. **Embedding Generation**: Uses Qwen3 to create dense vector representations of text
2. **Value Learning**: Ridge regression learns to map embeddings to scores
3. **Caching**: Embeddings are cached to avoid redundant computation
4. **Hyperparameter Optimization**: Built-in cross-validation for finding optimal Ridge alpha
5. **Model Persistence**: Save and load trained models with all components

## Installation

### Requirements

```bash
pip install dspy scikit-learn numpy joblib tqdm
```

### Optional Dependencies

For using OpenRouter or other API providers:
```bash
pip install openai  # For API access
```

## Quick Start

### Basic Usage

```python
from qwen3_embedding_value_learner import Qwen3EmbeddingValueLearner, RankingExample

# Initialize the learner
learner = Qwen3EmbeddingValueLearner(
    embedding_dim=768,
    ridge_alpha=1.0,
    api_key="your-api-key"  # Optional
)

# Add training examples
learner.add_training_example("This product is excellent!", 9.5)
learner.add_training_example("Poor quality, disappointed", 2.0)

# Or add multiple at once
examples = [
    RankingExample("Great value for money", 8.0),
    RankingExample("Average product", 5.0),
]
learner.add_training_examples(examples)

# Train the model
metrics = learner.train(validation_split=0.2)
print(f"Validation R²: {metrics['val_r2']:.3f}")

# Make predictions
score = learner.predict("Is this product worth buying?")
print(f"Predicted score: {score:.2f}")

# Rank multiple texts
texts = ["Amazing!", "Terrible!", "Not bad"]
rankings = learner.rank_texts(texts)
for text, score in rankings:
    print(f"{score:.2f}: {text}")
```

## API Reference

### Qwen3EmbeddingValueLearner

The main class for the embedding value learning system.

#### Constructor

```python
Qwen3EmbeddingValueLearner(
    model_name: str = "qwen/qwen-2.5-72b-instruct",
    embedding_dim: int = 768,
    ridge_alpha: float = 1.0,
    cache_dir: str = ".qwen3_embeddings",
    api_key: Optional[str] = None,
)
```

**Parameters:**
- `model_name`: The Qwen model to use for embeddings
- `embedding_dim`: Dimension of the embedding vectors
- `ridge_alpha`: L2 regularization strength for Ridge regression
- `cache_dir`: Directory to cache embeddings
- `api_key`: API key for model access (if required)

#### Methods

##### add_training_example
```python
add_training_example(text: str, score: float, metadata: Optional[Dict] = None)
```
Add a single training example.

**Parameters:**
- `text`: The text to learn from
- `score`: The target score/value for this text
- `metadata`: Optional metadata dictionary

##### add_training_examples
```python
add_training_examples(examples: List[RankingExample])
```
Add multiple training examples at once.

##### train
```python
train(validation_split: float = 0.2, cv_folds: int = 5) -> Dict[str, float]
```
Train the Ridge regression model on the embeddings.

**Parameters:**
- `validation_split`: Fraction of data to use for validation
- `cv_folds`: Number of cross-validation folds

**Returns:**
Dictionary containing training metrics:
- `train_mse`: Training mean squared error
- `train_r2`: Training R² score
- `val_mse`: Validation mean squared error
- `val_r2`: Validation R² score
- `cv_mse_mean`: Mean cross-validation MSE
- `cv_mse_std`: Standard deviation of CV MSE

##### predict
```python
predict(text: str) -> float
```
Predict the score for a given text.

##### rank_texts
```python
rank_texts(texts: List[str]) -> List[Tuple[str, float]]
```
Rank multiple texts by their predicted scores.

**Returns:**
List of (text, score) tuples sorted by score (highest first)

##### optimize_hyperparameters
```python
optimize_hyperparameters(
    alpha_range: List[float] = [0.01, 0.1, 1.0, 10.0, 100.0],
    cv_folds: int = 5
) -> Dict[str, Union[float, Dict]]
```
Find the optimal Ridge alpha parameter using cross-validation.

##### save_model / load_model
```python
save_model(path: str)
load_model(path: str)
```
Save or load the complete trained model.

### RankingExample

A dataclass for training examples.

```python
@dataclass
class RankingExample:
    text: str
    score: float
    metadata: Optional[Dict] = None
```

## Training Pipeline

### 1. Data Preparation

Prepare your training data with texts and their corresponding scores:

```python
# Example: Product reviews with ratings
training_data = [
    ("This product exceeded all my expectations!", 9.5),
    ("Good quality, fair price", 7.0),
    ("Not worth the money", 3.0),
    # ... more examples
]

for text, score in training_data:
    learner.add_training_example(text, score)
```

### 2. Embedding Generation

The system automatically generates embeddings for all training texts:
- Embeddings are cached to avoid recomputation
- Uses Qwen3 to create semantically rich representations
- Vectors are normalized to unit length

### 3. Model Training

Train the Ridge regression model:

```python
metrics = learner.train(
    validation_split=0.2,  # 80/20 train/validation split
    cv_folds=5            # 5-fold cross-validation
)
```

### 4. Evaluation

Evaluate model performance using the returned metrics:

```python
print(f"Training R²: {metrics['train_r2']:.3f}")
print(f"Validation R²: {metrics['val_r2']:.3f}")
print(f"CV MSE: {metrics['cv_mse_mean']:.3f} ± {metrics['cv_mse_std']:.3f}")
```

## Model Optimization

### Hyperparameter Tuning

Find the optimal Ridge alpha parameter:

```python
# Define search range
alpha_range = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]

# Run optimization
results = learner.optimize_hyperparameters(
    alpha_range=alpha_range,
    cv_folds=5
)

print(f"Best alpha: {results['best_alpha']}")
print(f"Best MSE: {results['best_mse']:.4f}")

# Model is automatically retrained with best alpha
```

### Cross-Validation Strategy

The system uses k-fold cross-validation to:
- Avoid overfitting
- Get robust performance estimates
- Select optimal hyperparameters

## Production Usage

### Model Deployment

```python
# Train your model
learner = Qwen3EmbeddingValueLearner(embedding_dim=768)
# ... add training data and train ...

# Save the trained model
learner.save_model("models/ranking_model_v1.pkl")

# In production:
production_learner = Qwen3EmbeddingValueLearner(embedding_dim=768)
production_learner.load_model("models/ranking_model_v1.pkl")

# Use for predictions
score = production_learner.predict("New text to rank")
```

### Batch Processing

For efficient batch processing:

```python
# Process many texts at once
texts_to_rank = load_texts_from_database()  # Your data source

# Rank all texts (uses caching and progress bar)
rankings = learner.rank_texts(texts_to_rank)

# Save results
with open("rankings.json", "w") as f:
    json.dump([{"text": t, "score": s} for t, s in rankings], f)
```

### API Integration

Example Flask API:

```python
from flask import Flask, request, jsonify

app = Flask(__name__)
learner = Qwen3EmbeddingValueLearner()
learner.load_model("model.pkl")

@app.route("/predict", methods=["POST"])
def predict():
    text = request.json["text"]
    score = learner.predict(text)
    return jsonify({"text": text, "score": score})

@app.route("/rank", methods=["POST"])
def rank():
    texts = request.json["texts"]
    rankings = learner.rank_texts(texts)
    return jsonify([{"text": t, "score": s} for t, s in rankings])
```

## Performance Considerations

### Embedding Caching

- Embeddings are cached in memory by default
- Cache persists with saved models
- Clear cache if memory is a concern: `learner.embedding_cache.clear()`

### Batch Size Recommendations

- For training: Add all examples before calling `train()`
- For inference: Process in batches of 100-1000 texts
- Monitor memory usage with large datasets

### Optimization Tips

1. **Embedding Dimension**: 
   - Larger dimensions (768-1024) for complex tasks
   - Smaller dimensions (128-256) for simple ranking

2. **Ridge Alpha**:
   - Higher values (10-100) for noisy data
   - Lower values (0.01-1) for clean, consistent data

3. **Training Data**:
   - Minimum 50-100 examples recommended
   - Balanced score distribution improves performance

## Examples

### Example 1: Customer Review Ranking

```python
# Initialize learner for review ranking
review_ranker = Qwen3EmbeddingValueLearner(
    embedding_dim=512,
    ridge_alpha=10.0  # Higher alpha for noisy review data
)

# Load training data from CSV
import pandas as pd
df = pd.read_csv("reviews.csv")

# Add training examples
for _, row in df.iterrows():
    review_ranker.add_training_example(
        text=row["review_text"],
        score=row["rating"],  # 1-5 stars
        metadata={"product_id": row["product_id"]}
    )

# Train and optimize
review_ranker.optimize_hyperparameters()
metrics = review_ranker.train()

# Rank new reviews
new_reviews = [
    "This product changed my life!",
    "Worst purchase ever made.",
    "It's okay, does what it says."
]

rankings = review_ranker.rank_texts(new_reviews)
```

### Example 2: Content Quality Scoring

```python
# Content quality scorer
content_scorer = Qwen3EmbeddingValueLearner(
    embedding_dim=768,
    model_name="qwen/qwen-2.5-72b-instruct"
)

# Training data: articles with quality scores
quality_examples = [
    RankingExample(
        text="Well-researched article with citations...",
        score=9.0,
        metadata={"type": "academic"}
    ),
    RankingExample(
        text="Clickbait title with no substance...",
        score=2.0,
        metadata={"type": "clickbait"}
    ),
    # ... more examples
]

content_scorer.add_training_examples(quality_examples)
content_scorer.train()

# Score new content
article = load_article("new_article.txt")
quality_score = content_scorer.predict(article)

if quality_score > 7.0:
    publish_article(article)
else:
    send_for_review(article)
```

### Example 3: Search Result Ranking

```python
# Search result ranker
search_ranker = Qwen3EmbeddingValueLearner(embedding_dim=256)

# Train on click-through data
for query, results in search_log:
    for result in results:
        # Score based on user engagement
        if result["clicked"]:
            score = 5.0 + result["time_on_page"] / 60  # Bonus for engagement
        else:
            score = 1.0
        
        search_ranker.add_training_example(
            text=f"{query} | {result['title']} | {result['snippet']}",
            score=score
        )

search_ranker.train()

# Rank search results
def rank_search_results(query, results):
    texts = [f"{query} | {r['title']} | {r['snippet']}" for r in results]
    rankings = search_ranker.rank_texts(texts)
    
    # Reorder results by score
    ranked_results = []
    for text, score in rankings:
        # Extract original result
        idx = texts.index(text)
        ranked_results.append(results[idx])
    
    return ranked_results
```

## Troubleshooting

### Common Issues

#### 1. Low Validation R² Score

**Symptoms**: `val_r2` < 0.3

**Solutions**:
- Add more diverse training examples
- Try different embedding dimensions
- Optimize Ridge alpha parameter
- Check for inconsistent labels in training data

#### 2. Memory Issues with Large Datasets

**Symptoms**: Out of memory errors

**Solutions**:
```python
# Process in smaller batches
def process_large_dataset(texts, batch_size=1000):
    all_rankings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        rankings = learner.rank_texts(batch)
        all_rankings.extend(rankings)
        # Clear cache periodically
        if i % 5000 == 0:
            learner.embedding_cache.clear()
    return all_rankings
```

#### 3. Slow Embedding Generation

**Symptoms**: Training or inference takes too long

**Solutions**:
- Use smaller embedding dimensions
- Implement batch processing for API calls
- Consider using a local model for embeddings
- Pre-compute embeddings for known texts

#### 4. API Rate Limits

**Symptoms**: API errors during embedding generation

**Solutions**:
```python
import time

class RateLimitedLearner(Qwen3EmbeddingValueLearner):
    def _get_embedding_vector(self, text):
        time.sleep(0.1)  # Rate limit to 10 requests/second
        return super()._get_embedding_vector(text)
```

### Debug Mode

Enable detailed logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("qwen3_embedding_value_learner")

# Now all operations will log detailed information
```

### Validation Techniques

1. **Score Distribution Analysis**:
```python
import matplotlib.pyplot as plt

plt.hist(learner.training_scores, bins=20)
plt.xlabel("Score")
plt.ylabel("Count")
plt.title("Training Score Distribution")
plt.show()
```

2. **Prediction vs Actual Plot**:
```python
# After training
predictions = [learner.predict(text) for text in validation_texts]
plt.scatter(validation_scores, predictions)
plt.xlabel("Actual Score")
plt.ylabel("Predicted Score")
plt.plot([0, 10], [0, 10], 'r--')  # Perfect prediction line
plt.show()
```

3. **Feature Importance** (for debugging):
```python
# Check which embedding dimensions are most important
importance = abs(learner.ridge.coef_)
top_features = np.argsort(importance)[-10:]
print(f"Most important embedding dimensions: {top_features}")
```

## Advanced Topics

### Custom Embedding Functions

Override the embedding generation for custom behavior:

```python
class CustomEmbeddingLearner(Qwen3EmbeddingValueLearner):
    def _get_embedding_vector(self, text):
        # Your custom embedding logic
        if self.use_custom_features:
            features = extract_custom_features(text)
            base_embedding = super()._get_embedding_vector(text)
            return np.concatenate([base_embedding, features])
        return super()._get_embedding_vector(text)
```

### Ensemble Models

Combine multiple learners:

```python
class EnsembleLearner:
    def __init__(self, learners):
        self.learners = learners
    
    def predict(self, text):
        predictions = [l.predict(text) for l in self.learners]
        return np.mean(predictions)  # Or use weighted average
```

### Online Learning

Implement incremental learning:

```python
def update_model_online(learner, new_text, new_score):
    # Add new example
    learner.add_training_example(new_text, new_score)
    
    # Retrain periodically
    if len(learner.training_texts) % 100 == 0:
        learner.train()
        learner.save_model("model_latest.pkl")
```

## Conclusion

The Qwen3 Embedding Value Learner provides a powerful and flexible system for learning to rank text based on examples. By combining state-of-the-art language models with robust machine learning techniques, it enables sophisticated text ranking applications with minimal code.

For questions, issues, or contributions, please refer to the project repository.