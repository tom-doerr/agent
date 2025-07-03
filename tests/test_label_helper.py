import json
from types import SimpleNamespace
from pathlib import Path

import pytest

import ambient_agent as aa
import label_helper as lh


class DummyJudge:
    def __init__(self, responses):
        self._iter = iter(responses)

    def __call__(self, *, text):  # noqa: D401 – simple stub
        return next(self._iter)


def _dummy_event(ts: int, _id: str = "id"):
    return {
        "id": _id,
        "ts": ts,
        "text": "dummy",
        "source": "hn",
        "labels": [],
    }


@pytest.mark.asyncio
async def test_agent_decision_logging(tmp_path, monkeypatch):
    # Patch paths
    raw_f = tmp_path / "raw.ndjson"
    dec_f = tmp_path / "dec.ndjson"
    notify_f = tmp_path / "notify.log"
    monkeypatch.setattr(aa, "RAW_FILE", raw_f)
    monkeypatch.setattr(aa, "DECISIONS_FILE", dec_f)
    monkeypatch.setattr(aa, "NOTIFY_FILE", notify_f)

    # Stub fetch_hn -> two events
    now = 1_000_000
    events = [_dummy_event(now + 1, "a"), _dummy_event(now + 2, "b")]
    monkeypatch.setattr(aa, "fetch_hn", lambda after_ts: events)

    # Stub judge responses yes / no
    judge_responses = [SimpleNamespace(helpful="yes", nugget="n1"), SimpleNamespace(helpful="no", nugget="")]
    monkeypatch.setattr(aa, "build_judge", lambda: DummyJudge(judge_responses))

    # Run main once
    await aa.main()

    # decisions file should have 2 rows
    assert dec_f.exists()
    rows = list(lh.ndjson_iter(dec_f))
    assert {r["id"] for r in rows} == {"a", "b"}
    # notify only for helpful==yes
    notes = list(lh.ndjson_iter(notify_f))
    assert len(notes) == 1 and "n1" in notes[0]["msg"]


def test_label_helper_export(tmp_path):
    # Prepare decisions with yes/no
    dec_f = tmp_path / "dec.ndjson"
    truth_f = tmp_path / "truth.ndjson"

    yes_row = {"id": "good", "ts": 1, "text": "foo", "helpful": "yes", "nugget": "bar"}
    no_row = {"id": "bad", "ts": 2, "text": "foo", "helpful": "no", "nugget": ""}
    for row in (yes_row, no_row):
        lh.append(dec_f, row)

    n = lh.export_helpful(truth_f, dec_f)
    assert n == 1  # only yes exported

    truth_rows = list(lh.ndjson_iter(truth_f))
    assert truth_rows[0]["id"] == "good"
    # helpful field should be stripped
    assert "helpful" not in truth_rows[0] and "nugget" not in truth_rows[0]


def test_interactive_label(tmp_path, monkeypatch):
    """Simulate user accepting a single helpful row via interactive CLI."""
    dec_f = tmp_path / "dec.ndjson"
    truth_f = tmp_path / "truth.ndjson"

    lh.append(dec_f, {"id": "x", "ts": 1, "text": "foo", "helpful": "yes", "nugget": "bar"})

    answers = iter([""])  # Press Enter once then StopIteration ends loop
    monkeypatch.setattr("builtins.input", lambda _="": next(answers))

    lh.interactive_label(decisions_path=dec_f, truth_path=truth_f)
    rows = list(lh.ndjson_iter(truth_f))
    assert len(rows) == 1 and rows[0]["id"] == "x"
