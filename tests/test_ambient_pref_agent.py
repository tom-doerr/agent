import types
from pathlib import Path
import pytest

# Import after monkeypatching sys.path if needed
import importlib


class DummyRankerAlwaysA:
    def __call__(self, *, a, b):  # noqa: D401 – matches CompareSig fields
        return types.SimpleNamespace(better="a")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _row(idx):
    return {"id": f"id{idx}", "text": f"text{idx}"}


@pytest.fixture
def pref_agent(monkeypatch):
    # Import module lazily after patching
    module = importlib.import_module("ambient_pref_agent")
    return module


def test_prepare_pairs(pref_agent):
    rows = [_row(0), _row(1), _row(2)]
    Sig, pairs = pref_agent._prepare_pairs(rows)
    assert len(pairs) == 2
    assert pairs[0].better == "a"
    assert pairs[0].a == "text0" and pairs[0].b == "text1"


def test_percentile_logic(pref_agent):
    ranking = [_row(i) for i in range(5)]
    cand = {"text": "candidate"}
    pct = pref_agent.compute_percentile(cand, ranking, ranker=DummyRankerAlwaysA(), comparisons=10)
    assert pct == 1.0


def test_main_writes_percentile(tmp_path, monkeypatch, pref_agent):
    # Redirect paths
    monkeypatch.setattr(pref_agent, "RAW_FILE", tmp_path / "raw.ndjson")
    monkeypatch.setattr(pref_agent, "GRADED_FILE", tmp_path / "graded.ndjson")
    monkeypatch.setattr(pref_agent, "PERC_FILE", tmp_path / "perc.log")

    # Graded file with 2 rows
    pref_agent.append(pref_agent.GRADED_FILE, _row(0))
    pref_agent.append(pref_agent.GRADED_FILE, _row(1))

    # Patch fetch_hn to return one candidate
    def fake_fetch(_ts):
        yield {"id": "cand", "ts": 1, "source": "hn", "text": "candidate text", "labels": []}
    monkeypatch.setattr(pref_agent, "fetch_hn", fake_fetch)

    # Patch build_compare to dummy ranker
    monkeypatch.setattr(pref_agent, "build_compare", lambda graded: DummyRankerAlwaysA())

    pref_agent.asyncio.run(pref_agent.main(pref_agent._parse_args(["--cutoff", "0.5", "--comparisons", "2"])))

    # percentile log should exist with one line
    lines = list(pref_agent.ndjson_iter(pref_agent.PERC_FILE))
    assert len(lines) == 1
