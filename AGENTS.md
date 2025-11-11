Agent Notes (updated 2025-11-10)

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
 - Context now includes weekday explicitly: `Datetime: YYYY-MM-DD HH:MM:SS (Friday)` for better temporal grounding.

Models & budgets (NLCO iter)
- Primary LM: `deepseek/deepseek-reasoner` with `max_tokens=40000` (`nlco_iter.py:35`, `nlco_textual.py:203`).
- Support LM for subsystems: `deepseek/deepseek-chat` with `max_tokens=4000`, `temperature=0` (`nlco_iter.py:39`, `nlco_textual.py:205`).
- Memory now uses the primary LM (reasoner) in both headless and TUI paths.
- No explicit OpenRouter reasoning budget is set; if routed via OpenRouter, provider defaults apply. We do not pass `reasoning`/`max_reasoning_tokens` today.

Reasoning trace display
- nlco_iter prints a “Model Reasoning · Refiner” panel when the provider returns native reasoning. Critic is currently disabled.
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

Release
- v0.1.1 (2025-11-06): reasoning trace panels in `nlco_iter`, JSONL model logging, TimestampLogApp Markdown view + `gi` input focus, tests updated.
- v0.1.2 (2025-11-10): TimestampLogApp adds a minimal UTF-8 TTY preflight to avoid Textual `UnicodeDecodeError` on misconfigured terminals; new tests in `tests/test_timestamp_textual_preflight.py`.

TTY / UTF-8 preflight (TimestampLogApp)
- Symptom: `UnicodeDecodeError` from `textual.drivers.linux_driver` on launch when the terminal isn’t UTF-8 or `stty iutf8` isn’t set.
- Change: `timestamp_textual_app.py` now checks for (a) TTY stdin/stdout, (b) UTF-8 locale, and (c) `stty iutf8`. If any fail, it exits with a clear message rather than crashing inside Textual.
- Additionally: a small `main()` wrapper prints a concise hint and exits if a `UnicodeDecodeError` escapes the app, though Textual may still render its own traceback from a background thread. The fix remains to correct the terminal environment.
- How to fix env: ensure a UTF-8 locale (e.g., `export LANG=en_US.UTF-8`) and enable UTF-8 input on the TTY: `stty iutf8`.
- Tests: `tests/test_timestamp_textual_preflight.py` exercises the three failure modes with monkeypatching.

Troubleshooting: `iutf8` disabled
- Enable for current shell: `stty iutf8` (run in the same pane you launch the app from).
- Verify: `stty -a | grep -E -- '-?iutf8'` → should show `iutf8` (not `-iutf8`).
- Persist for interactive shells (bash/zsh): add to `~/.bashrc` or `~/.zshrc`:
  - `[ -t 0 ] && stty iutf8 || true`
- tmux/screen: run `stty iutf8` inside each pane; to persist, keep the shell-rc line above (it runs only in interactive TTYs).

Repo housekeeping (2025-11-10)
- Committed and pushed v0.1.2 changes: UTF-8 TTY preflight in `timestamp_textual_app.py`, error hint in `main()`, and tests `test_timestamp_textual_preflight.py`+`test_timestamp_textual_main.py`.

Nootropics log (read-only)
- NLCO Textual UI now shows the last 72h of entries from `~/.nootropics_log.jsonl` in a side panel.
- Strictly read-only: the loader never writes or truncates the file.
- Env var `NLCO_NOOTROPICS_LOG` can point to a different JSONL file for testing.
- Minimal schema: each line must be JSON with an ISO `ts` field; lines without `ts` are skipped.

Caching placement
- To maximize DSPy cache reuse, nootropics data is appended to the `context` input (not `constraints`).
- This keeps the `constraints` string stable across runs and pushes variable nootropics lines "behind" constraints in the prompt ordering.
- Both `nlco_iter.py` and `nlco_textual.py` add a `Nootropics (last 72h)` section at the end of `context`.

NLCO iter tests
- Added tests covering headless iteration behavior without touching real LMs:
  - `tests/test_nlco_iter_logging_and_schedule.py` ensures artifact update, structured schedule JSON write, and JSONL model logs with reasoning.
  - `tests/test_nlco_iter_nootropics_context.py` asserts nootropics appear only in `context` and that `constraints` remain unchanged.
  - Existing `tests/test_nlco_iter.py` validates async memory invocation and artifact write.
- Note: Running the entire repo test suite may fail due to duplicate test module names in `packages/deepseek-batch/tests/`. Run selective tests for NLCO iter.

Quick usage
- TUI: press `r` to run one iteration, `Ctrl+S` to save, `Ctrl+L` to clear logs.
- Headless: scheduler decides when to run; finished-check is currently disabled.
 - Timestamp app: new `gi` shortcut focuses the input if focus is elsewhere.

Iteration counts
- After a constraints.md change (headless), the loop runs up to `MAX_ITERATIONS` (now 30) in one invocation.
- On scheduled hourly ticks (no changes), it runs exactly 1 iteration per tick.
- In the TUI, each press of `r` runs exactly 1 iteration.

Layout tweak (2025-11-07)
- Increased artifact editor area relative to constraints: `#constraints-pane` height 12, `#editor-row` height 30.
- Added `tests/test_nlco_textual_layout.py` to pin these values.

Constraints pane behavior
- The constraints pane now tails the last ~40 lines of `constraints.md`, so it reflects external edits (e.g., TimestampLogApp) rather than just the in-app message list.
- Input submissions still append to the in-app list and rewrite `constraints.md` from that list when running an iteration; avoid concurrent writers to the same file.
- Test: `tests/test_nlco_textual_constraints_tail.py` ensures the pane shows only the tail.

Potential rough edges observed
- `nlco_iter.py` disables finished-check (`if False:`), so it may iterate indefinitely unless externally stopped.
- `nlco_textual.py` writes files in place; concurrent runs could clobber state.
- Timewarrior context: headless `nlco_iter.py` currently does not call `TimewarriorModule.run`, so no Timewarrior info is added to the model context. In the Textual UI, `TimewarriorModule.run` is invoked and its output is shown in the "Timewarrior" pane, but it is not injected into the `context` string passed to Critic/Refiner.
 - Critic stage disabled (2025-11-08): We skip the Critic call and pass an empty critique to Refiner. The TUI shows “Critic disabled” in the Critique panel.

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

Artifact improvement (concept-only, 2025-11-08)
- Minimal acceptance gate: only replace the baseline artifact when a tiny rubric score improves. No fallbacks.
- Rubric inputs: constraints-derived checklist coverage, schedule consistency, and fewer TODO/TBD markers; return 0..100.
- Loop tweak: compute score(prev) and score(candidate); accept candidate if strictly higher (or equal with fewer TODOs). Keep a “best so far”.
- Focus cue: use `Affect.suggested_focus` to generate a one-liner “focus for next iteration” and pass it to the refiner.
- Tests proposed (not yet implemented): two-unchanged-hashes stop, accept-only-on-improvement, and context-frozen-per-iteration.
