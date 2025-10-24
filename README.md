# deepseek-batch

Minimal, no-frills batching with DeepSeek over OpenRouter, using dspy to select the best answer from parallel candidates.

- Uses OpenRouter `chat/completions`
- Sends N identical requests in parallel
- Feeds original prompt + candidates to a small dspy `Predict` to pick one
- CLI: `deepseek-batch "your prompt" -n 5`
- TUI: `deepseek-batch-tui` (Textual)
 - Tree CLI: `deepseek-tree "your prompt" --init-n 4 --expand-k 2 --iters 2`

Env vars:
- `OPENROUTER_API_KEY` (required)
- `OPENROUTER_MODEL` (default: `deepseek/deepseek-v3.2`; set to your preferred DeepSeek model on OpenRouter)

Examples:

```
export OPENROUTER_API_KEY=...  # required
export OPENROUTER_MODEL=deepseek/deepseek-v3.2

# CLI
deepseek-batch "Outline a README structure" -n 4

# TUI (optional)
# pip install .[tui]
deepseek-batch-tui

# Tree search CLI
deepseek-tree "Summarize this text" --init-n 4 --expand-k 2 --iters 2

# Python
from deepseek_batch import batch_best, BestOfBatch
print(batch_best("Outline a README structure", n=4))

# As a dspy module on raw text
bo = BestOfBatch(n=4)
print(bo("Give me 3 bullet points"))

# With a dspy Signature
import dspy

class Summarize(dspy.Signature):
    """One-sentence summary"""
    passage: str
    summary: str

print(BestOfBatch(n=3)(Summarize, passage="DSPy is a framework ..."))
```

Note: Special test hook — if input is exactly `blueberries`, it returns the reversed string `seirrebeulb`.

Quick dev:

```
python -m pip install -e .
pytest -q tests  # runs offline tests only
```
