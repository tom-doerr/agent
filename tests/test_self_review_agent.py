#!/usr/bin/env python3

import pytest
pytestmark = pytest.mark.timeout(10, method='thread')
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from self_review_agent import SelfReviewAgent
import dspy
from unittest.mock import patch, MagicMock

def test_self_review_agent_initialization():
    agent = SelfReviewAgent(max_iterations=3)
    assert agent.max_iterations == 3
    assert hasattr(agent, 'generate')
    assert hasattr(agent, 'criticize')
    assert hasattr(agent, 'improve')
    assert hasattr(agent, 'should_continue')

@patch.object(dspy, 'Predict')
def test_self_review_flow(mock_predict):
    # Mock the Predict module's behavior
    mock_instance = MagicMock()
    mock_predict.return_value = mock_instance

    # Set return values for each step
    mock_instance.side_effect = [
        MagicMock(response="Initial response"),
        MagicMock(feedback="Good but needs improvement"),
        MagicMock(should_continue="yes"),
        MagicMock(improved_response="Improved response v1"),
        MagicMock(feedback="Better but still needs work"),
        MagicMock(should_continue="yes"),
        MagicMock(improved_response="Improved response v2"),
        MagicMock(feedback="Perfect"),
        MagicMock(should_continue="no")
    ]

    agent = SelfReviewAgent(max_iterations=3)
    history, final_response = agent.forward("Test task")

    assert "Initial response" in history
    assert "Improved response v1" in history
    assert "Improved response v2" in history
    assert "Perfect" in history
    assert final_response == "Improved response v2"

@patch.object(dspy, 'Predict')
def test_self_review_early_stop(mock_predict):
    mock_instance = MagicMock()
    mock_predict.return_value = mock_instance

    mock_instance.side_effect = [
        MagicMock(response="Initial response"),
        MagicMock(feedback="Good enough"),
        MagicMock(should_continue="no")
    ]

    agent = SelfReviewAgent(max_iterations=3)
    history, final_response = agent.forward("Test task")
    
    assert "Initial response" in history
    assert "Stopping: Feedback indicates no further improvements needed" in history
    assert final_response == "Initial response"

if __name__ == "__main__":
    pytest.main()
