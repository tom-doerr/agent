#!/usr/bin/env python3

import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from iterative_improvement_elo import sample_version, get_random_opponent, update_elo_ratings
from unittest.mock import patch, MagicMock
import numpy as np
import random
import dspy
from simpledspy import predict, chain_of_thought

# Test helper functions
def test_sample_version():
    versions = [
        {'version': 'v1', 'elo': 1000},
        {'version': 'v2', 'elo': 1200},
        {'version': 'v3', 'elo': 800}
    ]
    sampled = sample_version(versions)
    assert sampled in versions

def test_get_random_opponent():
    versions = [
        {'version': 'v1', 'elo': 1000},
        {'version': 'v2', 'elo': 1200},
        {'version': 'v3', 'elo': 800}
    ]
    current = versions[0]
    opponent = get_random_opponent(versions, current)
    assert opponent != current
    assert opponent in versions

def test_update_elo_ratings():
    winner = {'version': 'v1', 'elo': 1000}
    loser = {'version': 'v2', 'elo': 1000}
    update_elo_ratings(winner, loser)
    assert winner['elo'] > 1000
    assert loser['elo'] < 1000
    assert abs(winner['elo'] - 1016) < 0.1
    assert abs(loser['elo'] - 984) < 0.1

# Test main flow with mocked LLM
@patch('iterative_improvement_elo.predict')
@patch('iterative_improvement_elo.chain_of_thought')
@patch('iterative_improvement_elo.console')
def test_iterative_improvement_flow(mock_console, mock_chain, mock_predict):
    # Mock LLM responses
    mock_chain.return_value = "Initial version"
    mock_predict.side_effect = [
        "New version",  # generation
        "1", "1", "1"   # comparisons (all prefer new version)
    ]

    # Mock helper functions to control randomness
    with patch('iterative_improvement_elo.sample_version') as mock_sample, \
         patch('iterative_improvement_elo.get_random_opponent') as mock_opponent:
        
        # Set up mock responses
        mock_sample.return_value = {'version': "Initial version", 'elo': 1000}
        mock_opponent.side_effect = [
            {'version': "v1", 'elo': 1000},
            {'version': "v2", 'elo': 1000},
            {'version': "v3", 'elo': 1000}
        ]

        # Import main function after mocks are set
        from iterative_improvement_elo import iterative_improvement_elo
        
        # Run with 1 iteration
        best_version = iterative_improvement_elo("test task", iterations=1, parallel=1)
        
        # Verify results
        assert "New version" in best_version
        assert mock_chain.call_count == 1
        assert mock_predict.call_count == 4  # 1 gen + 3 comparisons
        
        # Verify counters were updated
        console_calls = mock_console.print.call_args_list
        found_counters = False
        for call in console_calls:
            if "Requests: gen_success=1, gen_failures=0, eval_success=3, eval_failures=0" in call[0][0]:
                found_counters = True
                break
        assert found_counters, "Request counters not displayed"

# Test ELO ranking display
@patch('iterative_improvement_elo.predict')
@patch('iterative_improvement_elo.chain_of_thought')
def test_elo_ranking_order(mock_chain, mock_predict):
    # Mock LLM responses
    mock_chain.return_value = "Initial version"
    mock_predict.side_effect = [
        "New version",  # generation
        "1", "1", "1"   # comparisons
    ]

    # Import main function after mocks are set
    from iterative_improvement_elo import iterative_improvement_elo
    
    # Run with 1 iteration
    best_version = iterative_improvement_elo("test task", iterations=1, parallel=1)
    
    # Verify ranking order (best last)
    assert "New version" in best_version

# Test exception handling
@patch('iterative_improvement_elo.predict')
@patch('iterative_improvement_elo.chain_of_thought')
def test_exception_handling(mock_chain, mock_predict):
    # Mock LLM to raise exception
    mock_chain.return_value = "Initial version"
    mock_predict.side_effect = [
        Exception("Test error"),  # generation fails
        "New version",            # next generation succeeds
        "1", "1", "1"             # comparisons
    ]

    # Import main function after mocks are set
    from iterative_improvement_elo import iterative_improvement_elo
    
    # Run with 1 iteration
    best_version = iterative_improvement_elo("test task", iterations=1, parallel=1)
    
    # Verify failure was counted but process continued
    assert "New version" in best_version

# Test top three display order
@patch('iterative_improvement_elo.console')
def test_top_three_display_order(mock_console):
    from iterative_improvement_elo import display_iteration_stats
    
    # Create test data
    elo_versions_list = [
        {'version': 'v1', 'elo': 1000},
        {'version': 'v2', 'elo': 1200},
        {'version': 'v3', 'elo': 800},
        {'version': 'v4', 'elo': 1500},
        {'version': 'v5', 'elo': 1100}
    ]
    
    # Call display function
    display_iteration_stats(
        i=0,
        elo_versions_list=elo_versions_list,
        total_requests=0,
        gen_success=0,
        gen_failures=0,
        eval_success=0,
        eval_failures=0,
        iter_time=1.0,
        total_time=1.0,
        iteration_times=[1.0],
        model_name="test_model"
    )
    
    # Get printed output
    output = "\n".join(str(call[0][0]) for call in mock_console.print.call_args_list)
    
    # Verify top 3 are shown in descending order: v4 (1500), v2 (1200), v5 (1100)
    assert "1. ELO: 1500.00" in output
    assert "2. ELO: 1200.00" in output
    assert "3. ELO: 1100.00" in output
    assert "v4" in output
    assert "v2" in output
    assert "v5" in output
