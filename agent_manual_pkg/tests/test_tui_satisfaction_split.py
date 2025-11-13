from __future__ import annotations

from types import SimpleNamespace

import pytest

import sys
sys.path.insert(0, 'agent_manual_pkg/src')
from agent_manual_pkg.tui import TUI, InstrumentalGoals, SatisfactionResult  # type: ignore


class StubLog:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def write(self, message, **_: object) -> None:
        self.lines.append(str(getattr(message, "plain", message)))

    def clear(self) -> None:
        self.lines.append("__clear__")


def _stub_query_for_satisfaction(log: StubLog):
    def _q(selector, *_a, **_k):
        if selector == "#satisfaction":
            return log
        raise AssertionError(selector)

    return _q


def test_update_goals_sets_state(monkeypatch):
    tui = TUI(concurrency=0)
    slog = StubLog()
    monkeypatch.setattr(tui, "query_one", _stub_query_for_satisfaction(slog))

    monkeypatch.setattr(tui, "_run_goal_planner", lambda prompt: (InstrumentalGoals(goals=["g1"]), None))

    tui._update_goals("prompt")

    assert tui._latest_goals and tui._latest_goals.goals == ["g1"]
    assert "satisfaction_goals" in tui._active_modules
    assert slog.lines  # refresh wrote something


def test_update_score_sets_state(monkeypatch):
    tui = TUI(concurrency=0)
    # Seed goals so scorer is meaningful
    tui._latest_goals = InstrumentalGoals(goals=["g1"])  # type: ignore[attr-defined]

    slog = StubLog()
    monkeypatch.setattr(tui, "query_one", _stub_query_for_satisfaction(slog))

    monkeypatch.setattr(tui, "_run_satisfaction_scorer", lambda: (SatisfactionResult(score=7, rationale="ok"), None))

    tui._update_score()

    assert tui._latest_score and tui._latest_score.score == 7
    assert "satisfaction_score" in tui._active_modules
    assert slog.lines  # refresh wrote something

