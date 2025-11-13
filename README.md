<div align="center">
  <h1>NLCO Iteration Loop · Timestamp TUI</h1>
  <p>
    <a href="https://www.python.org/"><img alt="Python" src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white&style=for-the-badge"></a>
    <a href="https://textual.textualize.io/"><img alt="Textual" src="https://img.shields.io/badge/Textual-TUI-7B46BE?style=for-the-badge"></a>
    <a href="https://github.com/stanfordnlp/dspy"><img alt="DSPy" src="https://img.shields.io/badge/DSPy-Enabled-0F7C0F?style=for-the-badge"></a>
    <a href="#mobile-ssh--termux"><img alt="Termux Friendly" src="https://img.shields.io/badge/Termux-Friendly-00AA00?logo=android&logoColor=white&style=for-the-badge"></a>
    <a href="#testing"><img alt="Tests" src="https://img.shields.io/badge/Tests-pytest-0A9EDC?logo=pytest&logoColor=white&style=for-the-badge"></a>
  </p>
</div>

Refine an artifact from constraints, and capture new constraints quickly.

Contents
- Quick Start
- Key Bindings (TUI)
- Files & Behavior
- Configuration
- Mobile SSH / Termux
- Testing
- Subpackages

Quick Start
- Timestamp TUI (wrapper, recommended)
  - `./timestamp_tui.sh`
- Timestamp TUI (one‑liner, hardened)
  - `stty iutf8; LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 ./timestamp_textual_app.py --lenient-input --fallback-encoding cp1252`
- Headless NLCO loop
  - `python nlco_iter.py`

Key Bindings (TUI)
- `gi` focus input • `ga` focus artifact • `F1` help (more reliable than Ctrl+H on some SSH clients) • `Ctrl+C` exit • `PageUp`/`PageDown` scroll artifact.

Files & Behavior
- `constraints.md` — TUI appends under `# YYYY‑MM‑DD` headings and shows the bottom by default; pane is scrollable and preserves newlines.
- `artifact.md` — headless loop prints reasoning (when provided) and writes updates; TUI renders it read‑only and scrollable.
- `memory.md`, `short_term_memory.md` — persistent and short‑term notes; not injected into prompts by default.

Configuration
- NLCO loop
  - `NLCO_MAX_ITERS` (default 3) caps iterations per run.
  - MLflow optional; if not configured, it’s silently ignored.
- Timestamp TUI
  - Paths: defaults to `~/.nlco/private/{constraints.md, artifact.md}`.
    - Override via env: `TIMESTAMP_CONSTRAINTS_PATH`, `TIMESTAMP_ARTIFACT_PATH`.
    - Override base dir: `NLCO_PRIVATE_DIR` (e.g., `~/nlco-private`).
    - CLI flags: `--constraints-path /path/to/constraints.md`, `--artifact-path /path/to/artifact.md`.
  - `TIMESTAMP_CONSTRAINTS_ROWS` sets constraints pane height; tail count derives from it.
  - `--no-auto-scroll` or `TIMESTAMP_AUTO_SCROLL=0` disables snapping to end.
  - Mobile SSH aids: `--right-margin N` (env `TIMESTAMP_RIGHT_MARGIN`) and `--pad-eol` (env `TIMESTAMP_PAD_EOL=1`) avoid right‑edge clipping.
  - Lenient input for non‑UTF‑8 bytes: `--lenient-input [--fallback-encoding cp1252]` or env `TIMESTAMP_LENIENT_INPUT=1`.

Mobile SSH / Termux
- Enable UTF‑8 input: `stty iutf8`.
- Prefer `F1` for help.
- If you see right‑edge clipping of the last character, try `--pad-eol` or `--right-margin 2`.

Testing
- Timestamp TUI: `pytest -q tests/test_timestamp_textual_app.py`
- Headless NLCO: `pytest -q tests/test_nlco_iter.py`

Subpackages
- `deepseek-batch` remains available for batch selection experiments; see its folder for CLI docs. It’s not the focus of this README.

Dev setup
```
python -m pip install -e .
pytest -q tests
```
