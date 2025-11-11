Agent Notes (updated 2025-11-10)

- NLCO iter TUI lives in `nlco_textual.py` (`NLCOTextualApp`). Run: `python nlco_textual.py`.
- Headless alternative is `nlco_iter.py` (console loop). Run: `python nlco_iter.py`.
- You do NOT need both at once; the TUI runs iterations itself. Avoid concurrent runs (shared files).
- Another TUI exists: `timestamp_textual_app.py` (`TimestampLogApp`). This is a lightweight note pad that prefixes lines with the current time and appends them to `constraints.md` under daily headings. It does not run the NLCO iteration pipeline or any DSPy modules; it only shows `artifact.md` and its last-updated age.
- Files touched: none (informational change only).

Things to keep in mind
- Textual and Rich must be installed to run the TUI.
- MLflow is optional; `nlco_textual.py` enables it if available. Structured schedule JSON is no longer produced by the refiner.
- Constraints and artifact paths are fixed: `constraints.md`, `artifact.md`, `memory.md`, `short_term_memory.md`.
- `timestamp_textual_app.py` appends to `constraints.md` and can be used alongside NLCO tools, but beware of concurrent writes to the same file.
 - Context now includes weekday explicitly: `Datetime: YYYY-MM-DD HH:MM:SS (Friday)` for better temporal grounding.

Models & budgets (NLCO iter)
- Primary LM: `deepseek/deepseek-reasoner` with `max_tokens=40000` (`nlco_iter.py:35`, `nlco_textual.py:203`).
- Support LM for subsystems: `deepseek/deepseek-chat` with `max_tokens=4000`, `temperature=0` (`nlco_iter.py:39`, `nlco_textual.py:205`).
- Memory now uses the primary LM (reasoner) in both headless and TUI paths.

Memory module limits
- `MemoryModule.max_iters` = 4 by default. Each ReAct step can call a tool (e.g., `replace_memory` or `append_memory`).
- One `replace_memory` call replaces all occurrences of the search string in `memory.md` (not just one), and increments the edit counter.
- Effective bound per invocation: up to 4 tool-driven edits, but fewer if the ReAct loop decides to stop early.
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
- v0.1.3 (2025-11-11): Add a 1‑column right padding to the `Log` widget in `timestamp_textual_app.py` to avoid last‑column clipping observed on some mobile SSH clients (e.g., JuiceSSH/Termux). New test `tests/test_timestamp_textual_layout_margin.py` pins this CSS.
- v0.1.4 (2025-11-11): Optional lenient input hook for Textual: set `TIMESTAMP_LENIENT_INPUT=1` to monkeypatch `textual.drivers.linux_driver.decode` to fall back to `cp1252` (or `TEXTUAL_FALLBACK_ENCODING`) when non‑UTF‑8 bytes arrive. Tests: `tests/test_timestamp_textual_lenient_input.py`.
- v0.1.5 (2025-11-11): Fix script entry NameError by defining the lenient hook before `main()`/`__main__` guard; add `tests/test_timestamp_textual_entry_order.py` to ensure running the script directly doesn’t raise NameError and exits cleanly.
- v0.1.6 (2025-11-11): Add tests: constraints append behavior (`tests/test_timestamp_constraints_append.py`), lenient warn-once (`tests/test_timestamp_textual_lenient_warn_once.py`), preflight success path (`tests/test_timestamp_textual_preflight_success.py`), and timestamp formatting (`tests/test_timestamp_format_line.py`).
- v0.1.7 (2025-11-11): Add CLI flags to TimestampLogApp script: `--lenient-input` to enable decode fallback and `--fallback-encoding ENC` to select the fallback codec (default `cp1252`). Test `tests/test_timestamp_textual_cli_lenient.py` verifies the flag path without launching a real UI.
 - v0.1.8 (2025-11-11): Strengthen lenient input: in addition to patching `linux_driver.decode`, also patch `linux_driver.read` to sanitize non‑UTF‑8 bytes (`fallback → UTF‑8`) before they reach the decoder. This addresses cases where the driver binds the original `decode` at definition time.
 - v0.1.9 (2025-11-11): Add `timestamp_tui.sh` wrapper which sets UTF‑8 locale, enables `iutf8`, and runs the app with `--lenient-input --fallback-encoding cp1252`. Test `tests/test_timestamp_shell_wrapper.py` asserts wrapper contents.
 - v0.1.10 (2025-11-11): Ensure `timestamp_tui.sh` has executable bit set in repo workspace.
 - v0.1.11 (2025-11-11): Document copy‑paste one‑liner and step‑by‑step shell hardening commands.
- v0.1.11 (2025-11-11): Document quick shell hardening commands (UTF‑8 locale + `iutf8`) for ad‑hoc sessions.
- v0.1.12 (2025-11-11): Add `--right-margin N` to adjust Log right padding at runtime (env `TIMESTAMP_RIGHT_MARGIN`). Helps phones/SSH clients that clip the last column. Test: `tests/test_timestamp_cli_right_margin.py`.
- v0.1.13 (2025-11-11): Add `--pad-eol` (env `TIMESTAMP_PAD_EOL=1`) to append a single space when rendering each log line, without writing it to file—works around last-column clipping that margins don’t solve. Test: `tests/test_timestamp_cli_pad_eol.py`.
- v0.1.14 (2025-11-11): Make help reliable on mobile/SSH by adding `F1` binding for `toggle_help` (some clients translate `Ctrl+H` to backspace). Added tests: `tests/test_timestamp_help_binding_and_action.py`.
- v0.1.15 (2025-11-11): Make artifact Markdown view scrollable via CSS `overflow: auto`, allow focusing it (`ga` shortcut) and mark focusable. Tests: `tests/test_timestamp_artifact_scrollable.py`, `tests/test_timestamp_artifact_focus_shortcut.py`.
- v0.1.16 (2025-11-11): Replace the upper Log with a scrollable Constraints Markdown pane. It renders `constraints.md` directly and auto-refreshes. Shortcut `gi` focuses input, `ga` focuses artifact. Tests: `tests/test_timestamp_constraints_view_load.py`; updated CSS test to reference `#constraints-view` padding.
- v0.1.17 (2025-11-11): Default the Constraints pane to show the bottom (latest entries). On each load/refresh, we call `scroll_end()`; if supported, `auto_scroll=True` is set. Test updated in `tests/test_timestamp_constraints_view_load.py` to assert scrolling.
- v0.1.18 (2025-11-11): Make auto-scroll polite: it’s disabled while the constraints pane is focused, and can be turned off with `--no-auto-scroll` (env `TIMESTAMP_AUTO_SCROLL=0`). Tests: `tests/test_timestamp_no_auto_scroll_flag.py`, `tests/test_timestamp_constraints_focus_blocks_autoscroll.py`.
- v0.1.19 (2025-11-11): More tests for constraints pane: mtime-driven refresh (`tests/test_timestamp_constraints_refresh_mtime.py`), missing-file handling (`tests/test_timestamp_constraints_missing_file.py`), and `gi` input-focus shortcut (`tests/test_timestamp_input_focus_shortcut.py`).
- v0.1.20 (2025-11-11): Remove structured schedule output from the Refiner. `RefineSignature` now returns only `refined_artifact`; headless and TUI paths no longer write or parse `structured_schedule.json`. Tests updated accordingly.
- v0.1.21 (2025-11-11): Remove Critic module and input from Refiner. `RefineSignature` drops the `critique` field; headless and Textual flows no longer call or display Critic. TUI “Critique” panel removed. Tests updated.
- v0.1.22 (2025-11-11): Add `SystemState` Pydantic model with `last_artifact_update` (ISO). Passed to the Refiner right after `constraints` in both headless and Textual flows. Tests: `tests/test_system_state_refiner_input_headless.py`, `tests/test_system_state_refiner_input_textual.py`.
- v0.1.23 (2025-11-11): Make `nlco_textual.py` executable. You can now run it directly with `./nlco_textual.py`.
- v0.1.24 (2025-11-11): Repo housekeeping — commit and push TUI + pipeline changes (mobile SSH fixes, scrollable panes, constraints view overhaul, removal of Critic/structured schedule, new SystemState input) and tests.
- v0.1.25 (2025-11-11): Temporarily removed `nlco_textual.py` via `git rm`. The NLCO Textual app is disabled until restored; use the headless loop (`python nlco_iter.py`) or `timestamp_textual_app.py` for notes.
- v0.1.26 (2025-11-11): TimestampLogApp now tails `constraints.md` by default (last 200 lines) and scrolls to bottom. Flags/env: `--constraints-tail N` (env `TIMESTAMP_CONSTRAINTS_TAIL`) to adjust; `--no-auto-scroll` to stop snapping to end.
- v0.1.27 (2025-11-11): Tests for artifact scroll actions and fallbacks (`tests/test_timestamp_artifact_scroll_actions.py`).
 - v0.1.28 (2025-11-11): TimestampLogApp respects newlines in the constraints view by emitting Markdown line breaks. Test: `tests/test_timestamp_constraints_newlines.py`.

Structured Memory — Options (2025-11-11)
- Option A (light): add sectioned headings in `memory.md` (Policies/Procedures/Glossary) and constrain tools to edit within a selected section; add tests for section targeting.
- Option B (tags): require a tiny YAML front‑matter per block (`tags: [policy, time]`, `updated:`). Provide a minimal `append_memory --tags` helper and validate via tests.
- Option C (index JSON): maintain `.nlco/memory_index.json` with `{id, title, tags, updated, offset}` for quick lookup; unit‑test index build and lookup.
- Option D (RAG-lite): embed memory blocks once (e.g., 384‑d float per block) and select top‑k to show to the LM; start with a toy cosine impl + tests on selection only.
- Option E (recency window): inject only blocks updated in last N days into `context` when memory changed; add a test that verifies injection happens only on recent edits.
- Option F (write rules): add a 2‑rule acceptance gate: “non‑transient + reusable”; if not satisfied, do not write. Test with examples.
- Option G (CLI): tiny `./mem.py list|show|append` to manipulate memory deterministically; add smoke tests for the commands.

Quick Run — Textual Apps (cheat sheet)
- Install deps once: `source .venv/bin/activate || true; pip install -r requirements.txt`
- NLCO TUI (iterations UI): `python nlco_textual.py`
  - Keys: `r` run, `Ctrl+S` save, `Ctrl+L` clear, `q` quit
- Timestamp TUI (notes/constraints): `./timestamp_tui.sh` (recommended)
  - Alt: `./timestamp_textual_app.py --lenient-input --fallback-encoding cp1252`
  - Phone/SSH hardening: `stty iutf8 && export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8`

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

Right edge clipping (mobile SSH)
- Symptom: rightmost character of many lines is missing when running TimestampLogApp over JuiceSSH/Termux.
- Likely cause: terminal last-column/autowrap quirk or off‑by‑one width reporting over SSH. Textual/Rich will happily write into the last cell; some terminals fail to render it.
- Mitigation (2025-11-11): increased right padding on the `Log` widget (`padding: 1 2;`) so content stays one cell away from the terminal’s right edge.
- Quick check on client: compare `tput cols` vs `stty -a | grep -o 'columns [0-9]\+'`; they should match. Ensure `TERM=xterm-256color` and locale is UTF‑8. Minimal probe: `printf '%*sX\n' "$COLUMNS" ''` should visibly print an `X` in the last column.

Non‑UTF‑8 input over SSH (2025-11-11)
- Symptom: Textual prints a background thread traceback with `UnicodeDecodeError: invalid start byte 0x..` from `textual.drivers.linux_driver.decode`.
- Cause: the SSH client sends bytes that aren’t UTF‑8 (often CP1252 like 0x99 for ™). `iutf8` doesn’t transcode; it just changes line editing. Textual expects UTF‑8 and crashes.
- Fix on the remote shell: `export LANG=en_US.UTF-8; export LC_ALL=en_US.UTF-8; stty iutf8` (run inside tmux panes too). Verify with `locale charmap` → `UTF-8` and `stty -a` shows `iutf8`.
- Fix on the client (examples): set JuiceSSH/Termux character encoding to UTF‑8 and disable any legacy encoding. Avoid pasting content that yields CP1252 bytes; the hex for ™ should be `e2 84 a2` (UTF‑8), not `99`.
- Probe: run `xxd -p` then paste a ™ and press Enter; if you see `99`, your client isn’t sending UTF‑8.
- App behavior: we warn pre‑launch, but Textual may still show its own traceback if non‑UTF‑8 bytes arrive later. We prefer environment fixes over code fallbacks to keep the app minimal.
- Opt‑in fallback: set `TIMESTAMP_LENIENT_INPUT=1` (and optionally `TEXTUAL_FALLBACK_ENCODING=cp1252`) to enable a small monkeypatch that decodes bad bytes via cp1252. This is intentionally off by default to avoid hiding real issues.
- CLI alternative: run `./timestamp_textual_app.py --lenient-input [--fallback-encoding cp1252]` to toggle without env vars. Flags are parsed minimally and ignore unknown args.
Quick run (lenient input)
- One line: `./timestamp_textual_app.py --lenient-input --fallback-encoding cp1252`
- With env hardening for this shell:
  - `export LANG=en_US.UTF-8` (or keep `C.UTF-8`)
  - `export LC_ALL=en_US.UTF-8`
  - `stty iutf8`
  - `./timestamp_textual_app.py --lenient-input --fallback-encoding cp1252`

Shell wrapper (shortest path)
- Run: `./timestamp_tui.sh`
- It sets `LANG`/`LC_ALL`, runs `stty iutf8` if on a TTY, then executes the TUI with lenient input.

Quick shell hardening (no run)
- Per‑pane: `stty iutf8`
- Locale: `export LANG=en_US.UTF-8` and `export LC_ALL=en_US.UTF-8`
- Optional: `export TERM=xterm-256color`

Copy‑paste one‑liner (only harden shell)
- `stty iutf8 && export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 TERM=xterm-256color`

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
- After a constraints.md change (headless), the loop runs up to `MAX_ITERATIONS` (now 3) in one invocation.
- On scheduled hourly ticks (no changes), it runs exactly 1 iteration per tick.
- In the TUI, each press of `r` runs exactly 1 iteration.

Layout tweak (2025-11-07)
- Increased artifact editor area relative to constraints: `#constraints-pane` height 8, `#editor-row` height 30.
- Added `tests/test_nlco_textual_layout.py` to pin these values.

Constraints pane behavior
- The constraints pane now tails the last ~40 lines of `constraints.md`, so it reflects external edits (e.g., TimestampLogApp) rather than just the in-app message list.
- Input submissions now append directly to `constraints.md` (read/append, no in-memory rewrite). The iteration reads constraints fresh from the file at start.
- Test: `tests/test_nlco_textual_constraints_tail.py` ensures the pane shows only the tail.
- The pane scrolls to the end after refresh, so the bottom of the file is always visible.

File-first constraints behavior
- Run uses the live file contents, not an internal buffer.
- Test: `tests/test_constraints_append_live_read.py` appends twice and verifies the worker receives both lines.

Short‑term memory
- File: `short_term_memory.md`.
- Producers:
  - `TimewarriorModule`: appends a one‑line event whenever it starts/stops or prints a notable status.
  - `ExecutiveModule`: appends a one‑line trace per tool action when used (not currently wired in headless; TUI doesn’t invoke ExecutiveModule).
- Consumers: none at runtime; we don’t read it back into model context today. It’s for lightweight, append‑only breadcrumbs.

Potential rough edges observed
- `nlco_iter.py` disables finished-check (`if False:`), so it may iterate indefinitely unless externally stopped.
- `nlco_textual.py` writes files in place; concurrent runs could clobber state.
- Timewarrior context: headless `nlco_iter.py` currently does not call `TimewarriorModule.run`, so no Timewarrior info is added to the model context. In the Textual UI, `TimewarriorModule.run` is invoked and its output is shown in the "Timewarrior" pane, but it is not injected into the `context` string passed to Critic/Refiner.
- Critic stage disabled (2025-11-08): We skip the Critic call and pass an empty critique to Refiner. The TUI shows “Critic disabled” in the Critique panel.
- Planner stage: In the Textual UI we call `PlanningModule.run` and show its output; in headless `nlco_iter.py` the planner is instantiated but not called yet.

Future test ideas
- Add a Textual `App.run_test()` smoke test to ensure `NLCOTextualApp` composes and updates logs without launching a real UI.
- Validate that running one iteration updates the artifact. Structured schedule JSON is no longer produced by default.
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
Memory handling (summary, 2025-11-11)
- File `memory.md` is the persistent knowledge base; edits are made only when durable info should be kept.
- Module `MemoryModule` runs a small ReAct loop with tools `show_memory`, `replace_memory`, `append_memory`, `reset_memory` and writes back only if changes occurred.
- Headless and Textual flows both use the primary LM for memory updates; a short result string is printed to the Memory pane when changes happen.
- We don’t inject `memory.md` back into the model context yet (display-only except for edits). Short-term breadcrumbs go to `short_term_memory.md` separately.
