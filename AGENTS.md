 Agent Notes (updated 2025-11-05)

- NLCO iter TUI lives in `nlco_textual.py` (`NLCOTextualApp`). Run: `python nlco_textual.py`.
- Headless alternative is `nlco_iter.py` (console loop). Run: `python nlco_iter.py`.
- You do NOT need both at once; the TUI runs iterations itself. Avoid concurrent runs (shared files).
- Another TUI exists: `timestamp_textual_app.py` (`TimestampLogApp`). This is a lightweight note pad that prefixes lines with the current time and appends them to `constraints.md` under daily headings. It does not run the NLCO iteration pipeline or any DSPy modules; it only shows `artifact.md` and its last-updated age.
- Files touched: none (informational change only).

Things to keep in mind
- Textual and Rich must be installed to run the TUI.
- MLflow is optional; `nlco_textual.py` enables it if available and writes `structured_schedule.json` in repo root.
- Constraints and artifact paths are fixed: `constraints.md`, `artifact.md`, `memory.md`, `short_term_memory.md`.
- `timestamp_textual_app.py` appends to `constraints.md` and can be used alongside NLCO tools, but beware of concurrent writes to the same file.

Models & budgets (NLCO iter)
- Primary LM: `deepseek/deepseek-reasoner` with `max_tokens=40000` (`nlco_iter.py:35`, `nlco_textual.py:203`).
- Support LM for subsystems: `deepseek/deepseek-chat` with `max_tokens=4000`, `temperature=0` (`nlco_iter.py:39`, `nlco_textual.py:205`).
- No explicit OpenRouter reasoning budget is set; if routed via OpenRouter, provider defaults apply. We do not pass `reasoning`/`max_reasoning_tokens` today.

Reasoning trace display
- nlco_iter now prints a “Model Reasoning · Critic/Refiner” panel when the provider returns native reasoning:
  - DeepSeek API: reads `message.reasoning_content`.
  - OpenRouter: reads `message.reasoning.{text|summary}`.
- To force reasoning over OpenRouter, pass the unified `reasoning` parameter (e.g., `{"enabled": true}` or `{"effort": "medium"}`) via your LM config; we kept runtime code minimal and non-intrusive.

Model output logging
- All model outputs (including reasoning if present) append to JSONL at `.nlco/model_log.jsonl`.
- Set `NLCO_MODEL_LOG=/path/to/file.jsonl` to change the destination.
- Each line: `{ ts, stage, output, reasoning }`.

Textual Markdown
- Textual provides a `Markdown` widget that parses Markdown with a GFM-like parser (tables, task lists, strikethrough, autolinks).
- For interactive/spreadsheet-like tables, use `DataTable`; Markdown tables are static.
- TimestampLogApp now renders `artifact.md` via `Markdown` (read-only) instead of a `TextArea`.

Quick usage
- TUI: press `r` to run one iteration, `Ctrl+S` to save, `Ctrl+L` to clear logs.
- Headless: scheduler decides when to run; finished-check is currently disabled.
 - Timestamp app: new `gi` shortcut focuses the input if focus is elsewhere.

Potential rough edges observed
- `nlco_iter.py` disables finished-check (`if False:`), so it may iterate indefinitely unless externally stopped.
- `nlco_textual.py` writes files in place; concurrent runs could clobber state.

Future test ideas
- Add a Textual `App.run_test()` smoke test to ensure `NLCOTextualApp` composes and updates logs without launching a real UI.
- Validate that running one iteration creates/updates `structured_schedule.json`.
- Model lineage update (2025-09-29)
  - DeepSeek docs state both `deepseek-chat` and `deepseek-reasoner` were upgraded to `DeepSeek-V3.2-Exp`; `chat` = non-thinking mode, `reasoner` = thinking mode. Over OpenRouter, reasoning appears in the `reasoning` field; via DeepSeek API it appears as `message.reasoning_content`.
Timewarrior Control — Conceptual Plan
- Current state: `TimewarriorModule` exists and works in the Textual UI (`nlco_textual.py` calls `TimewarriorModule.run`, around the stage pipeline). In the headless loop, `nlco_iter.py` instantiates `TimewarriorModule` but never calls it, so no tracking occurs.
- Likely failure cause: headless flow never invokes Timewarrior; summary parsing is brittle (looks for a "Tags" line and the phrase "there is currently no active time tracking").
- Minimal enablement: call `timewarrior_tracker.run(...)` early in `iteration_loop` (before memory/planning) and log the result. Add two tests that monkeypatch the tool to simulate `summary` and `start/stop` success.
- Robust detection: prefer `timew export` JSON (or `timew get dom.active*`) to detect active state + tags instead of scraping `summary`. Keep it simple—no fallbacks unless asked.
- Control policy: default to deterministic rules from `structured_schedule.json` (start/stop on block boundaries; derive tags from the active block). Use the LLM reviewer only when schedule vs. context disagree.
- Safety and UX: add a 2–3 minute hysteresis to avoid flapping; add a dry-run flag; allow manual overrides via constraints lines (e.g., `timew:start tag1 tag2`, `timew:stop`).
- Observability: record `{ts, action, tags, justification, stdout/stderr}` to `.nlco/timew_log.jsonl`; unit-test both “timew missing” and normal paths.
