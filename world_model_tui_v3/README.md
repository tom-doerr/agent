
# World Model TUI — v0.3.0

Textual TUI + DSPy program to compare two *world models* (weighted theories).
Each step: sample k theories (weight-proportional, w/o replacement), send both bullet lists + an observation to a judge (LLM or offline heuristic), then update weights with multiplicative weights.

## New in 0.3.0 (compared to 0.2.0)
- **Row-key–safe** table operations (prevents wrong-row deletes).
- **Non-blocking judge** (offloaded via `asyncio.to_thread` + retries) — keeps UI responsive.
- **Centralized observations** state; table is just a view.
- **Offline provider**: `local-heuristic` (no API keys required).
- **Max tokens** control in UI; clamped **η** reflected in the field.
- **Distribution tools**: Show top-5 per model + Gini; run summary after N.

## Install
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Providers
Pick one in the UI:
- **Local heuristic (offline)** — zero setup.
- **DeepSeek Chat / Reasoner** — export `DEEPSEEK_API_KEY` (OpenAI-compatible at `https://api.deepseek.com`).
- **Gemini 2.5 Flash / Flash-Lite** — export `GOOGLE_API_KEY`.

## Run
```bash
python -m world_model_tui
```
- Add theories for **A** and **B** (weights auto-normalize).
- Add observations.
- Choose provider, set `k`, `N`, `η`, `seed`, and `max tokens`.
- **Run N** (or **Step**). **Cancel** interrupts between iterations.
- Use **Show Dist** to print top-5 theories and Gini for both models.
- **Save/Load** persists/recovers the session (`world_model_tui_state.json`).

## Notes
- LLM temperature is fixed to **0** for more stable judgments.
- If a model’s weights collapse to ~0, normalization resets it to **uniform** (keeps exploration alive).
- The **offline judge** uses simple token overlap; it’s only for quick checks, not correctness.

## Extend
- Add calibrated scoring judges and soft updates.
- CSV import/export for theories and observations.
- A/B/n with more than two world models.
