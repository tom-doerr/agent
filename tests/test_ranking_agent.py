import types
from pathlib import Path

import pytest
import ranking_agent as ra


class DummyRankerAlwaysA:
    def __call__(self, *, text_a, text_b):  # noqa: D401 – match call signature
        return types.SimpleNamespace(better="a")


class DummyRankerAlwaysB:
    def __call__(self, *, text_a, text_b):  # noqa: D401
        return types.SimpleNamespace(better="b")


def _row(idx: int):
    return {"id": f"id{idx}", "text": f"text{idx}"}


def test_prepare_pairs(monkeypatch):
    rows = [_row(i) for i in range(3)]  # id0, id1, id2
    Sig, pairs = ra._prepare_pairs(rows)
    # Should create len-1 pairs
    assert len(pairs) == 2
    # First pair should label 'a' as better (id0 > id1)
    assert pairs[0].better == "a"
    assert pairs[0].text_a == "text0" and pairs[0].text_b == "text1"


def test_compute_percentile(monkeypatch):
    # Prepare ranking rows
    ranking = [_row(i) for i in range(5)]
    cand = {"text": "candidate"}

    pct_a = ra.compute_percentile(cand, ranking, ranker=DummyRankerAlwaysA(), comparisons=10)
    assert pct_a == 100.0

    pct_b = ra.compute_percentile(cand, ranking, ranker=DummyRankerAlwaysB(), comparisons=10)
    assert pct_b == 0.0

    # edge case: zero comparisons → 0 pct
    pct_zero = ra.compute_percentile(cand, ranking, ranker=DummyRankerAlwaysA(), comparisons=0)
    assert pct_zero == 0.0


def test_prepare_pairs_single_row():
    ret = ra._prepare_pairs([_row(0)])
    if isinstance(ret, tuple):
        _, pairs = ret
    else:
        pairs = ret
    assert len(pairs) == 0


def test_cli_bootstrap_create(tmp_path, monkeypatch):
    monkeypatch.setattr(ra, "RANKING_FILE", tmp_path / "rank.ndjson")
    mp_model = tmp_path / "ranker_latest.pkl"
    monkeypatch.setattr(ra, "MODEL_PATH", mp_model)
    # create dummy model file to skip retrain
    mp_model.parent.mkdir(exist_ok=True)
    mp_model.write_bytes(b"x")

    called = {}
    monkeypatch.setattr(ra, "build_ranker", lambda force_retrain=False: called.setdefault("used", True))

    cand_file = tmp_path / "dec.ndjson"
    rows = [{"id": "x", "text": "foo"}, {"id": "y", "text": "bar"}]
    for r in rows:
        ra.append(cand_file, r)

    ra.main(["--eval", str(cand_file), "--quiet"])

    # ranking file should now exist with same rows (order preserved)
    created = list(ra.ndjson_iter(ra.RANKING_FILE))
    assert created == rows


def test_cli_force_retrain(tmp_path, monkeypatch):
    monkeypatch.setattr(ra, "RANKING_FILE", tmp_path / "rank.ndjson")
    mp_model = tmp_path / "ranker_latest.pkl"
    monkeypatch.setattr(ra, "MODEL_PATH", mp_model)

    # write dummy model file so that MODEL_PATH.exists() is True
    mp_model.parent.mkdir(exist_ok=True)
    mp_model.write_bytes(b"x")

    calls = {}

    def fake_build(force_retrain=False):
        calls.setdefault("cnt", 0)
        calls["cnt"] += 1
        return DummyRankerAlwaysA()

    monkeypatch.setattr(ra, "build_ranker", fake_build)

    # ranking file needs data so evaluation succeeds
    ra.append(ra.RANKING_FILE, {"id": "r1", "text": "foo"})
    ra.append(ra.RANKING_FILE, {"id": "r2", "text": "bar"})

    cand_file = tmp_path / "dec.ndjson"
    ra.append(cand_file, {"id": "c", "text": "candidate"})

    ra.main(["--eval", str(cand_file), "--force", "--quiet"])
    # Should call build_ranker twice: once for retrain, once to load later
    assert calls["cnt"] == 2


def test_cli_train_eval(tmp_path, monkeypatch):
    # Point paths to temp dir
    monkeypatch.setattr(ra, "RANKING_FILE", tmp_path / "rank.ndjson")
    monkeypatch.setattr(ra, "MODEL_PATH", tmp_path / "ranker_latest.pkl")

    # Write minimal ranking file (2 rows)
    ra.append(ra.RANKING_FILE, {"id": "a", "text": "good"})
    ra.append(ra.RANKING_FILE, {"id": "b", "text": "bad"})

    # Monkeypatch build_ranker to avoid real training
    called = {}

    def fake_build_ranker(force_retrain=False):
        called["yes"] = True
        return DummyRankerAlwaysA()

    monkeypatch.setattr(ra, "build_ranker", fake_build_ranker)

    # Prepare decisions file
    cand_file = tmp_path / "dec.ndjson"
    ra.append(cand_file, {"id": "c", "text": "candidate"})

    # Run CLI eval (quiet)
    ra.main(["--eval", str(cand_file), "--percentile", "50", "--comparisons", "2", "--output", str(tmp_path / "out.ndjson"), "--quiet"])

    # build_ranker should have been called lazily
    assert "yes" in called
