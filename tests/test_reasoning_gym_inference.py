"""
Comprehensive test suite for reasoning_gym_inference.py
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest
import dspy

from reasoning_gym_inference import (
    ReasoningGymInference,
    ReasoningGymSolver,
    REASONING_GYM_TASKS,
)


@pytest.fixture
def mock_api_key():
    """Provide mock API key for testing."""
    return "test-api-key-12345"


@pytest.fixture
def mock_reasoning_gym_dataset():
    """Mock reasoning_gym dataset."""
    mock_examples = [
        Mock(problem="What is 2/4 simplified?", answer="1/2"),
        Mock(problem="What is 6/8 simplified?", answer="3/4"),
        Mock(problem="What is 10/20 simplified?", answer="1/2"),
        Mock(problem="What is 15/45 simplified?", answer="1/3"),
        Mock(problem="What is 8/12 simplified?", answer="2/3"),
    ]
    return mock_examples


@pytest.fixture
def mock_dspy_lm():
    """Mock DSPy language model."""
    with patch("dspy.LM") as mock_lm:
        yield mock_lm


class TestReasoningGymInference:
    """Test ReasoningGymInference class."""
    
    def test_initialization(self, mock_api_key, mock_dspy_lm):
        """Test initialization of ReasoningGymInference."""
        runner = ReasoningGymInference(
            api_key=mock_api_key,
            max_tokens=100,
            temperature=0.0
        )
        
        assert runner.max_tokens == 100
        mock_dspy_lm.assert_called_once_with(
            model="deepseek-chat",
            api_key=mock_api_key,
            api_base="https://api.deepseek.com",
            max_tokens=100,
            temperature=0.0,
        )
    
    def test_evaluate_task_success(self, mock_api_key, mock_dspy_lm, mock_reasoning_gym_dataset):
        """Test successful task evaluation."""
        # Setup mocks
        with patch("reasoning_gym.create_dataset") as mock_create_dataset:
            mock_create_dataset.return_value = mock_reasoning_gym_dataset
            
            # Create runner first
            runner = ReasoningGymInference(api_key=mock_api_key)
            
            # Mock the solver instance's _mock_call method
            with patch.object(runner.solver, "_mock_call") as mock_solver:
                # Make first 3 correct, last 2 incorrect
                mock_solver.side_effect = [
                    Mock(answer="1/2"),
                    Mock(answer="3/4"),
                    Mock(answer="1/2"),
                    Mock(answer="wrong"),
                    Mock(answer="also wrong"),
                ]
                
                results = runner.evaluate_task("fraction_simplification", num_tries=5)
        
        assert results["task"] == "fraction_simplification"
        assert results["total_examples"] == 5
        assert results["correct"] == 3
        assert results["success_rate"] == 60.0
        assert len(results["results"]) == 5
        
        # Check individual results
        assert results["results"][0]["correct"] is True
        assert results["results"][3]["correct"] is False
    
    def test_evaluate_task_with_errors(self, mock_api_key, mock_dspy_lm, mock_reasoning_gym_dataset):
        """Test task evaluation with API errors."""
        with patch("reasoning_gym.create_dataset") as mock_create_dataset:
            mock_create_dataset.return_value = mock_reasoning_gym_dataset
            
            # Create runner first
            runner = ReasoningGymInference(api_key=mock_api_key)
            
            # Mock solver to raise error on second call
            with patch.object(runner.solver, "_mock_call") as mock_solver:
                mock_solver.side_effect = [
                    Mock(answer="1/2"),
                    Exception("API Error"),
                    Mock(answer="1/2"),
                    Mock(answer="1/3"),
                    Mock(answer="2/3"),
                ]
                
                results = runner.evaluate_task("fraction_simplification", num_tries=5)
        
        assert results["correct"] == 4  # One error, but 4 correct
        assert "error" in results["results"][1]
        assert results["results"][1]["correct"] is False
    
    def test_run_all_tasks(self, mock_api_key, mock_dspy_lm, mock_reasoning_gym_dataset):
        """Test running all tasks."""
        with patch("reasoning_gym.create_dataset") as mock_create_dataset:
            mock_create_dataset.return_value = mock_reasoning_gym_dataset[:2]  # Use only 2 examples
            
            # Create runner first
            runner = ReasoningGymInference(api_key=mock_api_key)
            
            with patch.object(runner.solver, "_mock_call") as mock_solver:
                # Always return correct answer for simplicity
                mock_solver.side_effect = [
                    Mock(answer="1/2"),
                    Mock(answer="3/4"),
                ] * len(REASONING_GYM_TASKS)
                
                all_results = runner.run_all_tasks(num_tries=2)
        
        assert len(all_results) == len(REASONING_GYM_TASKS)
        for task in REASONING_GYM_TASKS:
            assert task in all_results
            assert all_results[task]["success_rate"] == 100.0
    
    def test_save_results(self, mock_api_key, mock_dspy_lm):
        """Test saving results to files."""
        runner = ReasoningGymInference(api_key=mock_api_key)
        
        # Create mock results
        mock_results = {
            "fraction_simplification": {
                "task": "fraction_simplification",
                "total_examples": 100,
                "correct": 85,
                "success_rate": 85.0,
                "results": [],
            },
            "base_conversion": {
                "task": "base_conversion",
                "total_examples": 100,
                "correct": 72,
                "success_rate": 72.0,
                "results": [],
            },
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "test_results.json")
            summary = runner.save_results(mock_results, output_file)
            
            # Check JSON file
            assert os.path.exists(output_file)
            with open(output_file) as f:
                saved_data = json.load(f)
            
            assert "summary" in saved_data
            assert "detailed_results" in saved_data
            assert saved_data["summary"]["max_tokens"] == 100
            assert saved_data["summary"]["tasks"]["fraction_simplification"]["success_rate"] == 85.0
            
            # Check summary text file
            summary_file = output_file.replace(".json", "_summary.txt")
            assert os.path.exists(summary_file)
            with open(summary_file) as f:
                summary_text = f.read()
            
            assert "fraction_simplification:" in summary_text
            assert "Success Rate: 85.00%" in summary_text
            assert "Correct: 85/100" in summary_text


class TestReasoningGymSolver:
    """Test ReasoningGymSolver signature."""
    
    def test_signature_fields(self):
        """Test that signature has correct fields."""
        assert hasattr(ReasoningGymSolver, "problem")
        assert hasattr(ReasoningGymSolver, "answer")
        assert ReasoningGymSolver.problem.desc == "The problem to solve"
        assert ReasoningGymSolver.answer.desc == "The answer to the problem"


class TestMainFunction:
    """Test main entry point function."""
    
    @patch("reasoning_gym_inference.ReasoningGymInference")
    @patch("reasoning_gym.create_dataset")
    def test_main_with_args(self, mock_create_dataset, mock_inference_class):
        """Test main function with command line arguments."""
        mock_create_dataset.return_value = []
        mock_runner = Mock()
        mock_inference_class.return_value = mock_runner
        
        test_args = [
            "reasoning_gym_inference.py",
            "--api-key", "test-key",
            "--num-tries", "50",
            "--max-tokens", "75",
            "--output", "custom_output.json",
            "--tasks", "fraction_simplification", "base_conversion",
        ]
        
        with patch("sys.argv", test_args):
            from reasoning_gym_inference import main
            main()
        
        mock_inference_class.assert_called_once_with(api_key="test-key", max_tokens=75)
        assert mock_runner.evaluate_task.call_count == 2
        mock_runner.save_results.assert_called_once()
    
    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": "env-test-key"})
    @patch("reasoning_gym_inference.ReasoningGymInference")
    @patch("reasoning_gym.create_dataset")
    def test_main_with_env_var(self, mock_create_dataset, mock_inference_class):
        """Test main function using environment variable for API key."""
        mock_create_dataset.return_value = []
        mock_runner = Mock()
        mock_inference_class.return_value = mock_runner
        
        test_args = ["reasoning_gym_inference.py"]
        
        with patch("sys.argv", test_args):
            from reasoning_gym_inference import main
            main()
        
        mock_inference_class.assert_called_once_with(api_key="env-test-key", max_tokens=100)
        mock_runner.run_all_tasks.assert_called_once_with(100)
    
    def test_main_no_api_key(self):
        """Test main function exits when no API key provided."""
        test_args = ["reasoning_gym_inference.py"]
        
        with patch("sys.argv", test_args):
            with patch.dict(os.environ, {}, clear=True):
                with pytest.raises(SystemExit) as exc_info:
                    from reasoning_gym_inference import main
                    main()
                
                assert exc_info.value.code == 1


class TestIntegration:
    """Integration tests with mocked external dependencies."""
    
    @patch("reasoning_gym.create_dataset")
    @patch("dspy.LM")
    def test_full_workflow(self, mock_lm_class, mock_create_dataset):
        """Test complete workflow from initialization to saving results."""
        # Setup mocks
        mock_lm = Mock()
        mock_lm_class.return_value = mock_lm
        
        # Mock dataset
        mock_examples = [
            Mock(problem=f"Problem {i}", answer=f"Answer {i}")
            for i in range(10)
        ]
        mock_create_dataset.return_value = mock_examples
        
        # Create runner first
        runner = ReasoningGymInference(api_key="test-key", max_tokens=50)
        
        # Mock solver behavior
        with patch.object(runner.solver, "_mock_call") as mock_solver:
            # Make 7 out of 10 correct
            mock_solver.side_effect = [
                Mock(answer=f"Answer {i}") if i < 7 else Mock(answer="Wrong")
                for i in range(10)
            ]
            
            # Run inference
            results = runner.evaluate_task("fraction_simplification", num_tries=10)
            
            # Verify results
            assert results["total_examples"] == 10
            assert results["correct"] == 7
            assert results["success_rate"] == 70.0
            
            # Save and verify files
            with tempfile.TemporaryDirectory() as tmpdir:
                output_file = os.path.join(tmpdir, "integration_test.json")
                runner.save_results({"fraction_simplification": results}, output_file)
                
                assert os.path.exists(output_file)
                assert os.path.exists(output_file.replace(".json", "_summary.txt"))