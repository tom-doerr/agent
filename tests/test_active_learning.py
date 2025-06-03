import pytest
import os
import json
from unittest.mock import patch, MagicMock
from active_learning_loop import active_learning_loop, load_training_data, save_training_data
import dspy

@pytest.fixture
def mock_dspy(monkeypatch):
    # Mock DSPy modules
    mock_value_net = MagicMock()
    mock_generator = MagicMock()
    
    # Mock value network predictions
    mock_value_net.return_value.predict.return_value = MagicMock(
        score="0.7", uncertainty="0.3"
    )
    
    # Mock generator predictions
    mock_generator.return_value.generate.return_value = MagicMock(
        data_point="Test data point"
    )
    
    monkeypatch.setattr("active_learning_loop.ValueNetwork", mock_value_net)
    monkeypatch.setattr("active_learning_loop.GeneratorModule", mock_generator)

    # Mock configure_dspy
    monkeypatch.setattr("active_learning_loop.configure_dspy", MagicMock())

@pytest.fixture
def mock_input(monkeypatch):
    # Mock user input for ratings
    monkeypatch.setattr("builtins.input", lambda _: "5")

@pytest.fixture
def cleanup_files():
    # Clean up after tests
    yield
    if os.path.exists("value_net_training_data.json"):
        os.remove("value_net_training_data.json")

def test_active_learning_loop(mock_dspy, mock_input, cleanup_files, capsys):
    # Run the active learning loop
    active_learning_loop()
    
    # Capture output
    captured = capsys.readouterr()
    output = captured.out
    
    # Verify expected output
    assert "Test data point" in output
    assert "training examples" in output
    
    # Verify training data was saved
    training_data = load_training_data()
    assert len(training_data) == 3
    assert training_data[0].data_point == "Test data point"
    assert training_data[0].score == pytest.approx(5/9.0)

def test_load_save_training_data(cleanup_files):
    # Test data roundtrip
    test_data = [
        {"data_point": "test1", "score": 0.5},
        {"data_point": "test2", "score": 0.8}
    ]
    
    # Save and load data
    save_training_data([dspy.Example(**d) for d in test_data])
    loaded = load_training_data()
    
    # Verify data matches
    assert len(loaded) == 2
    assert loaded[0].data_point == "test1"
    assert loaded[0].score == 0.5
    assert loaded[1].data_point == "test2"
    assert loaded[1].score == 0.8
