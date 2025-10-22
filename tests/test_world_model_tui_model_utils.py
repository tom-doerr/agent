import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "world_model_tui_v3"))

from world_model_tui.model import (
    Theory,
    WorldModel,
    multiplicative_update,
    weighted_sample_without_replacement,
)
from world_model_tui.utils import (
    cursor_row_index,
    cursor_row_key,
    gini,
    kl_divergence,
    topk_sorted,
)


class DummyTable:
    def __init__(self, cursor_key=None, cursor=None, keys=None):
        self.cursor_row_key = cursor_key
        self.cursor_row = cursor
        self.rows = {k: idx for idx, k in enumerate(keys or [])}


def test_world_model_normalize_positive_weights():
    wm = WorldModel(
        "A",
        theories=[Theory("t1", 2.0), Theory("t2", -1.0), Theory("t3", 1.0)],
    )
    wm.normalize()
    weights = [t.weight for t in wm.theories]
    assert pytest.approx(weights[0], rel=1e-9) == 2 / 3
    assert weights[1] == 0.0
    assert pytest.approx(weights[2], rel=1e-9) == 1 / 3


def test_world_model_normalize_uniform_when_sum_nonpositive():
    wm = WorldModel("B", theories=[Theory("x", 0.0), Theory("y", -0.5)])
    wm.normalize()
    weights = [t.weight for t in wm.theories]
    assert weights == pytest.approx([0.5, 0.5])


def test_world_model_from_dict_normalizes():
    data = {"name": "C", "theories": [{"text": "t", "weight": 3}, {"text": "u", "weight": 1}]}
    wm = WorldModel.from_dict(data)
    weights = [t.weight for t in wm.theories]
    assert sum(weights) == pytest.approx(1.0)
    assert weights[0] > weights[1]


def test_world_model_as_bullets_handles_empty():
    wm = WorldModel("D")
    assert wm.as_bullets([]) == "(empty)"
    bullets = wm.as_bullets([Theory("hello"), Theory("world")])
    assert bullets == "- hello\n- world"


def test_weighted_sample_without_replacement_is_deterministic_with_stubbed_gumbel(monkeypatch):
    theories = [Theory(f"t{i}", w) for i, w in enumerate((0.6, 0.3, 0.1))]
    seq = iter([0.5, 0.1, 0.0])

    def fake_gumbel():
        return next(seq)

    monkeypatch.setattr("world_model_tui.model._gumbel", fake_gumbel)
    sample = weighted_sample_without_replacement(theories, 2)
    assert [t.text for t in sample] == ["t0", "t1"]
    assert len({id(t) for t in sample}) == len(sample)


def test_weighted_sample_handles_small_inputs(monkeypatch):
    monkeypatch.setattr("world_model_tui.model._gumbel", lambda: 0.0)
    assert weighted_sample_without_replacement([], 3) == []
    theories = [Theory("solo", 0.0)]
    sample = weighted_sample_without_replacement(theories, 5)
    assert sample == theories


def test_multiplicative_update_scales_winners_and_losers():
    win = [Theory("w", 0.5)]
    lose = [Theory("l", 0.5)]
    multiplicative_update(win, lose, eta=0.1)
    assert win[0].weight == pytest.approx(0.55)
    assert lose[0].weight == pytest.approx(0.45)


def test_multiplicative_update_clamps_eta():
    win = [Theory("w", 1.0)]
    lose = [Theory("l", 1.0)]
    multiplicative_update(win, lose, eta=5.0)
    assert win[0].weight == pytest.approx(1.999)
    assert lose[0].weight == pytest.approx(0.001)


def test_multiplicative_update_respects_eps_floor():
    win = [Theory("w", 1e-9)]
    lose = [Theory("l", 1e-9)]
    multiplicative_update(win, lose, eta=0.5, eps=1e-4)
    assert win[0].weight == pytest.approx(1e-4)
    assert lose[0].weight == pytest.approx(1e-4)


def test_topk_sorted_returns_highest_weights_first():
    data = [("b", 0.5), ("a", 0.9), ("c", 0.1)]
    assert topk_sorted(data, 2) == [("a", 0.9), ("b", 0.5)]


def test_kl_divergence_matches_manual_calculation():
    value = kl_divergence([0.5, 0.5], [0.9, 0.1])
    expected = 0.5 * math.log(0.5 / 0.9) + 0.5 * math.log(0.5 / 0.1)
    assert value == pytest.approx(expected)


def test_gini_zero_for_uniform_and_high_for_skewed():
    assert gini([1, 1, 1]) == pytest.approx(0.0)
    assert gini([0, 0, 1]) == pytest.approx(2 / 3, rel=1e-6)


def test_cursor_row_key_supports_legacy_attribute():
    table = DummyTable(cursor_key="row-2", keys=["row-1", "row-2", "row-3"])
    assert cursor_row_key(table) == "row-2"
    assert cursor_row_index(table) == 1


def test_cursor_row_index_returns_none_when_missing():
    table = DummyTable(cursor=None, keys=["row-1", "row-2"])
    assert cursor_row_key(table) is None
    assert cursor_row_index(table) is None
