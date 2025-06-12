import json
import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dspy_programs import active_learning

@pytest.fixture
def training_path(tmp_path, monkeypatch):
    path = tmp_path / "training.json"
    monkeypatch.setattr(active_learning, "TRAINING_DATA_FILE", str(path))
    return path

def test_save_and_load_training_data(training_path):
    example = active_learning.dspy.Example(data_point="x", score=0.8)
    active_learning.save_training_data([example])
    loaded = active_learning.load_training_data()
    assert len(loaded) == 1
    assert loaded[0].data_point == "x"
    assert loaded[0].score == 0.8
