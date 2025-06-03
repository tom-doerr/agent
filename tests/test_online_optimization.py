import pytest
import asyncio
import time
import os
import sys
from unittest.mock import MagicMock, patch
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from online_optimization_system import OnlineOptimizationSystem, AsyncModelManager, OptimizationRequest, InferenceResult
import dspy

class MockModule(dspy.Module):
    def __init__(self, output):
        super().__init__()
        self.output = output
        
    def forward(self, input_data):
        return self.output

@pytest.fixture
def mock_system():
    # Mock base program
    base_program = MockModule("base output")
    
    # Mock metric function
    def metric_fn(example, prediction, trace=None):
        return 1.0
        
    system = OnlineOptimizationSystem(base_program, metric_fn)
    system.model_manager.current_model = base_program
    return system

@pytest.mark.asyncio
async def test_inference_returns_result(mock_system):
    result = await mock_system.inference("test input")
    assert isinstance(result, InferenceResult)
    assert "base output" in result.prediction

def test_model_hot_swap(mock_system):
    # Create new model
    new_model = MockModule("optimized output")
    new_version = "v1"
    
    # Mock model loading
    with patch("dspy.Module.load", return_value=new_model):
        assert mock_system.model_manager.load_model("path.json", new_version)
    
    # Verify hot-swap
    model, version = mock_system.model_manager.get_model()
    assert version == new_version
    assert model("test") == "optimized output"

@pytest.mark.asyncio
async def test_graceful_degradation(mock_system):
    # Force inference error
    mock_system.model_manager.current_model = None
    result = await mock_system.inference("test input")
    assert "try again shortly" in result.prediction

def test_optimization_trigger_data_batch(mock_system):
    # Fill data collector with more than batch size
    for i in range(40):
        mock_system.data_collector.add_example(f"input{i}", f"prediction{i}")
    
    # Should trigger optimization
    mock_system._check_optimization_triggers()
    assert mock_system.optimization_engine.optimization_queue.qsize() == 1

def test_optimization_trigger_performance(mock_system):
    # Add data and simulate performance drop
    for i in range(30):
        mock_system.data_collector.add_example(f"input{i}", f"prediction{i}")
    
    mock_system.model_manager.performance_history = [
        {'accuracy': 0.7, 'latency': 100, 'version': "v0", 'timestamp': time.time()}
    ]
    mock_system.inference_count = 150
    
    # Should trigger optimization
    mock_system._check_optimization_triggers()
    assert mock_system.optimization_engine.optimization_queue.qsize() == 1

def test_optimization_completion(mock_system):
    # Get initial version
    _, initial_version = mock_system.model_manager.get_model()
    
    # Mock optimization
    optimized_model = MockModule("optimized output")
    request = OptimizationRequest([], "test", time.time(), initial_version)
    
    # Complete optimization
    with patch("dspy.SIMBA.compile", return_value=optimized_model):
        mock_system.optimization_engine._on_optimization_complete(optimized_model, request)
    
    # Verify new version loaded
    model, new_version = mock_system.model_manager.get_model()
    assert new_version != initial_version
