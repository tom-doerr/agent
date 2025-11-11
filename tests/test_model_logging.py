import importlib
import json
import os
from pathlib import Path


def test_log_model_writes_jsonl(tmp_path, monkeypatch):
    log_path = tmp_path / "calls.jsonl"
    monkeypatch.setenv("NLCO_MODEL_LOG", str(log_path))
    mod = importlib.import_module("nlco_iter")
    importlib.reload(mod)

    mod._log_model("Refiner", output="hello", reasoning="why")
    data = log_path.read_text().strip().splitlines()
    assert len(data) == 1
    rec = json.loads(data[0])
    assert rec["stage"] == "Refiner"
    assert rec["output"] == "hello"
    assert rec["reasoning"] == "why"


def test_log_model_accepts_none(tmp_path, monkeypatch):
    log_path = tmp_path / "calls.jsonl"
    monkeypatch.setenv("NLCO_MODEL_LOG", str(log_path))
    mod = importlib.import_module("nlco_iter")
    importlib.reload(mod)

    mod._log_model("Refiner", output=None, reasoning=None)
    rec = json.loads(log_path.read_text().strip())
    assert rec["stage"] == "Refiner"
    assert rec["output"] == ""
    assert rec["reasoning"] == ""
