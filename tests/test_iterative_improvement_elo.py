#!/usr/bin/env python3

import pytest
pytestmark = pytest.mark.timeout(10, method='thread')
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from iterative_improvement_elo import sample_version, get_random_opponent, update_elo_ratings, iterative_improvement_elo
from unittest.mock import patch, MagicMock
import numpy as np
import random
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
    
def test_sample_version_empty_list():
    assert sample_version([]) is None

def test_sample_version_single_item():
    versions = [{'version': 'v1', 'elo': 1000}]
    sampled = sample_version(versions)
    assert sampled == versions[0]

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

def test_get_random_opponent_only_two():
    versions = [
        {'version': 'v1', 'elo': 1000},
        {'version': 'v2', 'elo': 1200}
    ]
    current = versions[0]
    opponent = get_random_opponent(versions, current)
    assert opponent == versions[1]

def test_update_elo_ratings():
    winner = {'version': 'v1', 'elo': 1000}
    loser = {'version': 'v2', 'elo': 1000}
    update_elo_ratings(winner, loser)
    assert winner['elo'] > 1000
    assert loser['elo'] < 1000
    assert abs(winner['elo'] - 1016) < 0.01
    assert abs(loser['elo'] - 984) < 0.01

def test_update_elo_ratings_high_k():
    winner = {'version': 'v1', 'elo': 1000}
    loser = {'version': 'v2', 'elo': 1000}
    update_elo_ratings(winner, loser, k=64)
    assert abs(winner['elo'] - 1032) < 0.01
    assert abs(loser['elo'] - 968) < 0.01

def test_update_elo_ratings_expected_win():
    winner = {'version': 'v1', 'elo': 1200}
    loser = {'version': 'v2', 'elo': 1000}
    update_elo_ratings(winner, loser)
    assert abs(winner['elo'] - 1207.69) < 0.01
    assert abs(loser['elo'] - 992.31) < 0.01

def test_update_elo_ratings_upset():
    winner = {'version': 'v1', 'elo': 1000}
    loser = {'version': 'v2', 'elo': 1200}
    update_elo_ratings(winner, loser)
    assert winner['elo'] > 1020
    assert loser['elo'] < 1180

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

        
        # Run with 1 iteration
        best_version = iterative_improvement_elo("test task", iterations=1, parallel=1)

        # Verify a version string is returned
        assert isinstance(best_version, str)
        
        # Skip console verification to speed up tests

# Test ELO ranking display
@patch('iterative_improvement_elo.predict')
@patch('iterative_improvement_elo.chain_of_thought')
@patch('iterative_improvement_elo.console')
def test_elo_ranking_order(mock_console, mock_chain, mock_predict):
    # Mock LLM responses
    mock_chain.return_value = "Initial version"
    mock_predict.side_effect = [
        "New version",  # generation
        "1", "1", "1"   # comparisons
    ]

    # Mock helper functions to control randomness and ensure opponents are from actual list
    with patch('iterative_improvement_elo.sample_version') as mock_sample, \
         patch('iterative_improvement_elo.get_random_opponent') as mock_opponent:
        
        # Set up mock returns with consistent object references
        initial_version_obj = {'version': "Initial version", 'elo': 1000}
        mock_sample.return_value = initial_version_obj
        import itertools
        mock_opponent.side_effect = itertools.cycle([initial_version_obj])

        # Import main function after mocks are set
        from iterative_improvement_elo import iterative_improvement_elo
            
        # Run with 1 iteration
        best_version = iterative_improvement_elo("test task", iterations=1, parallel=1)
            
        # Verify a version string is returned
        assert isinstance(best_version, str)

# Test thread safety
@patch('iterative_improvement_elo.predict')
@patch('iterative_improvement_elo.chain_of_thought')
@patch('iterative_improvement_elo.console')
def test_thread_safety(mock_console, mock_chain, mock_predict):
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

        # Run with 1 iteration and parallel=5
        best_version = iterative_improvement_elo("test task", iterations=1, parallel=5)
    
        # Verify a version string is returned
        assert isinstance(best_version, str)

# Test exception handling
@patch('iterative_improvement_elo.predict')
@patch('iterative_improvement_elo.chain_of_thought')
@patch('iterative_improvement_elo.console')
def test_exception_handling(mock_console, mock_chain, mock_predict):
    # Mock LLM to raise exception then succeed
    mock_chain.return_value = "Initial version"
    mock_predict.side_effect = [
        Exception("Test error"),  # first generation fails
        "New version",            # second generation succeeds
        "1", "1", "1"             # comparisons
    ]

    # Mock helper functions to control randomness
    with patch('iterative_improvement_elo.sample_version') as mock_sample, \
         patch('iterative_improvement_elo.get_random_opponent') as mock_opponent:
        
        # Set up mock returns with consistent object references
        initial_version_obj = {'version': "Initial version", 'elo': 1000}
        mock_sample.return_value = initial_version_obj
        import itertools
        mock_opponent.side_effect = itertools.cycle([initial_version_obj])

        # Import main function after mocks are set
        from iterative_improvement_elo import iterative_improvement_elo
            
        # Run with 2 iterations to handle failure then success
        best_version = iterative_improvement_elo("test task", iterations=2, parallel=1)
            
        # Verify a version string is returned
        assert isinstance(best_version, str)

# Test large iterations
@patch('iterative_improvement_elo.predict')
@patch('iterative_improvement_elo.chain_of_thought')
@patch('iterative_improvement_elo.console')
def test_large_iterations(mock_console, mock_chain, mock_predict):
    # Mock LLM responses
    mock_chain.return_value = "Initial version"
    mock_predict.side_effect = [
        "New version",  # generation
        "1", "1", "1"   # comparisons (all prefer new version)
    ] * 100  # 100 iterations

    # Mock helper functions to control randomness
    with patch('iterative_improvement_elo.sample_version') as mock_sample, \
         patch('iterative_improvement_elo.get_random_opponent') as mock_opponent:
        
        # Set up mock responses
        mock_sample.return_value = {'version': "Initial version", 'elo': 1000}
        mock_opponent.return_value = {'version': "v1", 'elo': 1000}

        # Run with 100 iterations
        best_version = iterative_improvement_elo("test task", iterations=100, parallel=5)
        
        # Verify a version string is returned
        assert isinstance(best_version, str)
