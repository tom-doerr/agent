import types
import time
from types import SimpleNamespace
from pathlib import Path

import pytest

import ambient_agent as aa





def test_fetch_hn_filters_after_ts(monkeypatch):
    """`fetch_hn` must only yield items newer than *after_ts*."""
    # create two dummy RSS items
    now = int(time.time())
    older_ts = now - 1000
    newer_ts = now - 10

    def _t(ts):
        return time.gmtime(ts)  # struct_time compatible

    dummy_entries = [
        SimpleNamespace(title="Old item", summary="...", link="id1", published_parsed=_t(older_ts)),
        SimpleNamespace(title="New item", summary="...", link="id2", published_parsed=_t(newer_ts)),
    ]

    dummy_feed = SimpleNamespace(entries=dummy_entries)

    def fake_parse(url):  # noqa: D401 – simple stub
        assert url == aa.HN_RSS
        return dummy_feed

    monkeypatch.setattr("feedparser.parse", fake_parse)

    items = list(aa.fetch_hn(after_ts=now - 500))  # threshold between the two
    assert len(items) == 1
    assert items[0]["id"] == "id2"


def test_config_files_created(tmp_path: Path, monkeypatch):
    # Run helper to touch files in tmp
    tmp_raw = tmp_path / "raw_events.ndjson"
    tmp_truth = tmp_path / "truth_set.ndjson"
    tmp_notify = tmp_path / "notify.log"
    tmp_decisions = tmp_path / "decisions.ndjson"

    monkeypatch.setattr(aa, "RAW_FILE", tmp_raw)
    monkeypatch.setattr(aa, "TRUTH_FILE", tmp_truth)
    monkeypatch.setattr(aa, "NOTIFY_FILE", tmp_notify)
    monkeypatch.setattr(aa, "DECISIONS_FILE", tmp_decisions)

    aa._ensure_config_files()
    assert all(p.exists() for p in (tmp_raw, tmp_truth, tmp_notify, tmp_decisions))


def test_append_and_iter_ndjson(tmp_path: Path):
    path = tmp_path / "file.ndjson"
    obj1 = {"foo": 1}
    obj2 = {"bar": 2}

    aa.append(path, obj1)
    aa.append(path, obj2)

    assert list(aa.ndjson_iter(path)) == [obj1, obj2]
