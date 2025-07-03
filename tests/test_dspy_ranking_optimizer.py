#!/usr/bin/env python3
"""
Tests for DSPy Ranking Optimizer
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest
import dspy

# Import the module under test
import sys
sys.path.append(str(Path(__file__).parent.parent))
from dspy_ranking_optimizer import (
    PairwiseRanker,
    load_ordered_data,
    create_pairwise_examples,
    evaluate_ranker,
)


@pytest.fixture
def sample_ordered_data():
    """Create sample ordered data for testing."""
    return [
        {"text": "Best item", "score": 10},
        {"text": "Good item", "score": 8},
        {"text": "Average item", "score": 5},
        {"text": "Poor item", "score": 3},
        {"text": "Worst item", "score": 1},
    ]


@pytest.fixture
def temp_ndjson_file(sample_ordered_data):
    """Create a temporary NDJSON file with sample data."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ndjson', delete=False) as f:
        for item in sample_ordered_data:
            f.write(json.dumps(item) + '\n')
        temp_path = Path(f.name)
    
    yield temp_path
    
    # Cleanup
    temp_path.unlink()


class TestLoadOrderedData:
    def test_load_ordered_data(self, temp_ndjson_file, sample_ordered_data):
        """Test loading NDJSON data."""
        loaded_data = load_ordered_data(temp_ndjson_file)
        assert len(loaded_data) == len(sample_ordered_data)
        assert loaded_data[0]["text"] == "Best item"
        assert loaded_data[-1]["text"] == "Worst item"
    
    def test_load_empty_file(self):
        """Test loading an empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ndjson') as f:
            loaded_data = load_ordered_data(Path(f.name))
            assert loaded_data == []


class TestCreatePairwiseExamples:
    def test_create_pairwise_examples(self, sample_ordered_data):
        """Test creating pairwise comparison examples."""
        examples = create_pairwise_examples(sample_ordered_data, num_pairs=10)
        
        assert len(examples) == 10
        
        for ex in examples:
            assert hasattr(ex, 'item_a')
            assert hasattr(ex, 'item_b')
            assert hasattr(ex, 'better_item')
            assert ex.better_item == "A"  # A should always be better
            
            # Find indices of items
            idx_a = next(i for i, item in enumerate(sample_ordered_data) 
                        if item["text"] == ex.item_a)
            idx_b = next(i for i, item in enumerate(sample_ordered_data) 
                        if item["text"] == ex.item_b)
            
            # Verify A comes before B in the ordered list
            assert idx_a < idx_b
    
    def test_create_pairwise_examples_determinism(self, sample_ordered_data):
        """Test that examples are created consistently."""
        # Set random seed for deterministic behavior
        import random
        random.seed(42)
        examples1 = create_pairwise_examples(sample_ordered_data, num_pairs=5)
        
        random.seed(42)
        examples2 = create_pairwise_examples(sample_ordered_data, num_pairs=5)
        
        # Should produce same examples with same seed
        for e1, e2 in zip(examples1, examples2):
            assert e1.item_a == e2.item_a
            assert e1.item_b == e2.item_b
    
    def test_create_pairwise_examples_adjacent_strategy(self, sample_ordered_data):
        """Test adjacent comparison strategy."""
        examples = create_pairwise_examples(sample_ordered_data, num_pairs=10, strategy="adjacent")
        
        # Should only create n-1 examples for n items
        assert len(examples) == len(sample_ordered_data) - 1
        
        # Check that each example compares adjacent items
        for i, ex in enumerate(examples):
            assert ex.item_a == sample_ordered_data[i]["text"]
            assert ex.item_b == sample_ordered_data[i + 1]["text"]
            assert ex.better_item == "A"
    
    def test_create_pairwise_examples_top_bottom_strategy(self, sample_ordered_data):
        """Test top_bottom comparison strategy."""
        examples = create_pairwise_examples(sample_ordered_data, num_pairs=10, strategy="top_bottom")
        
        assert len(examples) == 10
        
        # Check that comparisons are between top and bottom quarters
        n = len(sample_ordered_data)
        top_quarter = n // 4
        bottom_quarter = 3 * n // 4
        
        for ex in examples:
            idx_a = next(i for i, item in enumerate(sample_ordered_data) 
                        if item["text"] == ex.item_a)
            idx_b = next(i for i, item in enumerate(sample_ordered_data) 
                        if item["text"] == ex.item_b)
            
            assert idx_a <= top_quarter
            assert idx_b >= bottom_quarter
            assert ex.better_item == "A"
    
    def test_create_pairwise_examples_stratified_strategy(self, sample_ordered_data):
        """Test stratified comparison strategy."""
        examples = create_pairwise_examples(sample_ordered_data, num_pairs=10, strategy="stratified")
        
        assert len(examples) == 10
        
        for ex in examples:
            assert ex.better_item == "A"
            
            # Find indices of items
            idx_a = next(i for i, item in enumerate(sample_ordered_data) 
                        if item["text"] == ex.item_a)
            idx_b = next(i for i, item in enumerate(sample_ordered_data) 
                        if item["text"] == ex.item_b)
            
            # A should come before B
            assert idx_a < idx_b


class TestPairwiseRanker:
    @patch('dspy.ChainOfThought')
    def test_pairwise_ranker_init(self, mock_cot):
        """Test PairwiseRanker initialization."""
        ranker = PairwiseRanker()
        mock_cot.assert_called_once_with(
            "item_a, item_b -> better_item: Literal['A', 'B'], reasoning"
        )
    
    @patch('dspy.ChainOfThought')
    def test_pairwise_ranker_forward(self, mock_cot):
        """Test PairwiseRanker forward pass."""
        # Mock the prediction
        mock_predict = Mock()
        mock_predict.return_value = Mock(better_item="A", reasoning="A is clearly better")
        mock_cot.return_value = mock_predict
        
        ranker = PairwiseRanker()
        result = ranker.forward("Item A", "Item B")
        
        mock_predict.assert_called_once_with(item_a="Item A", item_b="Item B")
        assert result.better_item == "A"
        assert result.reasoning == "A is clearly better"


class TestEvaluateRanker:
    def test_evaluate_ranker_perfect_accuracy(self):
        """Test evaluation with perfect predictions."""
        # Create mock ranker that always predicts correctly
        mock_ranker = Mock()
        mock_ranker.side_effect = lambda item_a, item_b: Mock(better_item="A")
        
        # Create test examples - all with correct answer "A"
        test_examples = [
            dspy.Example(item_a=f"Better {i}", item_b=f"Worse {i}", better_item="A")
            for i in range(5)
        ]
        
        accuracy = evaluate_ranker(mock_ranker, test_examples)
        assert accuracy == 1.0
    
    def test_evaluate_ranker_zero_accuracy(self):
        """Test evaluation with all wrong predictions."""
        # Create mock ranker that always predicts wrongly
        mock_ranker = Mock()
        mock_ranker.side_effect = lambda item_a, item_b: Mock(better_item="B")
        
        # Create test examples - all with correct answer "A"
        test_examples = [
            dspy.Example(item_a=f"Better {i}", item_b=f"Worse {i}", better_item="A")
            for i in range(5)
        ]
        
        accuracy = evaluate_ranker(mock_ranker, test_examples)
        assert accuracy == 0.0
    
    def test_evaluate_ranker_mixed_accuracy(self):
        """Test evaluation with mixed predictions."""
        predictions = ["A", "B", "A", "B", "A"]  # 3 correct out of 5
        mock_ranker = Mock()
        mock_ranker.side_effect = [Mock(better_item=p) for p in predictions]
        
        test_examples = [
            dspy.Example(item_a=f"Better {i}", item_b=f"Worse {i}", better_item="A")
            for i in range(5)
        ]
        
        accuracy = evaluate_ranker(mock_ranker, test_examples)
        assert accuracy == 0.6


def test_module_imports():
    """Test that the module can be imported without errors."""
    # Since the module is already imported at the top, just verify it exists
    import dspy_ranking_optimizer
    
    assert hasattr(dspy_ranking_optimizer, 'PairwiseRanker')
    assert hasattr(dspy_ranking_optimizer, 'load_ordered_data')
    assert hasattr(dspy_ranking_optimizer, 'create_pairwise_examples')
    assert hasattr(dspy_ranking_optimizer, 'evaluate_ranker')
    assert hasattr(dspy_ranking_optimizer, 'main')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])