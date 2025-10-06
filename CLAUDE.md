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
python -m pytest tests/test_executive_module.py -v  # Executive controller unit tests
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

### Timestamp Note Logger (Textual)
```bash
python timestamp_textual_app.py
```

Features:
- Prefixes each submitted note with `HHMM` military time and inserts `# YYYY-MM-DD` headings on date rollover.
- Shows `artifact.md` in a read-only pane updated automatically (default refresh every 2s; override via `artifact_refresh_seconds`).
- Displays a live "artifact updated X ago" status above the viewer (refreshes every second).
- Appends each entry to `constraints.md`, creating date headers on demand so NLCO loop picks up new instructions immediately.
- Help overlay (`Ctrl+H`) lists primary shortcuts (`Ctrl+C` exit, Enter submit, Esc/i toggle Vim-style modes for the input).
- Vim shortcuts supported: basic motions (`h`, `l`, `w`, `b`, `0`, `$`), delete/change (`d`, `c`, `C`), simple text objects (`iw`, `aw`), and delete/change word commands (e.g., `dw`, `diw`, `ciw`).
- Layout: header → run history log → Vim input → artifact pane (status bottom-right) → help footer.

### Webapp
```bash
cd webapp/
docker compose up --build
```

Backend: http://localhost:8000, Frontend: http://localhost:3000

### HTMX FastAPI Frontend
```bash
./start_htmx_server.sh  # defaults to 127.0.0.1:48123 with --reload
```

Environment overrides (auto-loaded from `.env` via `start_htmx_server.sh`, see `.env.example`):
- `NLCO_WEB_APP_MODULE` (default `webapp.nlco_htmx.app:app`)
- `NLCO_WEB_HOST`, `NLCO_WEB_PORT` (default `127.0.0.1`, `48123`)
- `NLCO_WEB_RELOAD` (set `false` for production) and `NLCO_WEB_WORKERS` (used when reload disabled)
- `NLCO_WEB_LOG_LEVEL` / `NLCO_WEB_EXTRA_OPTS` for additional `uvicorn` tuning
- `NLCO_PYTHON_BIN` to force a specific interpreter (defaults to `python`); useful when packages are installed under pyenv/virtualenv.

Features:
- HTMX dashboard for submitting timestamped constraints (appends to `constraints.md` with auto date headings).
- Live artifact (`artifact.md`), memory (`memory.md`), and short-term memory views with age indicators and auto-refresh.
- Single FastAPI service—no Node build step; HTML templates live in `webapp/nlco_htmx/templates/`.
- Tests: `pytest tests/test_web_htmx_app.py -q` exercises routing, timestamp formatting, and history limits.
- Authentication enforced with FastAPI Users (cookie-based JWT). Default login flow expects GitHub OAuth; password routes remain under `/auth/*` for testing/automation.
- Additional tests ensure unauthenticated requests receive 401s and the GitHub login CTA appears when OAuth is configured.

Auth configuration:
- `NLCO_AUTH_DB_URI` (default `sqlite+aiosqlite:///./nlco_auth.db`)
- `NLCO_AUTH_SECRET` (JWT + reset tokens)
- `NLCO_AUTH_COOKIE_SECURE` (`true` for HTTPS deployments)
- `NLCO_AUTH_COOKIE_MAX_AGE` (seconds, default 604800)
- `NLCO_GITHUB_CLIENT_ID`, `NLCO_GITHUB_CLIENT_SECRET`, `NLCO_GITHUB_REDIRECT_URL`, `NLCO_GITHUB_STATE_SECRET`
- Without GitHub credentials the UI shows a placeholder and you can still use `/auth/register` + `/auth/jwt/login` for local access.

## Configuration Management

Uses Pydantic-validated config from `nlco_config.toml`:
```python
from config import load_config
config = load_config()
```

Override with env vars: WEATHER_CITY, SMARTTHINGS_TOKEN, MLFLOW_TRACKING_URI

Key `[nlco_config.toml]` sections:
- `[social]` defines `post_queue_path` (saved posts queue) and `posted_posts_path` (autoposter history). `context_provider.py` uses them to surface queue counts and warn if the autoposter log is stale.

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
- `context_provider.py` - Builds runtime context (weather, system stats, home status, post queue counts, autoposter health alerts)
- `constraints_diff_module.py` - Computes diffs for constraints.md, feeds the current `task +nlco export` to the LLM, auto-tags commands with `+nlco`, and exposes both a verification module and a 3-try reconciliation loop so Taskwarrior updates are validated before acceptance.
- `nlco_iter.py` - Natural Language Command Optimization; async loop (`iteration_loop`) awaits an asyncified memory manager, so memory updates run concurrently and summaries print once each pass completes.
- `nlco_scheduler.py` - Centralized scheduling rules for the iteration loop: runs immediately on constraint edits, at least once per hour otherwise, and skips the hourly run when constraints have been untouched for ≥3 days. Tested via `pytest tests/test_nlco_scheduler.py -q`.
- `setup_env.sh` - Environment setup script

## Git Best Practices

**Do not commit these files:**
- `artifact.md` - User's personal task/schedule file (changes frequently)
- `constraints.md` - Symlink to user's personal constraints file

These files are tracked but should not be committed in normal workflows.
- `memory_module.py` - ReAct loop that edits persistent `memory.md` via search/replace tools
- `timewarrior_tools.py` - Structured DSPy tool for `timew summary/start/stop`
- `timewarrior_module.py` - Fast loop that keeps Timewarrior tracking aligned with plans
- `executive_module.py` - ReAct coordinator that triggers Timewarrior, memory, or planning updates as needed
- `planning_module.py` - ReAct loop that maintains `plan.toml` via typed edits
- `affect_module.py` - Generates qualitative urgency/emotional assessments from current context
- `reviewer_module.py` - Validates proposed Timewarrior actions before they execute
