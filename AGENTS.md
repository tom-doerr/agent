Agent Notes (updated 2025-11-13)

- TUIs at a glance:
  - `timestamp_textual_app.py` (TimestampLogApp): capture constraints and view `artifact.md` (Markdown). It doesn’t run NLCO.
  - `agent_manual_pkg/src/agent_manual_pkg/tui.py` (Agent Manual TUI): interactive agent runner (satisfaction, memory, DSPy logs).
  - Legacy `nlco_textual.py` was removed; use the two TUIs above instead.
- Headless alternative is `nlco_iter.py` (console loop). Run: `python nlco_iter.py`.
- You do NOT need both at once; the TUI runs iterations itself. Avoid concurrent runs (shared files).
- Run commands:
  - Timestamp (wrapper, recommended): `./timestamp_tui.sh`
  - Timestamp (one-liner, hardened): `stty iutf8; LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 ./timestamp_textual_app.py --lenient-input --fallback-encoding cp1252`
  - Agent Manual: `python -m agent_manual_pkg.cli` (supports `--model` and `--max-tokens`).
- Files touched: none (informational change only).

Things to keep in mind
- Textual and Rich must be installed to run the Timestamp TUI.
- MLflow is optional for headless; structured schedule JSON is no longer produced by the refiner.
- Timestamp TUI default paths now live under the user’s private directory:
  - Default base: `~/.nlco/private` (override with `NLCO_PRIVATE_DIR`).
  - Resolved files: `constraints.md`, `artifact.md` in that directory.
  - Override per-file via env: `TIMESTAMP_CONSTRAINTS_PATH`, `TIMESTAMP_ARTIFACT_PATH` or CLI flags `--constraints-path` / `--artifact-path`.
- `timestamp_textual_app.py` appends to the resolved constraints file and can be used alongside NLCO tools, but beware of concurrent writes to the same file.

Path migration note (2025-11-13)
- We did NOT move any existing `constraints.md`/`artifact.md`. They remain at repo root, untracked.
- To keep using them without moving: `TIMESTAMP_CONSTRAINTS_PATH="$PWD/constraints.md" TIMESTAMP_ARTIFACT_PATH="$PWD/artifact.md" ./timestamp_textual_app.py`.
- To migrate to the new defaults (`~/.nlco/private`):
  - One‑liner (hardened): `IFS=$'\n\t'; set -euo pipefail; umask 077; base="${NLCO_PRIVATE_DIR:-$HOME/.nlco/private}"; install -d -m 700 "$base"; for f in constraints.md artifact.md; do src="$PWD/$f"; dst="$base/$f"; if [ -f "$src" ] && [ ! -e "$dst" ]; then mv -- "$src" "$dst" && echo "moved $f -> $dst"; else echo "skipped $f"; fi; done`

Path migration executed (2025-11-13)
- On this machine, we moved `artifact.md` → `~/.nlco/private/artifact.md` and found `~/.nlco/private/constraints.md` already present; repo‑root `constraints.md` was untouched.
- TUI now reads/writes from the private paths by default; override via `TIMESTAMP_CONSTRAINTS_PATH` / `TIMESTAMP_ARTIFACT_PATH` if needed.
 - Context now includes weekday explicitly: `Datetime: YYYY-MM-DD HH:MM:SS (Friday)` for better temporal grounding.
- Auto-backups: Before any write to `constraints.md`, we snapshot the current file to `.nlco/backups/{hourly|daily|weekly}/constraints-*.md` if the period’s file doesn’t exist yet. Env override: `NLCO_BACKUP_DIR`.
- Constraints tail sizing: In `timestamp_app_core`, tail now always derives from pane height (tail = max(height - 2, 1)). The old `TIMESTAMP_CONSTRAINTS_TAIL` numeric env is ignored for rendering.
- Mobile SSH tip: some clients clip the last column. Use either `--right-margin N` (env `TIMESTAMP_RIGHT_MARGIN`) or `--pad-eol` (env `TIMESTAMP_PAD_EOL=1`) to add space at the right; both affect rendering only (no file changes).

Key bindings (Timestamp TUI)
- `gi` focus input • `ga` focus artifact • `F1` toggle help (more reliable than `Ctrl+H` on some phones/SSH) • `Ctrl+C` exit • `PageUp/PageDown` scroll artifact.

Next Steps (2025-11-13)
- 46a. Wire `TimewarriorModule.run()` into `nlco_iter.iteration_loop()` behind env `NLCO_TIMEW=1`; log a short status line and add 2 unit tests (timew present/absent). Recommended.
- 46b. Add a minimal “unchanged twice” stop rule to headless iterations to prevent endless runs; 2 tests (no-change stops, change resets counter).
- 46c. Apply `TIMESTAMP_RIGHT_MARGIN` padding in `timestamp_app_core.TimestampLogApp` (Constraints Markdown) and add one style assertion test. (Tracking.)
- 46d. Prune remaining legacy references to `nlco_textual.py` in docs and code comments; keep the file but mark clearly as deprecated.
- 46e. Harden JSONL model logging for path errors (permission/dir missing) with a tiny try/except and one test; keep code minimal.
- 46f. (Done) Lightweight advisory file lock to avoid simultaneous writes to `constraints.md` when headless + timestamp/web app run together.
  - New: `file_lock.locked_file(path, mode='a+')` (fcntl LOCK_EX; Linux only).
  - Used by: `constraints_io.append_line`, `timestamp_textual_app._append_to_constraints`, `webapp/nlco_htmx/utils.write_constraints_entry`.
  - Test: `tests/test_constraints_locking_utils.py` spawns two processes appending concurrently; asserts one heading and all lines present.

Proposed Next Steps (80)
- 80a. Split `TUI.apply_memory_updates` into `*_create/_update/_delete` helpers with one focused unit test. Minimal code; lowers CC hotspot. (Recommended.)
- 80b. Style cleanup in `tui.py`: remove semicolons flagged by ruff (E702/E703); no behavior change; quick win + keep lint clean.
- 80c. Wire `TimewarriorModule.run` into `nlco_iter` behind `NLCO_TIMEW=1` with 2 tests (timew present/absent). Small, controlled change toward earlier goals.
- 80d. Add a tiny `/help` command that echoes HelpScreen text into `#log`; add one assertion in tests to lock UX.

Shell hardening cheats
- One-liner (ad‑hoc): `stty iutf8; LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 ./timestamp_textual_app.py --lenient-input --fallback-encoding cp1252`
- Persistent (bash/zsh): add `[ -t 0 ] && stty iutf8 || true` to your shell rc.

Models & budgets (NLCO iter)
- Primary LM: `deepseek/deepseek-reasoner` with `max_tokens=40000` (see `nlco_iter.py`).
- Support LM for subsystems: `deepseek/deepseek-chat` with `max_tokens=4000`, `temperature=0` (used in various support modules).
- Memory now uses the primary LM (reasoner) in headless.

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

Timestamp TUI complexity reductions (2025-11-12)
- Merged CLI/TTY preflight across modules: `timestamp_textual_app.py` now delegates to `timestamp_app_core` for CLI parsing and UTF‑8 TTY checks, with a tiny wrapper that preserves the `stty iutf8` behavior required by tests.
- Extracted `_build_append` to assemble constraint writes; keeps `_append_to_constraints` linear and short.
- Kept richer lenient‑input helper in wrapper (prints one warning, patches `read`) since tests assert those messages; core retains a minimal variant.
- Result: wrapper no longer has any CC ≥ C; worst offenders are B(10/8/6). Core remains B‑level for `_ensure_utf8_tty` and `_parse_cli`.
- Constraints pane: factored wrapper’s constraints logic into helpers — `_md_preserve_lines`, `_maybe_scroll_constraints_end`. The old `_tail_env` helper was removed; the wrapper now derives the tail from the pane height (tail = max(height − 2, 1)), matching the core. `_load_constraints` stays straight‑line and ≤ B. Tests updated accordingly.
  - Added tests: `tests/test_timestamp_constraints_helpers.py` covers `_tail_env` defaults/values/invalids, newline preservation, and autoscroll focus/no-focus behavior.

Legacy: Old Vim Input
- `_OldVimInput` (previously in `timestamp_textual_app.py`) has been removed. The app uses `VimInput` from `timestamp_vim_input.py`.

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
- v0.1.23 (2025-11-11): (historical) `nlco_textual.py` was made executable. This TUI is now legacy and not maintained.
- v0.1.24 (2025-11-11): Repo housekeeping — commit and push TUI + pipeline changes (mobile SSH fixes, scrollable panes, constraints view overhaul, removal of Critic/structured schedule, new SystemState input) and tests.
- v0.1.25 (2025-11-11): (historical) `nlco_textual.py` removal was planned. The file may still be present but should be treated as deprecated; use headless loop (`python nlco_iter.py`) or `timestamp_textual_app.py`.
- v0.1.26 (2025-11-11): TimestampLogApp now tails `constraints.md` by default (last 200 lines) and scrolls to bottom. Flags/env: `--constraints-tail N` (env `TIMESTAMP_CONSTRAINTS_TAIL`) to adjust; `--no-auto-scroll` to stop snapping to end.
- v0.1.27 (2025-11-11): Tests for artifact scroll actions and fallbacks (`tests/test_timestamp_artifact_scroll_actions.py`).
 - v0.1.28 (2025-11-11): TimestampLogApp respects newlines in the constraints view by emitting Markdown line breaks. Test: `tests/test_timestamp_constraints_newlines.py`.
 - v0.1.29 (2025-11-12): Remove unused `_OldVimInput` from `timestamp_textual_app.py`; the TUI relies solely on `VimInput`.
- v0.1.30 (2025-11-12): Add hourly/daily/weekly auto-backups for `constraints.md` (locked writes). New module `backups.py`; used by `constraints_io`, `timestamp_textual_app`, and HTMX utils. Tests: `tests/test_constraints_backups.py`.
 - v0.1.31 (2025-11-12): Constraints tail now always tracks pane height in `timestamp_app_core`. Tests: `tests/test_timestamp_constraints_tail_auto.py` and updated display/tail default tests.
- v0.1.32 (2025-11-12): Ran `ruff check .` across repo; 397 findings, 166 auto-fixable. Consider adding a minimal `pyproject.toml` Ruff config and staged fixes.
- v0.1.33 (2025-11-12): Applied safe Ruff auto-fixes (`ruff check . --fix`). Findings reduced to 221 from 397; remaining include E402/E70x/F841 and a few F821/E722. No code semantics changes intended.
- v0.1.34 (2025-11-12): Added minimal Ruff config `.ruff.toml` (py311, line-length 100, ignore E501; per-file ignores for legacy/intentional patterns; excluded one experimental file). Current findings with config: 102.
- v0.1.35 (2025-11-12): Fixed high-signal Ruff issues: F821 in `agent_manual_b.py`, `interactive_chat.py`, `textual_dspy/app.py`; E722 in `abbrev_decoder/...` and `online_optimization_system.py`; minor F841 cleanups. Added targeted per-file ignores for tests, world_model, and submodules. `ruff check` now passes clean with `.ruff.toml`.
 - v0.1.36 (2025-11-12): Simplify Timestamp TUI constraints pane — wrapper tail derives from visible pane height; env `TIMESTAMP_CONSTRAINTS_TAIL` is ignored for rendering. Removed `_tail_env`. Tests updated: `tests/test_timestamp_constraints_tail_view.py`, `tests/test_timestamp_constraints_helpers.py`, and `tests/test_timestamp_constraints_newlines.py` adjusted to inject pane height.
 - v0.1.37 (2025-11-12): Delegate wrapper helpers to core: added tiny shared helpers in `timestamp_app_core.py` (`md_preserve_lines`, `constraints_tail_from_height`, `scroll_end`) and made the wrapper call them. Added `tests/test_timestamp_constraints_equivalence.py` to assert wrapper/core render identical content for the same pane height.
- v0.1.38 (2025-11-12): Wrapper now respects `TIMESTAMP_CONSTRAINTS_ROWS` like the core. On mount, it sets `#constraints-container` height and uses it to derive tail (`rows-2`). Added `tests/test_timestamp_constraints_rows_env_wrapper.py` to validate height + tail.
 - v0.1.39 (2025-11-12): Unified TUI apps: `timestamp_textual_app.TimestampLogApp` now subclasses the core `timestamp_app_core.TimestampLogApp` to remove duplicate CSS/compose and reuse helpers. Wrapper overrides only: key bindings, timers/refresh, input submit formatting, help toggle, artifact scroll actions, and a focus‑aware `_scroll_constraints_end` (skips autoscroll when constraints pane focused). Tests added: `tests/test_timestamp_constraints_equivalence.py` (wrapper vs core rendering), `tests/test_timestamp_artifact_scroll_helpers_delegate.py` (wrapper delegates to core scroll helpers).
 - v0.1.40 (2025-11-12): Extract constraints append formatting to shared helper `constraints_io.build_append_block(existing, needs_heading, date_str, line)`. Wrapper now uses it in `_append_to_constraints`. New tests: `tests/test_constraints_append_helper.py` covers first-entry, same-day, and next-day w/o trailing newline.
 - v0.1.41 (2025-11-12): Add smoke tests using Textual `run_test()` for both core and wrapper TimestampLogApp to ensure they compose and render without launching a real UI (`tests/test_timestamp_smoke_run_test.py`).
 - v0.1.42 (2025-11-12): Wrapper CLI adds `--constraints-rows N` to set `TIMESTAMP_CONSTRAINTS_ROWS` (mirrors core env). Test: `tests/test_timestamp_cli_constraints_rows.py`.
- v0.1.43 (2025-11-12): HTMX writer now uses shared `build_append_block` for consistent constraints formatting. Updated `webapp/nlco_htmx/utils.write_constraints_entry`. New test `tests/test_web_htmx_append_block_consistency.py` covers next-day insert with missing trailing newline.
- v0.1.44 (2025-11-12): Change timestamp format from `HHMM` to `HH:MM:SS` across TUI and HTMX. Updated `_format_line` in `timestamp_textual_app.py` and `write_constraints_entry` in `webapp/nlco_htmx/utils.py`. Tests updated accordingly (Textual app formatting, HTMX POST/API, and consistency test).
 - v0.1.45 (2025-11-12): Artifact pane now scrolls to the top by default (polite `auto_scroll` gating). Core calls `scroll_home` after load; wrapper inherits behavior. Added tests: `tests/test_timestamp_artifact_default_top.py` for core and wrapper.

Things learned / to keep in mind (2025-11-12)
- Two `TimestampLogApp` classes exist (core and wrapper). Their behaviors can drift; we aligned tailing behavior to reduce divergence. Consider consolidating or delegating constraints logic from the wrapper to the core in a future change.
- CLI still accepts `--constraints-tail` and sets `TIMESTAMP_CONSTRAINTS_TAIL` for backward compatibility, but the wrapper ignores it during rendering. Tests only assert env propagation.
- Textual's `Markdown.update` may emit a benign "no running event loop" message when called on stubbed views in tests; currently harmless and can be ignored.
- Helper naming: the core calls `_scroll_constraints_end`. For backward‑compat with older tests, the wrapper keeps `_maybe_scroll_constraints_end()` and forwards it to `_scroll_constraints_end()`.
 - Append logic centralization: both headless and TUI paths should use `constraints_io.build_append_block` for consistent spacing/heading behavior; today only the wrapper calls it. Consider adopting it in any other path that writes constraints to avoid drift.

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
- Legacy NLCO TUI: deprecated and not maintained; examples removed. Use headless `nlco_iter.py` or `timestamp_textual_app.py`.
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

Repo housekeeping (2025-11-13)
- README refocused on NLCO headless loop and Timestamp TUI. DeepSeek batch docs moved to a short subpackages note. Added hardened one‑liner and wrapper as primary run paths.
 - README polished for readability: compact contents list, consistent section headers, and concise quick‑start. No behavior changes.
 - README now features centered heading and Material‑style badges (shields.io); purely visual.
 - Pushed documentation commits to origin/main.

Nootropics log (read-only)
- NLCO Textual UI now shows the last 72h of entries from `~/.nootropics_log.jsonl` in a side panel.
- Strictly read-only: the loader never writes or truncates the file.
- Env var `NLCO_NOOTROPICS_LOG` can point to a different JSONL file for testing.
- Minimal schema: each line must be JSON with an ISO `ts` field; lines without `ts` are skipped.
- Helper: `append_nootropics_section(context)` now appends the section; both headless and TUI call this instead of duplicating string glue.

Caching placement
- To maximize DSPy cache reuse, nootropics data is appended to the `context` input (not `constraints`).
- This keeps the `constraints` string stable across runs and pushes variable nootropics lines "behind" constraints in the prompt ordering.
- `nlco_iter.py` appends a `Nootropics (last 72h)` section at the end of `context`.

NLCO iter tests
- Added tests covering headless iteration behavior without touching real LMs:
  - `tests/test_nlco_iter_logging_and_schedule.py` ensures artifact update, structured schedule JSON write, and JSONL model logs with reasoning.
  - `tests/test_nlco_iter_nootropics_context.py` asserts nootropics appear only in `context` and that `constraints` remain unchanged.
  - Existing `tests/test_nlco_iter.py` validates async memory invocation and artifact write.
- Note: Running the entire repo test suite may fail due to duplicate test module names in `packages/deepseek-batch/tests/`. Run selective tests for NLCO iter.

Quick usage
- Headless (nlco_iter): scheduler decides when to run; finished-check is currently disabled.
- Timestamp app: `gi` focuses the input if focus is elsewhere; use Enter to append a timestamped line.

Iteration counts
- After a constraints.md change (headless), the loop runs up to `MAX_ITERATIONS` in one invocation. Override with `NLCO_MAX_ITERS` (default 3).
- On scheduled hourly ticks (no changes), it runs exactly 1 iteration per tick.
- In the TUI, each press of `r` runs exactly 1 iteration.

Layout tweak (2025-11-07)
- Removed NLCO TUI layout. Timestamp app has its own constraints height (8) documented below.

Timestamp app constraints
- TimestampLogApp now uses a fixed constraints height of 8 (`#constraints-container { height: 8; }`).
- Uses the shared `constraints_io.tail_lines` for tailing and scrolls to bottom by default.
- Test: `tests/test_timestamp_constraints_height.py` pins the height.
- Tests: `tests/test_timestamp_constraints_display.py` verifies the tail content and scroll-to-end behavior; `tests/test_timestamp_constraints_tail_default.py` ensures default tail (200) doesn't trim small files.
- Wrapper: `tests/test_timestamp_wrapper_exports.py` smoke tests that `timestamp_textual_app` exposes the app and helpers, and that `main()` wires parse/tty/lenient/run calls without launching a real UI.
- Env: `tests/test_timestamp_constraints_autoscroll_env.py` asserts `TIMESTAMP_AUTO_SCROLL=0` disables scrolling to end on reload.

Refactor: Timestamp app split
- `timestamp_vim_input.py` contains the minimal `VimInput` widget.
- `timestamp_app_core.py` holds the app class and helper functions.
- `timestamp_textual_app.py` is a thin wrapper that re-exports the app, helpers, and main().

Constraints pane behavior (Timestamp app)
 - Tail count = max(pane height − 2, 1). No implicit fallback.
 - Env `TIMESTAMP_CONSTRAINTS_ROWS=N` sets the container height to `N` rows at mount time and drives tail count (`N-2`).
 - Scrolls to the end after refresh so the bottom is visible by default.

File-first constraints behavior
- Shared helpers `constraints_io.tail_lines` and `constraints_io.append_line` centralize file tailing and appending.

Short‑term memory
- File: `short_term_memory.md`.
- Producers:
  - `TimewarriorModule`: appends a one‑line event whenever it starts/stops or prints a notable status.
  - `ExecutiveModule`: appends a one‑line trace per tool action when used (not currently wired in headless; TUI doesn’t invoke ExecutiveModule).
- Consumers: none at runtime; we don’t read it back into model context today. It’s for lightweight, append‑only breadcrumbs.

Potential rough edges observed
- `nlco_iter.py` disables finished-check (`if False:`), so it may iterate indefinitely unless externally stopped.
- Legacy `nlco_textual.py` also writes files in place; avoid running it alongside headless to prevent clobbering.
- Timewarrior context: headless `nlco_iter.py` currently does not call `TimewarriorModule.run`, so no Timewarrior info is added to the model context. In the Textual UI, `TimewarriorModule.run` is invoked and its output is shown in the "Timewarrior" pane, but it is not injected into the `context` string passed to Critic/Refiner.
- Critic stage disabled (2025-11-08): We skip the Critic call and pass an empty critique to Refiner. The TUI shows “Critic disabled” in the Critique panel.
- Planner stage: In the Textual UI we call `PlanningModule.run` and show its output; in headless `nlco_iter.py` the planner is instantiated but not called yet.

Future test ideas
- Add a Textual `App.run_test()` smoke test to ensure `NLCOTextualApp` composes and updates logs without launching a real UI.
- Validate that running one iteration updates the artifact. Structured schedule JSON is no longer produced by default.
- Model lineage update (2025-09-29)
  - DeepSeek docs state both `deepseek-chat` and `deepseek-reasoner` were upgraded to `DeepSeek-V3.2-Exp`; `chat` = non-thinking mode, `reasoner` = thinking mode. Over OpenRouter, reasoning appears in the `reasoning` field; via DeepSeek API it appears as `message.reasoning_content`.
Timewarrior Control — Conceptual Plan
- Current state: `TimewarriorModule` is wired for use but not yet invoked in the headless loop (`nlco_iter.py`). We plan to gate it behind `NLCO_TIMEW=1` and log a concise status line each iteration.
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
Code Quality Snapshot (2025-11-12)
- Refreshed Radon (post-constraints refactor): repo avg CC C ≈ 14.89. Top hotspots unchanged; constraints pane no longer contributes.
- Radon CC (C–F) hotspots (function · score) — latest:
  - `dspy_programs/memory_gan.main` · D (24)
  - `dspy_programs/taskwarrior_agent.main` · D (21)
  - `refiner_signature.render_schedule_timeline` · C (20)
  - `agent_manual_pkg.tui.TUI._process_job` · C (20)
  - `executive_module._execute_step` · C (16)
  - `nlco_iter.iteration_loop` · C (15)
  - `timewarrior_module._apply_decision` · C (15)
  - Full listing captured via `radon cc -s -n C -a .`.
- Radon MI: no grade‑C production files observed; `agent_manual_pkg/.../tui.py` remains MI “C” (legacy/test-heavy context). See `radon mi -s .`.

Actionable Quick Wins
- `timestamp_vim_input._handle_normal_mode_key` refactored into helpers — now below C and no longer listed.
- `nlco_iter.iteration_loop` refactored internally (helpers for reading state, building context, logging, and refiner print) with no behavior change; CC dropped below C.
- Agent TUI: unified command routing. Merged `_handle_inline_commands` into a single `_route_command`, and kept a tiny `_handle_command` wrapper for compatibility. Overlap eliminated for `/model`, `/modules`, `/max_tokens`, and `/layout`.
- Tests for unified router: added `test_layout_command_via_on_input` and a full `/modules` flow test to assert state transitions and configuration calls. The suite now covers `/layout`, `/model`, `/modules`, and `/max_tokens` (prompted and inline). See `agent_manual_pkg/tests/test_tui_router_commands.py` and existing tests.
- Split satisfaction update: `_process_job` now calls `_update_goals(prompt)` and `_update_score()` separately; added unit tests for each. Kept `_update_satisfaction` as a tiny wrapper for compatibility.
- Radon artifact (58d): added `scripts/gen_radon_report.py` which writes JSON + minimal HTML to `.nlco/meta/`. Test: `tests/test_radon_report.py` monkeys patches subprocess to avoid external dependency.
- `timestamp_app_core._load_constraints` split into small helpers (`_tail_count`, `_constraints_text`, `_scroll_constraints_end`) to simplify the constraints pane logic without behavior changes.
- Extract subroutines from `nlco_iter.iteration_loop` (context build, model calls, writeback) to lower CC without changing behavior.
- In `timewarrior_module._apply_decision`, add early returns for NONE/denied cases to flatten nesting.
Radon Snapshot (2025-11-12, 01:35)
- Repo average CC: C ≈ 14.89 (46 C–F blocks).
- Top hotspots unchanged: `agent_manual_pkg.tui.TUI.on_input_submitted` D(26), `dspy_programs/memory_gan.main` D(24), `dspy_programs/taskwarrior_agent.main` D(21), plus several C(20–16) functions.
- MI: no grade‑C production files; `agent_manual_pkg/.../tui.py` MI “C” (legacy/test heavy).
Security scan (2025-11-13)
- Scope: working tree, full Git history (patterns), and TruffleHog v2 entropy/regex pass.
- High‑risk secrets: none found (no private keys, AWS/GitHub/Slack tokens, Bearer tokens).
- .env files: only `.env.example` is tracked (placeholders). Any `.env*` in the tree are untracked.
- Emails: only test/example emails in content; commit metadata naturally contains author emails (not part of file contents).
- Nested repo note: `telegram-mcp-repo/.git/` exists locally but is not tracked; avoid bundling this folder when archiving.
- Largest blobs in history are code/log artifacts; no credential patterns detected in those blobs.

How to re‑run locally
- Quick grep (HEAD): `rg -n --hidden -P -g '!/.git' -g '!**/.git/**' -e '-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----' -e 'ghp_[A-Za-z0-9]{36,}' -e 'github_pat_[A-Za-z0-9_]{80,}' -e 'AKIA[0-9A-Z]{16}' -e 'ASIA[0-9A-Z]{16}' -e 'xox[bap]-' -e 'hooks\.slack\.com/services/' -e 'Authorization: Bearer [A-Za-z0-9_\-\.]+'
- Full history (patterns): `git rev-list --all | while read c; do git grep -I -n --full-name -E '(AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{80,}|xox[bap]-|hooks\\.slack\\.com/services/|BEGIN [A-Z ]+PRIVATE KEY|Authorization: Bearer )' "$c" || true; done`
- TruffleHog v2 (optional): `python -m pip install --user trufflehog==2.2.1 && trufflehog --regex --entropy=True --json --since_commit $(git rev-list --max-parents=0 HEAD | tail -n1) --branch $(git rev-parse --abbrev-ref HEAD) file://$PWD`

Recommended hardening
- Add a `pre-commit` hook with `gitleaks` or `trufflehog` (kept minimal; fail on verified secrets only).
- Enable GitHub secret scanning & push protection on the repo (if using GitHub).
- Convert `telegram-mcp-repo` to a proper submodule or add packaging excludes so its local `.git/` never ships.

PII scrub (2025-11-13)
- Removed from Git history and remote: `constraints.md`, `memory.md`, `short_term_memory.md`, `notes.md`, `info.md`.
- Local copies preserved (untracked) and added to `.gitignore`.
- Safety: mirror backup at `/tmp/agent-pre-scrub-mirror-YYYYmmdd-HHMMSS`, tag `pre-scrub-20251113-060334`, branch `backup/pre-scrub-20251113-060334`.
- Force-pushed rewritten history to `origin` (all branches + tags).
- If collaborators exist: they must `git fetch --all --prune` and hard reset their branches (history was rewritten).

Pre-commit secrets scan (2025-11-13)
- Hook: `.pre-commit-config.yaml` with a local `secrets-scan` that runs `scripts/secrets_scan.sh` over staged files.
- Patterns are high-confidence only (no entropy): private keys, GitHub tokens, GitHub PATs, AWS AKIA/ASIA, Slack webhooks, Bearer tokens.
- Setup once: `python -m pip install --user pre-commit && pre-commit install`
- Run ad-hoc: `bash scripts/secrets_scan.sh $(git diff --cached --name-only)`
- Tests: `tests/test_secrets_scan.py` covers clean and leaked cases.

PII double‑check (2025-11-13)
- Local repo: no occurrences of `constraints.md`, `memory.md`, `short_term_memory.md`, `notes.md`, `info.md` in any commit; high‑risk patterns only appear in documentation and the scan script (not secrets).
- Remote `main`: clean (no target files present).
- Remote PR refs: `refs/pull/{1..17}/head` still contain the removed files (GitHub stores PR heads separately). Action: close these PRs and recreate from the new `main`. GitHub will GC unreachable objects over time; to accelerate removal, contact GitHub Support.
- Re‑run locally: see “How to re‑run” in Security scan; remote check: `git clone --mirror $REPO_URL /tmp/repo.git && cd /tmp/repo.git && <same scans>`.

PII prevention policy (2025-11-13)
- Separation: personal logs/notes live outside the repo (default paths remain `constraints.md`, `memory.md`, `short_term_memory.md`, `notes.md`, `info.md` but are .gitignored and treated as local state).
- Blocking hooks: pre-commit `secrets-scan` is mandatory for contributors (`pre-commit install`). A second hook `forbid-paths` blocks staging any of the five Markdown files (matched by basename).
- CI gate (planned): GitHub Actions job runs the same scans on PRs and fails if secrets or forbidden paths are touched.
- Repo settings: enable GitHub “Secret scanning” and “Push protection” in Settings → Code security and analysis.
- Packaging: add `.gitattributes` `export-ignore` entries for those files to keep them out of `git archive` and release tarballs (planned).
- Incident playbook: if a leak occurs, run the scrub script (filter-repo), force-push with backups/tags, close PR refs, notify collaborators to hard reset.

Forbid-paths hook (2025-11-13)
- Hook: `.pre-commit-config.yaml` `forbid-paths` runs `scripts/forbid_paths.sh`.
- Deny-list: `constraints.md`, `memory.md`, `short_term_memory.md`, `notes.md`, `info.md` (basename match).
- Tests: `tests/test_forbid_paths.py` ensures safe files pass and forbidden names fail.

Release (continued)
- v0.1.46 (2025-11-13): Temporary headless hotfix — added a local `artifact.md` to avoid a first-run crash while investigating path alignment. The file remained ignored by Git.
- v0.1.47 (2025-11-13): Proper fix — headless now uses the shared resolver (`timestamp_app_core.resolve_artifact_path`) so `artifact.md` lives under `~/.nlco/private` (or env override). Removed the temporary repo file and added a tiny `FileNotFoundError` guard in `_read_artifact_and_state()` so first-run works without creating files up front. Tests: `tests/test_nlco_iter_paths_env.py`, `tests/test_nlco_iter_missing_artifact.py`.
- v0.1.48 (2025-11-13): Align headless constraints path with TUI — `CONSTRAINTS_FILE` now uses `timestamp_app_core.resolve_constraints_path()` (defaults to `~/.nlco/private/constraints.md`). Updated test `tests/test_nlco_iter_paths_env.py` to assert both artifact and constraints use shared resolvers.
- v0.1.49 (2025-11-13): Add shared resolvers for memory files — `resolve_memory_path()` and `resolve_short_term_path()` default to `~/.nlco/private/{memory.md, short_term_memory.md}` with env overrides. Headless now passes these to `MemoryModule` and `TimewarriorModule`. Tests updated: extended `tests/test_timestamp_paths_env.py` and `tests/test_nlco_iter_paths_env.py`.
- v0.1.50 (2025-11-13): Add tests asserting artifact does not auto-scroll when `TIMESTAMP_AUTO_SCROLL=0`: `tests/test_timestamp_artifact_no_autoscroll.py` (core + wrapper). Complements default-top tests.
- v0.1.51 (2025-11-13): Web app uses shared defaults for memory files — `WebConfig.memory_path` and `WebConfig.short_term_memory_path` now default via `timestamp_app_core.resolve_memory_path/_short_term_path`. Test: `tests/test_web_paths_resolvers.py`.
- v0.1.52 (2025-11-15): Memory diffs — on `replace_memory`, NLCO now prints a minimal unified diff to the console after a successful replacement. Kept implementation tiny (uses `difflib.unified_diff`). Test: `tests/test_memory_replace_diff.py` asserts diff headers and changed lines.
 - v0.1.53 (2025-11-15): Added `dspy_programs/concept_worldmodel_experiment.py`, a minimal concept-worldmodel experiment using DSPy + DeepSeek. Concepts are Pydantic models, tagging uses a DSPy `Signature` with Pydantic output, and metrics cover tagging quality plus concept-structure via logistic regression. New tests: `tests/test_concept_worldmodel_experiment.py` exercise synthetic data generation, the `ConceptTagger` Pydantic path, and the metric helpers.
 - v0.1.54 (2025-11-15): Made `dspy_programs/concept_worldmodel_experiment.py` executable (shebang + chmod) so it can be run directly as `./dspy_programs/concept_worldmodel_experiment.py` once dependencies and environment are configured.
- v0.1.55 (2025-11-16): Added `dspy_programs/concept_world_model.py`, a multi-step concept world-model + control experiment. It simulates a hidden-state reactor env, tags STATE concepts via an LLM, represents ACTION concepts in the same concept universe, fits a linear RewardModel on discounted returns `G_t ≈ f([state_concepts_t, action_bits_t])`, discovers high-reward concept pairs, asks the LLM to mint new abstract STATE concepts from those pairs, re-tags with the expanded schema, and runs a greedy actor that chooses actions by argmax predicted discounted reward.
 - v0.1.56 (2025-11-16): Added `dspy_programs/concept_world_model_v3.py`, an updated world-model + control script that fixes the pre-/post-action mismatch (training on PRE-action observations so Q(s_t, a_t) semantics are consistent), increases meltdown frequency via more aggressive glitch dynamics and lower thresholds, and uses a fully unified concept feature space: `X_t` is a K-dimensional vector over all concepts (STATE bits from the LLM, ACTION one-hots from the env, MODEL concepts currently zeroed). It computes Monte-Carlo returns `G_t` under a random policy, fits a linear RewardModel `G_t ≈ f(X_t)`, and acts greedily by embedding current STATE bits + candidate ACTION bits into `X_t` and taking argmax predicted return. Default run is small (`num_episodes=5`, `max_steps=12`) to keep LLM calls manageable.
- v0.1.57 (2025-11-17): Updated `dspy_programs/concept_world_model_v3.py` concept encoding. STATE concept activations now use a ternary scheme in training data: `1` = present, `-1` = explicitly absent, `0` = missing / not defined at that time (e.g. concepts introduced later). The LLM still returns boolean activations; the tagger maps them into {-1, 0, 1}. Future-occupancy analysis now treats presence as `value > 0` when building discounted occupancy signals, so `S_j(t)` remains “discounted future presence” even with the richer encoding. RewardModel features embed these ternary STATE values directly; ACTION concepts remain one-hot (0/1). Running v3 still requires valid OpenRouter credentials for DSPy.
- v0.1.58 (2025-11-17): Switched the default LM for `concept_world_model_v3` to Gemini 2.5 Flash over OpenRouter (`openrouter/google/gemini-2.5-flash`) and added a `--lm` CLI flag so the model can be overridden (e.g. `--lm openrouter/deepseek/deepseek-reasoner`). DSPy is now configured inside `main()` from this flag; the module still defines a default LM at import time for ad-hoc use, but script runs will reconfigure it based on `--lm`. Without a valid `OPENROUTER_API_KEY`, runs will fail during tagging or concept creation.
 - v0.1.59 (2025-11-17): Added `tests/test_concept_world_model_v3.py` to cover key pieces of the v3 world-model script without calling real LMs. Tests stub the DSPy `Predict` call to feed a fixed `activations_json` into `LLMConceptTagger.tag_state` and assert the ternary encoding (`[1, -1, 0]` for present / absent / missing). Additional tests exercise `EpisodeDataset.build_discounted_reward()` for (a) a no-meltdown episode (checking discounted Monte Carlo returns) and (b) an episode that ends in meltdown (reward at the meltdown step is 0 and earlier steps do not see any future reward beyond that point). A fourth test patches `LogisticRegression` and `ConceptCreator` so that `_analyze_concept_future()` deterministically appends a new meta-concept to the `Experiment.universe`, verifying that new STATE concepts are added correctly without depending on real model weights. Two more tests assert that malformed `activations_json` (invalid JSON or wrong schema) causes Pydantic `ValidationError` to propagate from `tag_state`, so schema violations fail loudly instead of being silently treated as zeros. Two further tests cover future-occupancy analysis: one asserts that when all concept future-occupancy targets are constant, `_analyze_concept_future()` prints the “all zero/constant” message along with per-concept `y` means (always 0/1); the other constructs a mixed target for a single concept and asserts that this message is not emitted. All eight tests pass with `pytest -q tests/test_concept_world_model_v3.py`.
 - v0.1.60 (2025-11-17): Made Pydantic validation failures in the concept-tagging path very visible at runtime. `LLMConceptTagger.tag_state` now wraps `ConceptActivations.model_validate_json(...)` in a `try`/`except ValidationError` block; on failure it uses `rich` to draw a red rule with a clear message, prints the raw `activations_json` payload, and then re-raises the original exception. This keeps the behavior non-fallback (errors still fail fast) while making it obvious in logs when the LLM returned malformed or schema-incompatible activations.
 - v0.1.61 (2025-11-17): Relaxed the default cosine-similarity threshold for future-occupancy meta-concept creation. `Experiment` now takes a `corr_threshold` parameter (CLI flag `--corr-threshold`, default `0.0`); `_analyze_concept_future` uses this instead of a hard-coded `0.8`. With the default, any positively correlated pair (sim > 0) is eligible, but we still cap additions with `max_new` and keep the “no structure” path when weight vectors are all zero. `Experiment.run_greedy_actor_demo` also prints `concepts_added_total` and `samples_total` in each step, and `_analyze_concept_future` reports how many concepts were created in that analysis plus the running total. To avoid sklearn shape errors after adding concepts, `_greedy_action` resets the `LinearRegression` coefficients when the feature dimension changes.
 - v0.1.62 (2025-11-17): Removed vestigial `baseline_*` fields from `run_greedy_actor_demo` output; the earlier Monte Carlo warmup (which had populated `baseline_overall_mean` and `baseline_action_means`) is gone, so those baselines were always 0/empty and misleading. Tests now assert that per-step logs contain no `baseline_mean_G` or `baseline_action_means` strings. A `--difficulty` CLI flag was added to `Experiment`/`ReactorEnv` to scale instability: difficulty >1.0 multiplies glitch probability, scales stress/margin drift, and tightens meltdown thresholds slightly; difficulty <1.0 does the opposite. Default remains 1.0.

Next Steps (2025-11-13)
- 90a. Add a test verifying artifact does not auto‑scroll when `TIMESTAMP_AUTO_SCROLL=0` (symmetry with constraints). Recommended.
- 90b. Optional: CLI/env toggle to select artifact top/bottom; add 1–2 tests.
- 90c. Consider `constraints_io.append_daily_line(now, message)` helper to encapsulate last‑date detection; 1 unit test.

Things learned (2025-11-13)
- Align paths across headless + TUI to avoid surprises; using the shared resolver eliminates the repo-root dependency.
- Minimal guard (not a broad fallback): treating missing artifact as empty input allows first-run without creating files ahead of time.
Things learned (2025-11-15)
- Concept-worldmodel experiments live under `dspy_programs/concept_worldmodel_experiment.py`; they rely on DSPy’s Pydantic integration (Pydantic models as input/output fields) and scikit-learn for simple logistic-regression structure probes. Tests stub the DSPy `Predict` call so no real LM traffic occurs; when adding similar experiments, follow this pattern to keep tests fast and offline-friendly.
- When adding new Python scripts meant to be run directly (not just imported), add a shebang and ensure the file has the executable bit set in the workspace so `./path/to/script.py` works without extra chmod steps.
- Running `./dspy_programs/concept_worldmodel_experiment.py` without OpenRouter credentials currently fails with a litellm `AuthenticationError` (HTTP 401). This is expected; configure `OPENROUTER_API_KEY` (and any other dspy/OpenRouter settings) in the environment before running the full experiment to avoid noisy stack traces and repeated failures.
- Invoking the concept-worldmodel script via `zsh -ic ./dspy_programs/concept_worldmodel_experiment.py` does not change this requirement; an interactive shell run still needs valid OpenRouter credentials. A previous run was aborted mid-call, but after sourcing `~/.env_api_keys` in bash the script completed end-to-end and printed tagging + structure metrics, confirming the wiring works with a valid key.
- The concept-worldmodel script seeds both Python’s `random` and NumPy (`random.seed(42)`, `np.random.seed(42)`) at the start of `main()`, so the synthetic dataset (observations + ground-truth labels) is reproducible across runs. LM outputs may still vary depending on the model’s temperature/config.
- The concept-worldmodel script now prints the full concept list once at startup via `print_concepts()` (id + definition for each concept) before generating data. Tests (`test_print_concepts_lists_ids`) assert this helper emits all concept IDs, so future changes to the concept set must keep the description output in sync.
- The concept-worldmodel script logs the first few examples (indices, observations, true labels, and predicted activations) to `.nlco/meta/concept_worldmodel_samples.jsonl` via `log_samples_jsonl()`. Tests (`test_log_samples_jsonl_writes_lines`) cover the helper; when debugging or comparing runs, inspect this JSONL rather than scrolling back through the full console output.
- Concept-worldmodel hyperparameter search:
  - For the structure models (`C_j ~ other concepts`), we now run a tiny random hyperparameter search over logistic regression settings **once, globally**, instead of per concept:
    - We sample three `(C, max_iter)` pairs with `C ~ 10**U[-2,2]` and `max_iter ~ U{200..800}`, fit a model for each concept and each trial, and aggregate validation CE/acc/AUC + total ΔCE across all non-degenerate concepts.
    - We print a compact table (`Hyperparam search for structure models (shared across concepts)`) showing all trials and their average scores plus `sum_ΔCE`, then select the best trial by `sum_ΔCE` and reuse its `(C, max_iter)` for all per-concept reports and ΔCE_self.
  - The usefulness summary is labeled “ΔCE_self (predictable from others)” and sorted by ΔCE_self descending, with `frac_of_total` showing each concept’s share of the total ΔCE_self sum. A one-line explanation clarifies that `ΔCE_self = baseline_CE − best_CE` for predicting that concept from the others, so higher values mean a concept is more structured/predictable in the learned concept space.
- Concept-worldmodel pipeline (detailed notes):
  - High-level goal: let an LLM create and use **abstract concepts** as a compact world model, then use a separate ML layer to learn structure over those concepts (predictive relations, redundancies, higher-level abstractions). The outer objective is “make the system less surprised” (better prediction / compression), not just classify labels.
  - Concept representation: concepts are treated as **predicates over observations** (`C(o) ∈ {0,1}` now, optionally [0,1] later). In code we keep them as Pydantic `Concept(id, definition)` objects so they can be passed into DSPy signatures dynamically and used as stable keys in matrices.
  - Binary vs scalar activations: v1 uses **binary activations** (0/1) for simplicity and for clean metrics; the design allows upgrading to scalar scores (`[0,1]` confidence) later, with thresholding for discrete models and raw scores for richer ML.
  - What makes a concept “good”:
    - Compression/MDL view: adding the concept should reduce `L(data | K) + L(K)`; i.e. it lets us encode many observations with fewer bits.
    - Predictive view: the concept should improve prediction of external targets or of other concepts.
    - Invariants view: conditioned on the concept being true, some other properties become very stable (low entropy).
  - Concept–observation matrix: for N observations and K concepts we build `Z ∈ {0,1}^{N×K}` (or scores). On top of this, we run standard ML:
    - For each concept `C_j`, train logistic regression `C_j ~ Z_{-j}`; compare baseline CE (constant pos_rate) vs model CE to get ΔCE, plus acc/AUC.
    - Concepts that are highly predictable from others are likely composite/redundant; concepts that are hard to predict are more primitive/independent.
    - The same machinery can be pointed at external labels (e.g. failure) to get concept importances.
  - Causality vs compression: we treat MDL/compression + predictive fit as a **pragmatic heuristic** for structural learning in concept space, not as full causal discovery. Score-based causal-learning ideas inspire the design (simpler factorisations that still predict well) but we do not try to identify causal direction; we just learn “useful, stable dependencies” between concepts.
  - Synthetic worlds: to avoid contamination from real-world knowledge, we use synthetic simulators with hidden numeric rules. The current script uses a **reactor log** world (hidden `stress, margin, glitches, tone` → textual logs + concept labels `STRAINED_CORE`, `THIN_MARGIN`, `STORMY_CHANNEL`, `AGITATED_OPERATOR`, `CRITICAL_MODE`), but the same pattern could be reused for other toy worlds.
  - Logprobs and fuzziness: the inner concept layer does not require token logprobs; we can treat the LLM as a black-box concept tagger. Logprobs are only needed if the outer objective is “reduce raw text perplexity given a world-model prefix”. For concept learning and structure analysis we work entirely in concept space (bits/scores + CE/ΔCE).
  - Concept auto-regression and higher-level concepts: in the full design, we:
    - Fit sparse models `C_j ~ other C`s to see which concepts cluster and which combinations have strong predictive power.
    - Use those patterns (e.g. `A & B & ¬C`) as candidates for **new higher-level concepts**, then ask the LLM to propose a short natural-language definition from positive vs negative examples.
    - Keep both: a machine-side pattern (function of base concepts) and a compressed text definition (handle for the LLM).
  - Multi-step / future-aware concepts: for sequential data, instead of `failure_step_23` we define trajectory-wide labels like `WILL_EVENTUALLY_FAIL(t)` or `FAIL_WITHIN_H(t)` and treat them as concepts that depend on current state. This lets us train per-step “failure risk” concepts without exploding the concept set by time index.
  - Text definitions and compression: for new composite concepts, the definition prompt should not expose the raw logical pattern (A, B, C). Instead we show positive and negative examples and ask for a short abstraction, explicitly discouraging “laundry list” definitions. We can enforce compression by constraining length and rejecting definitions that are not materially shorter than spelling out the components.
Things learned (2025-11-16)
- The multi-step concept world-model script lives at `dspy_programs/concept_world_model.py`. It keeps the LLM’s role minimal (STATE tagging + concept naming) and pushes control and value learning into a tiny linear RewardModel over concept bits, plus a greedy actor that selects actions by predicted discounted reward.
- The new script currently uses bare `dspy.InputField()` / `dspy.OutputField()` (no positional `...`) in its Signatures; older `InputField(...)` usage now fails against the local DSPy version with `TypeError: InputField() takes 0 positional arguments but 1 was given`. When adding new Signatures, follow the zero-positional-args pattern so they stay compatible.
- Running `python dspy_programs/concept_world_model.py` without valid OpenRouter credentials fails during the first tagging pass with a `litellm.AuthenticationError` (“No auth credentials found” / HTTP 401) from the OpenRouter backend. This is expected; configure `OPENROUTER_API_KEY` (e.g., via `source ~/.env_api_keys`) before running the full multi-step experiment, especially since it makes many LLM calls (one per step, plus concept-creation calls).
- The multi-step script also seeds `random` and `numpy` inside `Experiment.run()` (`random.seed(42)`, `np.random.seed(42)`), so the synthetic trajectories (hidden state, actions under the random behavior policy, and meltdown events) are reproducible across runs. LLM outputs (STATE tags and new concept definitions) may still vary with model temperature/config.
- To keep runs tractable in this environment, `concept_world_model.py` now defaults to `num_episodes=5` in `main()`, which means ~50 LLM calls for the initial tagging pass plus a few more for the greedy-actor demo. Bigger runs (e.g., 40 episodes) are possible by editing the `Experiment` arguments or wiring a small CLI/env override, but be aware they scale linearly in LLM calls and wall time.
- For debugging transparency, `concept_world_model.py` now prints all LLM inputs and outputs for STATE tagging and concept creation: before each tagging call it prints the observation and the current STATE concept set (id + source), then prints the returned activation dict; before each new-concept call it prints the pattern concepts, pattern description, and a couple of positive/negative examples, followed by the generated concept id/definition. This is intentionally verbose and should be left as-is while we’re iterating on the world-model design; if it becomes too noisy for larger runs, consider gating it behind a simple verbosity flag or env var rather than removing it outright.
- The v3 script (`concept_world_model_v3.py`) keeps the same broad structure but makes a few semantic fixes and runtime tweaks:
  - RL semantics: episodes are logged with PRE-action observations (`obs_t`) and actions `a_t`, and Monte-Carlo returns `G_t` are computed from step t onward; the RewardModel is trained on `(obs_t, a_t, G_t)` so its predictions are genuinely Q-like for the random behavior policy. At inference time the greedy actor also operates on PRE-action observations, embedding STATE bits and each candidate ACTION bit into the unified concept vector before querying the RewardModel.
  - Environment tuning: glitch probability now ramps up more strongly with high stress/low margin, and the meltdown rule is relaxed to `stress > 85`, `margin < 25`, `glitches >= 2`, which produces meltdowns with reasonable frequency over ~10–15 steps. This gives the RewardModel a more informative target signal than the earlier almost-always-survive regime.
  - DSPy integration: to stay compatible with the current DSPy version, v3 uses `InputField(desc=...)` / `OutputField(desc=...)` and a JSON-string output (`activations_json`) for the tagging Signature, parsing into the `ConceptActivations` Pydantic model via `model_validate_json`. Avoid using a field named `labels` on Signatures, since that collided with internal attributes in earlier experiments and produced confusing `'function' object` errors at runtime.
  - Runtime: a full v3 run with `num_episodes=5` and `max_steps=12` (60 decision steps, plus 3 greedy episodes) completes in ~5 minutes in this environment with the current OpenRouter-backed DeepSeek model. Increasing episodes/steps will raise runtime roughly linearly due to one LLM call per state tag, so any future CI-style tests for this script should stub the LM instead of hitting the real endpoint.
  - LLM I/O visibility: like the original `concept_world_model.py`, v3 now prints all LLM inputs and outputs for STATE tagging and concept creation. For tagging it prints the STATE concept set once, then for each observation logs `[LLM TAG INPUT v3]` (index + full text) and `[LLM TAG OUTPUT v3]` (concept→0/1 dict). For concept creation (once we have strong pairs) it logs `[LLM NEW-CONCEPT INPUT v3]` with pattern concepts, description, and a couple of positive/negative examples, followed by `[LLM NEW-CONCEPT OUTPUT v3]` with the proposed id/definition. This is intentionally verbose for debugging; if it becomes cumbersome for larger experiments, consider adding a simple verbosity flag or env gate instead of removing the logs.
  - Output formatting: v3 now uses Rich (`rich.console.Console`, `rich.table.Table`) for key sections. The random-policy simulation, baseline stats, and train/test split are wrapped in `console.rule()` headers and printed with color; baseline per-action returns are shown in a small Rich table. The greedy-actor demo prints one line per step with colored fields for the chosen action, predicted per-action returns, baseline means, and running average rewards (global + per-episode), plus colored meltdown/no-meltdown markers. The LLM tagging logs remain plain `print()` calls to keep them simple; only the high-level experiment/RewardModel/actor sections use Rich styling.
  - Control knobs: the `--episodes/--epochs` CLI arg now controls both (a) the number of random-policy episodes used to collect training data and (b) the number of greedy-actor episodes in the demo (we pass `num_episodes` into both phases). An additional `--epsilon` arg toggles epsilon-greedy exploration during the greedy phase; with `--epsilon > 0`, each step chooses a random action with probability ε instead of the argmax predicted return. This keeps the model-learning phase Monte-Carlo over a random policy, while allowing exploration in the evaluation/control phase without touching the RewardModel itself.
  - Environment hardness + reward: we simplified away the separate random warmup and now start directly in ε-greedy episodes with a trivial zero-initialized RewardModel. The env gained a simple `demand` variable (`"low"`/`"high"`) which is exposed in the observation text (“grid demand is modest” vs “grid demand is elevated; operators are asked to keep output up”). Reward is now demand-sensitive: meltdown yields a large penalty; otherwise we add a base survival reward plus an “output” term (push > steady > cool) that is rewarded when demand is high and mildly penalized when demand is low if output is far from a moderate level. This creates a minimal, sensible trade-off where “always cool” or “always push” is no longer obviously best; the agent must read both STATE concepts and demand text to balance safety vs output over time.
  - Minimal implementation scope: the current script covers the **first step only**:
    - Hand-defined concepts (5 reactor concepts).
    - Synthetic data with hidden numeric rules.
    - LLM tagging vs ground truth (acc/F1).
    - Concept-from-concept structure via logistic regression (ΔCE, acc, AUC).
    - A small JSONL log (`concept_worldmodel_samples.jsonl`) with a few observations, labels, and predicted activations for inspection.
    - No concept importance ranking, automatic concept creation, MDL selection, or sequence modeling yet—those are future layers on top of the same representation.
