import pytest
pytestmark = pytest.mark.timeout(10, method='thread')
import os
import json
import sys
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from active_learning_loop import active_learning_loop, load_training_data, save_training_data
import dspy

@pytest.fixture
def mock_dspy(monkeypatch):
    # Mock DSPy modules
    mock_value_net = MagicMock()
    mock_generator = MagicMock()
        
    # Mock value network: when the instance is called, it returns a MagicMock with score and uncertainty
    mock_value_net_instance = mock_value_net.return_value
    mock_value_net_instance.return_value = MagicMock(
        score="0.7", uncertainty="0.3"
    )
        
    # Mock generator: when the instance is called, it returns a MagicMock with data_point
    mock_generator_instance = mock_generator.return_value
    mock_generator_instance.return_value = MagicMock(
        data_point="Test data point"
    )
        
    monkeypatch.setattr("active_learning_loop.ValueNetwork", mock_value_net)
    monkeypatch.setattr("active_learning_loop.GeneratorModule", mock_generator)

    # Mock configure_dspy
    monkeypatch.setattr("active_learning_loop.configure_dspy", MagicMock())
        
    # Reduce topics and mock LM
    monkeypatch.setattr("active_learning_loop.topics", ["Test topic"])
        
    # Mock LM to avoid real API calls
    mock_lm = MagicMock()
    monkeypatch.setattr("active_learning_loop.dspy.settings.configure", MagicMock(return_value=mock_lm))
        
    # Also mock the generator instance to return our test data point
    monkeypatch.setattr("active_learning_loop.generator", MagicMock(return_value=MagicMock(data_point="Test data point")))

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
    # We have one topic and we score top 3, but we only have one candidate, so only one is added
    assert len(training_data) == 1
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
