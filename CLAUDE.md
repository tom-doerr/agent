# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Multi-project repository focused on DSPy-based AI agents and tools:
- **SimpleDSPy Agent** - Main agent with command execution
- **NLCO Iteration Loop** - Local planner with Timewarrior + memory automation
- **Web DSPy Builder** - Node-based visual editor for DSPy programs
- **Abbreviation Decoder** - CLI for expanding abbreviated text
- **Textual DSPy** - Terminal UI for DSPy
- **Webapp** - Multimodal web app with Gemini

## Environment Setup

```bash
./setup_env.sh  # Creates venv, installs deps
source .venv/bin/activate
uv pip install -r requirements.txt  # Manual install
```

Environment variables (.env):
- OPENROUTER_API_KEY
- FIRECRAWL_API_KEY (optional)
- SMARTTHINGS_TOKEN (optional)
- MLFLOW_TRACKING_URI

## Running Tests

```bash
pytest  # All tests
python -m pytest tests/test_cognition_typed_dspy.py -v  # Specific file
python -m pytest tests/test_config.py::TestConfigIO -v  # Specific class
```

## Running Components

### SimpleDSPy Agent
```bash
python agent_simpledspy.py  # Default model
python agent_simpledspy.py --lm r1  # Use specific model (flash/r1/dv3)
```

Training data: `.simpledspy/modules/*/training.jsonl`

### Web DSPy Builder
```bash
python -m web_dspy_builder --host 0.0.0.0 --port 8800
python -m web_dspy_builder --reload  # Development mode
```

Access at http://localhost:8800
Key files: server.py, graph_runner.py, frontend/app.js

### Abbreviation Decoder
```bash
cd abbrev_decoder/
./abbrev "wdyt"  # Decode abbreviation
./abbrev -i  # Interactive mode
python abbrev_optimization_simple.py  # Run optimization
```

Uses `abbrev_dataset.jsonl` for training, saves to `abbrev_expander_optimized.json`

### Webapp
```bash
cd webapp/
docker compose up --build
```

Backend: http://localhost:8000, Frontend: http://localhost:3000

## Configuration Management

Uses Pydantic-validated config from `nlco_config.toml`:
```python
from config import load_config
config = load_config()
```

Override with env vars: WEATHER_CITY, SMARTTHINGS_TOKEN, MLFLOW_TRACKING_URI

## Key Architecture

### Typed Cognition Pipeline
`cognition_typed_dspy.py` implements multi-stage cognition:
- Perception → Belief → Affect → Planning → Scoring → Decision → Verification → Outcome → Update
- Each stage uses typed Pydantic models
- Supports offline testing with `OfflineDSPyLM`

### Graph Execution Engine
`web_dspy_builder/graph_runner.py` processes nodes topologically:
- Caches node outputs with invalidation
- Supports loops with body graphs
- Emits WebSocket events (node_start, node_end, edge_data)
- Handles Python execution, LLM calls, custom nodes

### DSPy Patterns
- DSPy modules in `dspy_modules/` and `dspy_programs/`
- Configure with `dspy.configure(lm=...)`
- Training data in `.jsonl` format
- Use `OfflineDSPyLM` for testing without API calls

## MLflow Integration

```python
import mlflow
mlflow.set_tracking_uri(config.mlflow.tracking_uri)
mlflow.log_param("model", "gemini-flash")
mlflow.log_metric("accuracy", 0.95)
```

Data in `mlruns/` and `mlartifacts/`

## Docker Usage

Docker Compose files with non-standard ports to avoid host conflicts:
- `webapp/docker-compose.yml` - Backend (8000), Frontend (3000)
- `web_dspy_builder/docker-compose.yml` - Builder (8800)

## Important Files

- `agent_simpledspy.py` - Main SimpleDSPy agent
- `cognition_typed_dspy.py` - Typed cognition pipeline
- `config.py` - Pydantic configuration management
- `context_provider.py` - Context utilities
- `nlco_iter.py` - Natural Language Command Optimization
- `setup_env.sh` - Environment setup script

## Git Best Practices

**Do not commit these files:**
- `artifact.md` - User's personal task/schedule file (changes frequently)
- `constraints.md` - Symlink to user's personal constraints file

These files are tracked but should not be committed in normal workflows.
- `memory_module.py` - ReAct loop that edits persistent `memory.md` via search/replace tools
- `timewarrior_tools.py` - Structured DSPy tool for `timew summary/start/stop`
- `timewarrior_module.py` - Fast loop that keeps Timewarrior tracking aligned with plans
