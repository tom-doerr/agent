# Hypothesis Perplexity Evaluation Scripts

This collection of scripts helps evaluate the explanatory value of hypotheses by measuring how much they improve the predictability of outcomes given situations.

## Scripts

### 1. `hypothesis_perplexity_evaluator.py`
Full-featured evaluator using local transformer models to calculate actual perplexity scores.
- Uses Hugging Face transformers (GPT-2 by default)
- Calculates true perplexity metrics
- Suitable for rigorous evaluation

### 2. `hypothesis_perplexity_api.py`
Lightweight API-based evaluator using language models via OpenRouter.
- Two evaluation methods:
  - **likelihood**: Asks model to rate outcome likelihood (0-100)
  - **comparative**: Direct A/B comparison of explanatory value
- Faster and doesn't require local GPU

### 3. `test_hypothesis_simple.py`
Minimal test script to verify API connectivity and basic functionality.

## Usage Examples

```bash
# API version with demo
python hypothesis_perplexity_api.py --demo --method comparative

# API version with file
python hypothesis_perplexity_api.py --file hypothesis_examples.json --method likelihood

# Local transformer version with demo
python hypothesis_perplexity_evaluator.py --demo --model gpt2

# Interactive mode (enter cases manually)
python hypothesis_perplexity_api.py --method comparative
```

## Example Data Format

Create JSON files with evaluation cases:

```json
[
  {
    "name": "Conservation of Energy",
    "hypothesis": "Energy cannot be created or destroyed, only transformed",
    "situation": "A pendulum is released from a height",
    "outcome": "The pendulum swings back to nearly the same height"
  }
]
```

## Key Insights

1. **Comparative method** tends to give more meaningful distinctions than likelihood scores
2. The system evaluates whether including the hypothesis makes the outcome more expected/natural
3. Good hypotheses should significantly improve outcome predictability
4. Results help validate scientific theories and explanatory frameworks

## Requirements

- Python 3.8+
- For API version: `OPENROUTER_API_KEY` in `.env` file
- For local version: `pip install transformers torch`
- DSPy and other dependencies from the project

## Notes

- The API version is recommended for quick evaluation
- The comparative method provides clearer signal about explanatory value
- Consider using multiple test cases to validate hypothesis quality
- Lower perplexity = more predictable = better hypothesis