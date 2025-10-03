# DSPy Visual Builder

Interactive node-based interface for authoring and running DSPy programs. The backend
is a FastAPI service that serves the static LiteGraph UI and executes graphs via the
`web_dspy_builder` runtime.

## Prerequisites
- Python 3.11+ (project already uses `.venv`)
- Dependencies from `requirements.txt` (`fastapi`, `uvicorn`, `pydantic`, `dspy-ai`, ...)
- Optional: DSPy configured with actual language-model credentials; otherwise the
  mock engine lets you experiment offline.

Install dependencies if you have not already:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Launch

```bash
python -m web_dspy_builder --host 0.0.0.0 --port 8800
```

Then open <http://localhost:8800> to access the builder. The command-line flags (or
`DSPY_BUILDER_HOST`/`DSPY_BUILDER_PORT` environment variables) let you avoid port
collisions with other services. Use `--reload` while iterating on the backend.

## Features
- Node palette with DSPy-specific blocks (inputs, LLMs, Python nodes, loops, outputs)
- WebSocket-backed execution engine with run history, logs, and edge visualisation
- Program templates to bootstrap common DSPy workflows (e.g. typed cognition agent)
- Mock LLM engine so you can test the UI without external APIs; switch engines in
  the sidebar to use real models once configured.
