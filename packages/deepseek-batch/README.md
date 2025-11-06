# deepseek-batch (subpackage)

Installable on its own from this directory via Poetry or pip.

Install
- Poetry: `poetry install` (or `poetry install -E tui`)
- Pip: `python -m pip install -e .` (or `.[tui]`)

Environment
- `OPENROUTER_API_KEY` (required)
- `OPENROUTER_MODEL` (optional; defaults to `deepseek/deepseek-v3.2`)

CLI
- `deepseek-batch "Prompt" -n 4 --temperature 0.2`
- `deepseek-tree "Prompt" --init-n 4 --expand-k 2 --iters 2`
- `deepseek-batch-tui` (after installing with `-E tui`)

Python
```
from deepseek_batch import batch_best
print(batch_best("3 key risks", n=4, gen_params={"temperature":0.2}))
```
