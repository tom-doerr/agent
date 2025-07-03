# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Codebase Overview

This is a DSPy-based agent framework for building intelligent command-line agents that can execute shell commands, learn from interactions, and optimize their performance over time. The framework emphasizes safety, cost tracking, and continuous learning.

## Key Architecture

### Agent Hierarchy
- **Base Classes** (`base_agent.py`): Abstract base classes defining standard agent interfaces
  - `BaseAgent`: Core functionality (safety checking, command execution)
  - `CommandAgent`: Command generation and execution
  - `BatchProcessingAgent`: Batch processing capabilities

### Agent Implementations
- **Main Agent** (`agent_simpledspy.py`): Primary DSPy agent with SimpleDSPy integration
- **Local Agent** (`local_agent.py`): Interactive CLI with Vi-style bindings using Textual
- **Preference Agents** (`ambient_agent.py`, `ambient_pref_agent.py`): Learn from user preferences
- **Ranking Agent** (`ranking_agent.py`): Pairwise comparison for preference learning

### DSPy Integration
- Uses DSPy v1.0+ for language model programming
- SimpleDSPy v0.3.1+ for simplified interfaces
- Custom DSPy programs in `dspy_programs.py` (ValueNetwork, GeneratorModule)
- Extensive mocking in `conftest.py` for testing without API calls

### Data Management
- **NDJSON Format**: All data stored as newline-delimited JSON
- Training data in `.simpledspy/modules/*/training.jsonl`
- Logged interactions in `.simpledspy/modules/*/logged.jsonl`
- Utility functions in `utils/io.py` for NDJSON operations

## Development Commands

```bash
# Environment setup
./setup_env.sh              # Creates venv, installs deps, generates .env.example
source .venv/bin/activate   # Activate virtual environment

# Running agents
python agent_simpledspy.py [--lm MODEL] [--max-tokens N]  # Main agent
python local_agent.py                                      # Interactive CLI
python ranking_agent.py                                    # Ranking helper
python ambient_pref_agent.py                              # Preference agent

# Model options for --lm flag
flash    # Google Gemini Flash (fast, cheap)
r1       # DeepSeek R1 (reasoning)
dv3      # DeepSeek v3 (balanced)

# Testing
pytest                          # Run all tests
pytest tests/test_agent.py -v   # Run specific test file
pytest -k "test_name"          # Run tests matching pattern

# Token usage and cost tracking
python optimization_demo.py              # Run optimization (checks pricing periods)
python optimization_demo.py --force-expensive  # Override expensive period check
python plot_token_usage.py              # Visualize token usage from logs

# MLflow tracking
mlflow ui --port 5002          # Start MLflow UI (default port in config)
```

## Important Patterns

### Safety Features
- All agents inherit command safety checking from `BaseAgent`
- Commands are analyzed before execution to prevent harmful operations
- Whitelist/blacklist patterns for allowed/forbidden commands

### Token and Cost Tracking
- `optimization_demo.py` includes comprehensive token logging
- Tracks input, output, and reasoning tokens separately
- Time-based pricing with DeepSeek discount periods (16:30-00:30 UTC)
- Logs to both NDJSON files and MLflow

### Configuration
- Pydantic-based configuration in `config.py`
- Environment variables override config values
- TOML files for structured configuration

### Testing Strategy
- Comprehensive DSPy mocking to avoid API calls in tests
- Custom pytest configuration in `pytest.ini`
- Test data as NDJSON in test directories

## Key Files to Understand

1. **Agent Logic**: Start with `base_agent.py` then specific implementations
2. **DSPy Programs**: `dspy_programs.py` for custom modules
3. **Testing**: `conftest.py` for the mocking strategy
4. **Utilities**: `utils/io.py` for data operations, `utils/models.py` for DSPy patterns
5. **Cost Tracking**: `optimization_demo.py` and `pricing_config.json`

## Training Data Management

Training data quality directly impacts agent performance:

1. Review interactions: `less .simpledspy/modules/*/logged.jsonl`
2. Copy good examples to training: Add to `training.jsonl`
3. Fix incorrect responses: Edit `training.jsonl` entries
4. Add new behaviors: Create new training examples

## Environment Variables

Required in `.env`:
- `OPENROUTER_API_KEY`: For LLM API access
- `FIRECRAWL_API_KEY`: For web scraping (optional)
- `OLLAMA_MODEL`: Local model name (optional)
- `OLLAMA_BASE_URL`: Local Ollama server (optional)