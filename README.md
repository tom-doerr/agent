# NLCO Iteration Loop and Timestamp TUI

Short, focused tools for iterating on an artifact with constraints and for fast note‑taking into `constraints.md`.

What’s here
- Headless NLCO loop: `nlco_iter.py` refines `artifact.md` from `constraints.md` + context. Critic and structured schedule output are removed. The refiner receives a minimal `SystemState` containing the last artifact update time.
- Timestamp Log TUI: `timestamp_textual_app.py` shows the bottom of `constraints.md`, lets you append timestamped lines, and renders `artifact.md` (scrollable Markdown).

Quick start
- Timestamp TUI (recommended wrapper):
  - `./timestamp_tui.sh`
- Timestamp TUI (one‑liner, hardened):
  - `stty iutf8; LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 ./timestamp_textual_app.py --lenient-input --fallback-encoding cp1252`
- Headless NLCO:
  - `python nlco_iter.py`

Key bindings (TUI)
- `gi` focus input • `ga` focus artifact • `F1` help (use this instead of Ctrl+H on some SSH clients) • `Ctrl+C` exit • `PageUp/PageDown` scroll artifact.

Files and behavior
- `constraints.md` — Timestamp TUI appends lines under `# YYYY‑MM‑DD` headings and shows the bottom by default; the pane is scrollable and preserves newlines.
- `artifact.md` — headless loop prints model reasoning (when supported) and writes updates; TUI renders it read‑only and scrollable.
- `memory.md`, `short_term_memory.md` — persistent and short‑term notes; not injected into prompts by default.

Configuration
- NLCO loop:
  - `NLCO_MAX_ITERS` (default 3) caps iterations per run.
  - Optional MLflow (local): set tracking URI if you use it; otherwise it’s ignored.
- Timestamp TUI:
  - `TIMESTAMP_CONSTRAINTS_ROWS` sets the constraints pane height; the tail count derives from it.
  - `--no-auto-scroll` or `TIMESTAMP_AUTO_SCROLL=0` disables snapping to end.
  - Mobile SSH aids: `--right-margin N` (env `TIMESTAMP_RIGHT_MARGIN`) and `--pad-eol` (env `TIMESTAMP_PAD_EOL=1`) help avoid right‑edge clipping.
  - Lenient input for non‑UTF‑8 bytes: `--lenient-input [--fallback-encoding cp1252]` or env `TIMESTAMP_LENIENT_INPUT=1`.

Mobile SSH / Termux notes
- Enable UTF‑8 input on the TTY: `stty iutf8`.
- Prefer `F1` for help (some clients map `Ctrl+H` to backspace).
- If you see right‑edge clipping of the last character, try `--pad-eol` or `--right-margin 2`.

Testing
- Timestamp TUI focused tests: `pytest -q tests/test_timestamp_textual_app.py`
- Headless loop smoke tests: `pytest -q tests/test_nlco_iter.py`

Subpackages
- The `deepseek-batch` package remains available for batch selection experiments; see its CLI docs in that folder. It’s not the focus of this README.

Dev setup
```
python -m pip install -e .
pytest -q tests  # offline‑friendly tests
```

