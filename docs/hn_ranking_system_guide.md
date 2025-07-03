# Hacker News Ranking System Guide

## Overview

The HN Ranking System consists of two Textual TUIs (Terminal User Interfaces) that use Qwen3 embeddings and Ridge regression to learn your preferences for ranking and rating Hacker News content.

## Components

### 1. HN Ranking TUI (`hn_ranking_tui.py`)

A TUI for maintaining your personal top 10 HN items with insertion ranking.

**Features:**
- Displays your current top 10 items
- Suggests new items predicted to be in top 10 
- Allows inserting items at specific positions (1-10)
- Supports rejecting items as "not top 10"
- Learns from your ranking decisions

**Usage:**
```bash
python hn_ranking_tui.py
```

**Keyboard Shortcuts:**
- `q` - Quit
- `r` - Refresh candidates
- `s` - Save model
- `l` - Load model
- `t` - Train model
- Click on candidates to rank them

### 2. HN Rating TUI (`hn_rating_tui.py`)

A TUI for directly rating HN items on a 1-10 scale with uncertainty display.

**Features:**
- Direct 1-10 rating interface
- Shows Qwen3 prediction with uncertainty
- Tracks rating accuracy (MAE, RMSE)
- Real-time model updates
- Performance metrics dashboard

**Usage:**
```bash
python hn_rating_tui.py
```

**Keyboard Shortcuts:**
- `q` - Quit
- `n` - Next item
- `s` - Save model
- `l` - Load model
- `r` - Refresh predictions
- `1-9` - Rate 1-9
- `0` - Rate 10

### 3. Live HN Ranking TUI (`hn_ranking_live_tui.py`)

Production version with real HN data integration.

**Features:**
- Fetches real stories from HN API
- Auto-refreshes every 5 minutes
- Persistent top 10 storage
- Multiple story sources (top, new, best)
- Advanced statistics tracking

**Usage:**
```bash
python hn_ranking_live_tui.py
```

**Additional Shortcuts:**
- `f` - Fetch new candidates
- `u` - Update predictions

### 4. HN API Client (`hn_api_client.py`)

Async client for fetching HN data.

**Features:**
- Concurrent story fetching
- Multiple endpoints (top, new, best, show)
- Rate limiting
- Error handling

## Machine Learning Details

### Value Function Learning

The system uses Ridge regression on text embeddings to learn a value function:

```python
value = f(embedding(text))
```

Where:
- `embedding()` - Qwen3 text embeddings (simulated or real)
- `f()` - Ridge regression model
- `value` - Predicted score (0-10)

### Training Data

Training examples are generated from:
1. **Ranking actions**: Position 1 → score 10, Position 10 → score 1
2. **Rejection actions**: Rejected items → score 0
3. **Direct ratings**: User ratings → exact scores

### Uncertainty Estimation

Uncertainty is estimated through ensemble predictions:
```python
predictions = [predict(text + noise) for _ in range(10)]
mean = np.mean(predictions)
uncertainty = np.std(predictions) + base_uncertainty
```

## Installation

### Using uv (recommended):
```bash
uv pip install textual aiohttp requests numpy scikit-learn
```

### Using pip:
```bash
pip install textual aiohttp requests numpy scikit-learn
```

## Quick Start

1. **First Time Setup:**
   ```bash
   # Start the live ranking TUI
   python hn_ranking_live_tui.py
   
   # It will fetch top stories from HN
   # Train the model after a few rankings
   ```

2. **Ranking Workflow:**
   - View current top 10
   - Click on suggested candidates
   - Choose insertion position or reject
   - Model learns from your choices
   - Press `t` to train after 5+ examples

3. **Rating Workflow:**
   ```bash
   python hn_rating_tui.py
   
   # Rate items 1-10
   # Model trains automatically every 5 ratings
   # Watch prediction accuracy improve
   ```

## Data Files

The system creates several data files:

- `hn_ranking_model.pkl` - Trained ranking model
- `hn_rating_model.pkl` - Trained rating model  
- `hn_top_10.json` - Your current top 10
- `hn_live_top_10.json` - Live version's top 10
- `hn_live_ranking_model.pkl` - Live version's model

## Advanced Usage

### Using Real Qwen3 Embeddings

To use real Qwen3 embeddings instead of simulated:

1. Install dependencies:
   ```bash
   uv pip install sentence-transformers
   ```

2. Modify the import in your TUI:
   ```python
   # Replace this:
   from qwen3_embedding_value_learner import Qwen3EmbeddingValueLearner
   
   # With this:
   from qwen3_embedding_real import Qwen3RealEmbeddingLearner as Qwen3EmbeddingValueLearner
   ```

### Custom Task Instructions

When using real embeddings, provide task-specific instructions:

```python
learner = Qwen3RealEmbeddingLearner(
    model_name="Qwen/Qwen3-Embedding-0.6B",
    use_instructions=True,
    task_description="Rank HN stories by technical quality and relevance"
)
```

### Batch Training

For better model performance with existing data:

```python
# Load historical rankings
examples = [
    ("Great technical deep-dive on database internals", 9.0),
    ("Yet another JS framework announcement", 3.0),
    # ... more examples
]

learner.add_training_examples([
    RankingExample(text, score) 
    for text, score in examples
])

metrics = learner.train()
```

## Performance Tips

1. **Model Training**: Train after 5-10 examples for best results
2. **Uncertainty**: Higher uncertainty = less confident predictions
3. **Caching**: Models cache embeddings for performance
4. **GPU**: Use GPU for real Qwen3 embeddings if available

## Troubleshooting

### "Need at least X examples to train"
- Add more ranking/rating examples before training
- Load a pre-trained model with `l` key

### API Rate Limiting
- HN API has no official rate limits
- Client uses semaphore for concurrent limits
- Adjust `max_concurrent` if needed

### TUI Display Issues
- Ensure terminal supports Unicode
- Try different terminal emulators
- Resize terminal if layout is broken

### Model Not Improving
- Check training data quality
- Ensure diverse examples
- Try adjusting `ridge_alpha` parameter
- Consider using real embeddings

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│   HN API Client │────▶│  TUI Apps    │────▶│ Qwen3 Learner   │
│  (async fetch)  │     │  (Textual)   │     │ (Ridge + Embed) │
└─────────────────┘     └──────────────┘     └─────────────────┘
         │                      │                      │
         ▼                      ▼                      ▼
   ┌──────────┐          ┌──────────┐          ┌──────────┐
   │ HN Data  │          │ User     │          │ Models   │
   │ (JSON)   │          │ Actions  │          │ (.pkl)   │
   └──────────┘          └──────────┘          └──────────┘
```

## Future Enhancements

1. **Active Learning**: Suggest items with highest uncertainty
2. **Multi-user**: Separate models per user
3. **Export/Import**: Share rankings with others
4. **Web Interface**: Browser-based version
5. **Categories**: Separate rankings by topic
6. **Time Decay**: Older items naturally decline
7. **Comments Integration**: Consider comment quality

## Contributing

To add new features:

1. Follow existing patterns for TUI widgets
2. Maintain type hints
3. Add tests for new functionality
4. Update documentation

## License

This system is provided as-is for educational purposes. The Qwen3 models are licensed under Apache 2.0.