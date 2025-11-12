#!/usr/bin/env python3

from __future__ import annotations
import asyncio
import json
import random
import functools
from dataclasses import dataclass, asdict
from typing import List, Optional

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Button, DataTable, Select, Label, RichLog
from textual.containers import Horizontal, Vertical, Grid
from textual import on


from .model import WorldModel, Theory, weighted_sample_without_replacement, multiplicative_update
from .dspy_judge import WorldModelJudge, LocalHeuristicJudge
from .llm_providers import configure_lm, LMConfigError
from .utils import cursor_row_index, topk_sorted, gini

@dataclass
class RunConfig:
    sample_k: int = 3
    iterations: int = 10
    eta: float = 0.1
    provider: str = "deepseek-chat"
    seed: int = 42
    max_tokens: int = 1024

STATE_FILE = "world_model_tui_state.json"

class ModelPanel(Vertical):
    def __init__(self, title: str, model: WorldModel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        self.title = title

    def compose(self) -> ComposeResult:
        yield Label(self.title, id=f"title-{self.model.name}")
        self.table = DataTable(id=f"table-{self.model.name}")
        self.table.add_columns("#", "Weight", "Theory")
        yield self.table
        with Horizontal():
            self.input_theory = Input(placeholder="new theory text", id=f"input-{self.model.name}")
            self.input_weight = Input(placeholder="weight (float)", id=f"w-{self.model.name}", value="1.0")
            yield self.input_theory
            yield self.input_weight
            yield Button("Add", id=f"add-{self.model.name}")
            yield Button("Del Sel", id=f"del-{self.model.name}")

    def refresh_table(self):
        self.table.clear()
        for i, t in enumerate(self.model.theories):
            self.table.add_row(str(i), f"{t.weight:.4f}", t.text)

    def delete_selected(self):
        idx = cursor_row_index(self.table)
        if idx is None:
            return
        if 0 <= idx < len(self.model.theories):
            del self.model.theories[idx]
            self.model.normalize()
            self.refresh_table()

class ObservationsPanel(Vertical):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table: DataTable | None = None

    def compose(self) -> ComposeResult:
        yield Label("Observations")
        self.table = DataTable(id="table-obs")
        self.table.add_columns("#", "Observation")
        yield self.table
        with Horizontal():
            self.input_obs = Input(placeholder="new observation text", id="input-obs")
            yield self.input_obs
            yield Button("Add", id="add-obs")
            yield Button("Del Sel", id="del-obs")
            yield Button("Show Dist", id="show-dist")

    def refresh_from(self, observations: List[str]) -> None:
        self.table.clear()
        for i, o in enumerate(observations):
            self.table.add_row(str(i), o)

    def selected_index(self) -> int | None:
        return cursor_row_index(self.table)

class ControlPanel(Grid):
    DEFAULT_CSS = """
    Grid {
        grid-size: 4 4;
        grid-gutter: 1 1;
    }
    """
    def __init__(self, cfg: RunConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cfg = cfg

    def compose(self) -> ComposeResult:
        yield Label("Provider / LLM")
        self.sel_provider = Select(
            options=[
                ("Local heuristic (offline)", "local-heuristic"),
                ("DeepSeek Chat", "deepseek-chat"),
                ("DeepSeek Reasoner", "deepseek-reasoner"),
                ("Gemini 2.5 Flash", "gemini-2.5-flash"),
                ("Gemini 2.5 Flash-Lite", "gemini-2.5-flash-lite"),
            ],
            value=self.cfg.provider,
            id="sel-provider",
        )
        yield self.sel_provider

        yield Label("Sample k (per model)")
        self.in_k = Input(value=str(self.cfg.sample_k), placeholder="k", id="in-k")
        yield self.in_k

        yield Label("Iterations N")
        self.in_n = Input(value=str(self.cfg.iterations), placeholder="N", id="in-n")
        yield self.in_n

        yield Label("Learning rate η (0..1)")
        self.in_eta = Input(value=str(self.cfg.eta), placeholder="eta", id="in-eta")
        yield self.in_eta

        yield Label("Seed")
        self.in_seed = Input(value=str(self.cfg.seed), placeholder="seed", id="in-seed")
        yield self.in_seed

        yield Label("Max tokens")
        self.in_maxtok = Input(value=str(self.cfg.max_tokens), placeholder="max tokens", id="in-maxtok")
        yield self.in_maxtok

        self.btn_run = Button("Run N", id="run-n")
        yield self.btn_run
        self.btn_step = Button("Step", id="step-1")
        yield self.btn_step
        self.btn_cancel = Button("Cancel", id="cancel")
        yield self.btn_cancel
        self.btn_save = Button("Save", id="save")
        yield self.btn_save
        self.btn_load = Button("Load", id="load")
        yield self.btn_load

class WorldModelTUI(App):
    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 5;
        grid-rows: auto auto 1fr auto auto;
        grid-cols: 1fr 1fr;
        grid-gutter: 1 1;
    }
    #header { column-span: 2; }
    #controls { column-span: 2; }
    #log { column-span: 2; height: 12; }
    #footer { column-span: 2; }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("s", "step_once", "Step"),
        ("r", "run_n", "Run N"),
        ("c", "cancel", "Cancel"),
        ("S", "save_state", "Save"),
        ("L", "load_state", "Load"),
    ]

    def __init__(self):
        super().__init__()
        self.model_a = WorldModel("A")
        self.model_b = WorldModel("B")
        self.cfg = RunConfig()
        self.judge = None  # WorldModelJudge or LocalHeuristicJudge
        self._cancel = False
        self._obs_index = 0
        self._observations: List[str] = []
        self.wins = {"A": 0, "B": 0}

    def compose(self) -> ComposeResult:
        yield Header(id="header", show_clock=True)
        with Horizontal():
            self.panel_a = ModelPanel("World Model A", self.model_a)
            self.panel_b = ModelPanel("World Model B", self.model_b)
            yield self.panel_a
            yield self.panel_b
        self.obs_panel = ObservationsPanel()
        yield self.obs_panel
        self.controls = ControlPanel(self.cfg, id="controls")
        yield self.controls
        self.log = RichLog(highlight=True, markup=True, id="log")
        yield self.log
        yield Footer(id="footer")

    def on_mount(self):
        random.seed(self.cfg.seed)
        if not self.model_a.theories:
            self.model_a.theories.extend([
                Theory("The sun rises in the east", 0.6),
                Theory("Stocks usually go up on Mondays", 0.4),
            ])
        if not self.model_b.theories:
            self.model_b.theories.extend([
                Theory("The sun rises in the west", 0.5),
                Theory("Stocks usually go down on Mondays", 0.5),
            ])
        self.model_a.normalize()
        self.model_b.normalize()
        self.panel_a.refresh_table()
        self.panel_b.refresh_table()
        self.obs_panel.refresh_from(self._observations)

    # --- Helpers ---
    def _configure_lm(self) -> bool:
        provider = self.controls.sel_provider.value
        try:
            self.cfg.seed = int(self.controls.in_seed.value.strip() or self.cfg.seed)
            random.seed(self.cfg.seed)
            self.cfg.provider = provider
            self.cfg.sample_k = max(1, int(self.controls.in_k.value))
            self.cfg.iterations = max(1, int(self.controls.in_n.value))
            eta_val = float(self.controls.in_eta.value)
            self.cfg.eta = max(1e-6, min(eta_val, 0.99))
            self.controls.in_eta.value = str(self.cfg.eta)  # reflect clamp
            self.cfg.max_tokens = max(64, int(self.controls.in_maxtok.value))
        except Exception:
            self.log.write("[red]Invalid numeric config (k/N/η/seed/max_tokens).[/red]")
            return False
        try:
            lm = configure_lm(provider, max_tokens=self.cfg.max_tokens, temperature=0.0)
            if provider == "local-heuristic" or lm is None:
                self.judge = LocalHeuristicJudge()
            else:
                self.judge = WorldModelJudge()
            self.log.write(f"[bold green]Provider:[/bold green] {provider}  [blue]max_tokens:[/blue] {self.cfg.max_tokens}")
            return True
        except LMConfigError as e:
            self.log.write(f"[bold red]LM config error:[/bold red] {e}")
        except Exception as e:
            self.log.write(f"[bold red]Unknown LM error:[/bold red] {e}")
        return False

    def _next_observation(self) -> Optional[str]:
        if not self._observations:
            return None
        val = self._observations[self._obs_index % len(self._observations)]
        self._obs_index += 1
        return val

    async def _call_judge_async(self, bullets_a: str, bullets_b: str, observation: str):
        # run potentially blocking judge call off the event loop with retries
        func = functools.partial(self.judge, model_a=bullets_a, model_b=bullets_b, observation=observation)
        for attempt in range(3):
            try:
                # Local heuristic is fast; but to keep flow uniform, still to_thread
                return await asyncio.to_thread(func)
            except Exception:
                if attempt == 2:
                    raise
                await asyncio.sleep(1.5 ** attempt)

    async def _run_once(self, observation: Optional[str] = None):
        if not self.judge and not self._configure_lm():
            return
        if self._cancel:
            self.log.write("[yellow]Run cancelled.[/yellow]")
            return
        k = self.cfg.sample_k
        eta = self.cfg.eta
        if observation is None:
            observation = self._next_observation()
            if observation is None:
                self.log.write("[yellow]No observations. Add one first.[/yellow]")
                return
        # sample k without replacement from each model
        sample_a = weighted_sample_without_replacement(self.model_a.theories, k)
        sample_b = weighted_sample_without_replacement(self.model_b.theories, k)
        bullets_a = self.model_a.as_bullets(sample_a)
        bullets_b = self.model_b.as_bullets(sample_b)
        try:
            pred = await self._call_judge_async(bullets_a, bullets_b, observation)
        except Exception as e:
            self.log.write(f"[red]Judge error:[/red] {e}")
            return
        winner = getattr(pred, "winner", "A").strip().upper()
        just = getattr(pred, "justification", "").strip()
        if winner not in {"A", "B"}:
            winner = "A"
        if winner == "A":
            multiplicative_update(sample_a, sample_b, eta=eta)
            self.wins["A"] += 1
        else:
            multiplicative_update(sample_b, sample_a, eta=eta)
            self.wins["B"] += 1
        self.model_a.normalize()
        self.model_b.normalize()
        self.panel_a.refresh_table()
        self.panel_b.refresh_table()
        self.log.write(f"[bold]Obs:[/bold] {observation}\n[bold]Winner:[/bold] {winner} [dim]- {just}[/dim]  [blue]Score A/B:[/blue] {self.wins['A']}/{self.wins['B']}")

    # --- Events ---
    @on(Button.Pressed, "#add-A")
    def add_theory_a(self, _: Button.Pressed):
        text = self.panel_a.input_theory.value.strip()
        w = self.panel_a.input_weight.value.strip() or "1.0"
        if text:
            try:
                self.model_a.theories.append(Theory(text, float(w)))
                self.model_a.normalize()
                self.panel_a.input_theory.value = ""
                self.panel_a.input_weight.value = "1.0"
                self.panel_a.refresh_table()
            except Exception:
                self.log.write("[red]Invalid weight for A[/red]")

    @on(Button.Pressed, "#add-B")
    def add_theory_b(self, _: Button.Pressed):
        text = self.panel_b.input_theory.value.strip()
        w = self.panel_b.input_weight.value.strip() or "1.0"
        if text:
            try:
                self.model_b.theories.append(Theory(text, float(w)))
                self.model_b.normalize()
                self.panel_b.input_theory.value = ""
                self.panel_b.input_weight.value = "1.0"
                self.panel_b.refresh_table()
            except Exception:
                self.log.write("[red]Invalid weight for B[/red]")

    @on(Button.Pressed, "#del-A")
    def del_theory_a(self, _: Button.Pressed):
        self.panel_a.delete_selected()

    @on(Button.Pressed, "#del-B")
    def del_theory_b(self, _: Button.Pressed):
        self.panel_b.delete_selected()

    @on(Button.Pressed, "#add-obs")
    def add_obs(self, _: Button.Pressed):
        text = self.obs_panel.input_obs.value.strip()
        if text:
            self._observations.append(text)
            self.obs_panel.refresh_from(self._observations)
            self.obs_panel.input_obs.value = ""

    @on(Button.Pressed, "#del-obs")
    def del_obs(self, _: Button.Pressed):
        idx = self.obs_panel.selected_index()
        if idx is None:
            return
        if 0 <= idx < len(self._observations):
            self._observations.pop(idx)
            self.obs_panel.refresh_from(self._observations)

    @on(Button.Pressed, "#show-dist")
    def show_dist(self, _: Button.Pressed):
        # Log top-5 theories for each model and simple metrics
        wa = [(t.text, t.weight) for t in self.model_a.theories]
        wb = [(t.text, t.weight) for t in self.model_b.theories]
        top_a = topk_sorted(wa, 5)
        top_b = topk_sorted(wb, 5)
        g_a = gini([w for _, w in wa]); g_b = gini([w for _, w in wb])
        self.log.write("[bold]Top A:[/bold] " + "; ".join(f"{txt} ({w:.3f})" for txt, w in top_a))
        self.log.write("[bold]Top B:[/bold] " + "; ".join(f"{txt} ({w:.3f})" for txt, w in top_b))
        self.log.write(f"[dim]Gini A={g_a:.3f}  Gini B={g_b:.3f}[/dim]")

    @on(Button.Pressed, "#run-n")
    async def run_n(self, _: Button.Pressed):
        if not self._configure_lm():
            return
        self._cancel = False
        for i in range(self.cfg.iterations):
            if self._cancel:
                self.log.write("[yellow]Run cancelled.[/yellow]")
                break
            await self._run_once(None)
            await asyncio.sleep(0)  # allow UI to refresh
        # summary
        wa = [t.weight for t in self.model_a.theories]
        wb = [t.weight for t in self.model_b.theories]
        self.log.write(f"[bold magenta]Run summary:[/bold magenta] A/B wins {self.wins['A']}/{self.wins['B']}  Gini A={gini(wa):.3f} B={gini(wb):.3f}")

    @on(Button.Pressed, "#step-1")
    async def step_one(self, _: Button.Pressed):
        await self._run_once(None)

    @on(Button.Pressed, "#cancel")
    def cancel_btn(self, _: Button.Pressed):
        self._cancel = True

    @on(Button.Pressed, "#save")
    def save_btn(self, _: Button.Pressed):
        self._save_state()

    @on(Button.Pressed, "#load")
    def load_btn(self, _: Button.Pressed):
        self._load_state()

    def action_run_n(self):
        asyncio.create_task(self.run_n(Button.Pressed(self.controls.btn_run)))

    def action_step_once(self):
        asyncio.create_task(self.step_one(Button.Pressed(self.controls.btn_step)))

    def action_cancel(self):
        self._cancel = True

    def action_save_state(self):
        self._save_state()

    def action_load_state(self):
        self._load_state()

    # --- Save/Load ---
    def _snapshot(self) -> dict:
        return {
            "config": asdict(self.cfg),
            "model_a": self.model_a.to_dict(),
            "model_b": self.model_b.to_dict(),
            "observations": list(self._observations),
            "wins": self.wins,
        }

    def _restore(self, d: dict):
        try:
            self.cfg = RunConfig(**d.get("config", {}))
        except TypeError:
            # Handle old versions lacking max_tokens
            c = d.get("config", {})
            c.setdefault("max_tokens", 1024)
            self.cfg = RunConfig(**c)
        self.model_a = WorldModel.from_dict(d.get("model_a", {"name": "A", "theories": []}))
        self.model_b = WorldModel.from_dict(d.get("model_b", {"name": "B", "theories": []}))
        self.panel_a.model = self.model_a
        self.panel_b.model = self.model_b
        self.panel_a.refresh_table()
        self.panel_b.refresh_table()
        self.controls.sel_provider.value = self.cfg.provider
        self.controls.in_k.value = str(self.cfg.sample_k)
        self.controls.in_n.value = str(self.cfg.iterations)
        self.controls.in_eta.value = str(self.cfg.eta)
        self.controls.in_seed.value = str(self.cfg.seed)
        self.controls.in_maxtok.value = str(self.cfg.max_tokens)
        self._observations = list(d.get("observations", []))
        self.obs_panel.refresh_from(self._observations)
        self.wins = dict(d.get("wins", {"A":0, "B":0}))
        random.seed(self.cfg.seed)
        self.log.write("[green]State loaded.[/green]")

    def _save_state(self):
        try:
            data = self._snapshot()
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self.log.write(f"[green]State saved to {STATE_FILE}[/green]")
        except Exception as e:
            self.log.write(f"[red]Save failed:[/red] {e}")

    def _load_state(self):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
            self._restore(d)
        except FileNotFoundError:
            self.log.write(f"[yellow]{STATE_FILE} not found.[/yellow]")
        except Exception as e:
            self.log.write(f"[red]Load failed:[/red] {e}")

def main():
    app = WorldModelTUI()
    app.run()


if __name__ == "__main__":
    main()
