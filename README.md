# NLCO Iteration Loop · Timestamp TUI

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
