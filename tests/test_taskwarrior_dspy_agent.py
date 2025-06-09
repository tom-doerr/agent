import os
import pytest
pytestmark = pytest.mark.timeout(10, method='thread')
import sys
import pytest
import subprocess
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from taskwarrior_dspy_agent import execute_taskwarrior_command, setup_dspy, main

def test_execute_taskwarrior_command_success():
    with patch("subprocess.run") as mock_run:
        # Mock successful command execution
        mock_run.return_value = subprocess.CompletedProcess(
            args=["task", "list"],
            returncode=0,
            stdout="Task output",
            stderr=""
        )
        
        stdout, stderr = execute_taskwarrior_command("task list")
        assert stdout == "Task output"
        assert stderr == ""

def test_execute_taskwarrior_command_invalid():
    stdout, stderr = execute_taskwarrior_command("invalid command")
    assert "Error: Invalid command format" in stderr

def test_execute_taskwarrior_command_not_found():
    with patch("subprocess.run", side_effect=FileNotFoundError):
        stdout, stderr = execute_taskwarrior_command("task list")
        assert "not found" in stderr

@patch("builtins.input", side_effect=["What's next?", "exit"])
@patch("taskwarrior_dspy_agent.TaskWarriorModule")
@patch("taskwarrior_dspy_agent.execute_taskwarrior_command")
def test_main_flow(mock_execute, mock_module, mock_input, capsys):
    # Mock DSPy setup
    mock_setup = MagicMock()
    
    # Mock command generation
    mock_prediction = MagicMock()
    mock_prediction.taskwarrior_command = "task list"
    mock_module.return_value.forward.return_value = mock_prediction
    
    # Mock command execution
    mock_execute.return_value = ("Task output", "")
    
    with patch("taskwarrior_dspy_agent.setup_dspy", mock_setup):
        main()
    
    # Verify output
    captured = capsys.readouterr()
    assert "LLM suggested command" in captured.out
    assert "To execute, you would run:" in captured.out
    assert "In an integrated environment" in captured.out
