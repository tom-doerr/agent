# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Multi-project repository focused on DSPy-based AI agents and tools:
- **SimpleDSPy Agent** - Main agent with command execution
- **NLCO Iteration Loop** - Local planner with Timewarrior + memory automation
- **Structured Schedule Pipeline** – Refiner now emits Pydantic-typed `ScheduleBlock` data in parallel with the artifact; the CLI/Textual loops persist it to `structured_schedule.json` for downstream tooling.
- **Web DSPy Builder** - Node-based visual editor for DSPy programs
- **Abbreviation Decoder** - CLI for expanding abbreviated text
- **Textual DSPy** - Terminal UI for DSPy
- **agent-manual Poetry Package** - Minimal Textual DSPy TUI packaged for installation (modular runtime, memory, CLI, TUI components)
- **Webapp** - Multimodal web app with Gemini
- **Hill Climb Learning** - Interactive text improvement via human-in-the-loop DSPy optimization

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

### agent-manual (Poetry package)
```bash
cd agent_manual_pkg
poetry install
poetry run agent-manual
```

Highlights:
- `/model` prompt toggles between the two DeepSeek v3.2 experimental presets (`chat` vs `reasoner`), both using the `openrouter/deepseek/deepseek-v3.2-exp` slug with different reasoning budgets.
- `run_shell` tool shows the shell command, DSPy safety verdict, and captured output directly in the Textual log.
- Uses a custom `ReadableReAct` DSPy module (no upstream fallback) so each step (thought/tool/observation) streams into the UI, the raw LM transcript is preserved, and the runtime exposes it via `runtime.get_agent()`.
- Config persisted to `~/.config/agent-manual/config.json` (override with `AGENT_MANUAL_CONFIG` or `--config` CLI flag); updates made via CLI or `/model` are saved and reloaded on next launch.
- `max_tokens` is configurable via CLI (`--max-tokens`), the config file, or `/max_tokens` inside the TUI, and persists across runs.
- Dedicated memory pane mirrors the persisted `memory.json` alongside the main log; the async `MemoryModule` produces Pydantic-validated slot updates (<=100 chars) after each tool step and keeps file + UI in sync.
- Satisfaction pane (top-left) shows the latest instrumental goals plus a 1–9 score with rationale computed by two DSPy modules (`GoalPlanner` and `SatisfactionScorer`); memory occupies the lower-left pane, while the chat log lives on the right.
- `/modules` now includes per-module presets for `satisfaction_goals` and `satisfaction_score` so you can swap LMs independently of the agent and memory summarizer.
- `/modules` opens a menu to assign models per DSPy module (agent vs memory); selections persist in `module_models` within the config.
- Status pane shows active models/modules, live elapsed timer, and request state while the TUI is working; all errors bubble into the log and status banner.
- Animated spinner (`⠋⠙⠹…`) appears under the status while DSPy work is in progress, flipping to the result once the step finishes so users see live feedback during long calls.
- Theme refreshed around a deep-red accent: consistent borders, red scrollbars, and a compact top bar keep the layout balanced.
- Side pane now includes “DSPy Raw” which shows the unparsed conversation payloads so you can inspect exactly what DSPy saw each turn.
- Press `Ctrl+,` to open the in-app settings overlay—cycle through models or edit `max_tokens` inline, with inline descriptions for every knob.
- `?` toggles a help modal, `g` then `i` focuses the prompt input, and `ESC` exits it; user, agent, and system messages are color-coded in the log for clarity.
- New `send_message` tool lets the agent reply directly to the user (message is emitted in the log/status without additional tooling).
- Memory summarization now uses a DSPy `Predict` call (`MemoryModule.SummarySignature`) to produce structured updates; validators in `MemorySlotUpdate` enforce max length with inline documentation.
- Tests: `DSPY_CACHEDIR=/tmp/.dspy_cache pytest tests/test_agent_manual.py -q`
- E2E (requires OpenRouter/OpenAI creds): `zsh -ic 'cd /home/tom/git/agent && DSPY_CACHEDIR=/tmp/.dspy_cache pytest tests/test_agent_manual_e2e.py -q'`
- Unit coverage for the Textual shell lives in `agent_manual_pkg/tests/test_tui.py`; from `agent_manual_pkg/` run `pytest` to validate theme, overlay, and raw-history wiring.

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
- Structured schedule table sourced from `structured_schedule.json`, refreshed via HTMX and mirrored in the `/api/v1/status` payload for other clients.
- Single FastAPI service—no Node build step; HTML templates live in `webapp/nlco_htmx/templates/`.
- Tests: `pytest tests/test_web_htmx_app.py -q` exercises routing, timestamp formatting, and history limits.
- Additional cases cover the structured schedule table, schedule JSON parsing errors, and loader helpers to guarantee validation stays consistent with the refiner contract.
- Authentication enforced with FastAPI Users (cookie-based JWT). Default login flow expects GitHub OAuth; password routes remain under `/auth/*` for testing/automation.
- Additional tests ensure unauthenticated requests receive 401s and the GitHub login CTA appears when OAuth is configured.
- JSON API endpoints (authenticated): `GET /api/v1/status` returns artifact/memory/history snapshots, `POST /api/v1/messages` appends a constraint line and returns the refreshed snapshot. Both reuse FastAPI Users sessions (cookie `nlco_auth`).
- Login UI: the `/` route now renders a username/password form (plus optional GitHub button). The form POSTs to `/auth/jwt/login`, shows client-side errors, and redirects on success. Usernames without `@` are expanded using the default-user domain or the closest matching email (e.g. `tom` → `tom@nlco.dev`).
- Optional bootstrap user: set `NLCO_DEFAULT_USER_EMAIL` and `NLCO_DEFAULT_USER_PASSWORD`; the app creates that account at startup so you can sign in immediately.
- `pytest tests/test_web_htmx_app.py -q` exercises both HTMX pages and JSON routes.

### Android Mobile App
- Location: `android/nlco-android`
- Features: native Compose UI mirroring the HTMX dashboard (artifact + memory snapshots, constraint history, message composer), Retrofit client with persisted session cookies, and reactive state via `MainViewModel`.
- Build requirements: JDK 17 and Android SDK (`platforms;android-34`, `build-tools;34.0.0`). Configure `local.properties` (`sdk.dir`) or `ANDROID_SDK_ROOT`.
- Backend URL defaults to `http://10.0.2.2:48123/`; override with `-Pnlco.baseUrl=https://your-host/` or adjust `gradle.properties`.
- Tests: run from `android/nlco-android/` with `JAVA_HOME=/path/to/jdk17 ./gradlew test` (ensure the Gradle wrapper can download `gradle-8.7-bin.zip`).
- Manual builds: `JAVA_HOME=/path/to/jdk17 ./gradlew assembleDebug`. To avoid wrapper downloads on restricted networks, you can use a pre-installed Gradle 8.7 binary (`/path/to/gradle-8.7/bin/gradle assembleDebug`).

### Hill Climb Learning
```bash
cd hill_climb_learning/
python cli.py "Your initial text here"
```

Features:
- Interactive Rich CLI for human-in-the-loop text improvement.
- Two DSPy modules: `TextModifier` generates improved versions, `TextEvaluator` predicts if modifications are better.
- Human feedback loop: user marks each modification as better/worse, feedback becomes few-shot examples.
- Uses `dspy.LabeledFewShot` with k=64 to rebuild the evaluator after each feedback round.
- Few-shot examples stored in `examples.jsonl` with fields: `original`, `modified`, `is_better`.
- Tests: `pytest tests/test_hill_climb_learning.py -v`

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
- Signature convention: declare `constraints` as the first input wherever a DSPy signature includes it to minimize cache churn.

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
- `refiner_signature.py` - `RefineSignature` outputs `List[ArtifactEdit]` (single-line search/replace) + summary; Pydantic validator enforces no newlines in search field.
- `nlco_scheduler.py` - Centralized scheduling rules for the iteration loop: runs immediately on constraint edits, at least once per hour otherwise, and skips the hourly run when constraints have been untouched for ≥3 days. Tested via `pytest tests/test_nlco_scheduler.py -q`.
- `setup_env.sh` - Environment setup script

## Git Best Practices

**Do not commit these files:**
- `artifact.md` - User's personal task/schedule file (changes frequently)
- `constraints.md` - Symlink to user's personal constraints file

These files are tracked but should not be committed in normal workflows.
- `memory_module.py` - Predict-based module that edits `memory.md` via `List[EditBlock]` search/replace; maintains a Hypotheses section with evidence for/against
- `timewarrior_tools.py` - Structured DSPy tool for `timew summary/start/stop`
- `timewarrior_module.py` - Fast loop that keeps Timewarrior tracking aligned with plans
- `executive_module.py` - ReAct coordinator that triggers Timewarrior, memory, or planning updates as needed
- `planning_module.py` - ReAct loop that maintains `plan.toml` via typed edits
- `affect_module.py` - Generates qualitative urgency/emotional assessments from current context
- `reviewer_module.py` - Validates proposed Timewarrior actions before they execute
