# Hacker News Personal Ranking System

A set of terminal UIs for learning your preferences and ranking Hacker News content using machine learning.

## Quick Start

### Install Dependencies (using uv)
```bash
uv pip install textual aiohttp requests numpy scikit-learn
```

### Run the Live Ranking System
```bash
python hn_ranking_live_tui.py
```

This will:
1. Fetch current top stories from Hacker News
2. Let you build your personal top 10
3. Learn from your ranking decisions
4. Suggest new stories that might belong in your top 10

## Features

- **Smart Filtering**: Only shows stories predicted to be in your top 10
- **Uncertainty Display**: See how confident the model is
- **Real-time Learning**: Model improves as you rank
- **Auto-refresh**: Fetches new stories every 5 minutes
- **Persistent State**: Your top 10 is saved between sessions

## How It Works

1. **Initial State**: Shows sample top 10 or loads your saved list
2. **Candidates**: After training, suggests stories that might belong in top 10
3. **Ranking**: Click a candidate to insert it at a specific position
4. **Learning**: The model learns from where you place items
5. **Rejection**: Mark items as "not top 10 material"

## Keyboard Shortcuts

- `q` - Quit
- `r` - Refresh HN data
- `t` - Train model (need 5+ examples)
- `s` - Save model
- `l` - Load saved model
- `f` - Fetch more candidates

## Files Created

- `hn_live_top_10.json` - Your current top 10
- `hn_live_ranking_model.pkl` - Your trained preferences
- `.embeddings_cache/` - Cached text embeddings

## Tips

1. **Start Training Early**: After 5 ranking decisions, press `t` to train
2. **Be Consistent**: The model learns your preferences over time
3. **Reject Liberally**: Don't hesitate to reject items that don't belong
4. **Check Uncertainty**: High uncertainty means the model is less sure

## Other Tools

- `hn_rating_tui.py` - Rate items 1-10 with predictions
- `hn_ranking_tui.py` - Basic ranking without live data
- `hn_api_client.py` - Standalone API client

## Example Session

```
Your Top 10 Items
1. [450pts] Show HN: I built a better way to learn algorithms
2. [380pts] The mathematics of neural networks explained
...

Candidates (Predicted Top 10)
[Pred: 8.5±0.3] [234pts] Why functional programming matters...
[Pred: 7.9±0.5] [198pts] Building compilers from scratch...

> Click on a candidate to rank it
> Choose position 1-10 or reject
> Press 't' after several rankings to train the model
```

## Troubleshooting

**"No candidates to show"**: Train the model first (press `t`)
**"Need at least 5 examples"**: Rank more items before training
**API errors**: Check internet connection
**Display issues**: Resize terminal window

## Advanced Usage

To use real Qwen3 embeddings for better accuracy:
1. Install: `uv pip install sentence-transformers`
2. Edit the imports to use `qwen3_embedding_real.py`
3. Expect 2-3x better ranking accuracy

Enjoy building your personalized HN experience!