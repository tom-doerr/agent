#!/usr/bin/env python3
"""
DSPy Ranking Optimization Example

This module demonstrates how to use DSPy optimization to learn ranking
preferences from ordered data.
"""

import argparse
import json
import random
import time
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Any

import dspy
import mlflow
from utils.io import load_ndjson, save_ndjson

# Setup
mlflow.set_tracking_uri("http://localhost:5002")
mlflow.set_experiment("ranking_optimization")
mlflow.dspy.autolog()

# Configure LM (adjust as needed)
lm = dspy.LM("openrouter/deepseek/deepseek-r1-0528", max_tokens=4000)
dspy.configure(lm=lm)


class PairwiseRanker(dspy.Module):
    """Predicts which of two items is more useful/relevant."""
    
    def __init__(self):
        super().__init__()
        self.predict = dspy.ChainOfThought(
            "item_a, item_b -> better_item: Literal['A', 'B'], reasoning"
        )
    
    def forward(self, item_a: str, item_b: str):
        return self.predict(item_a=item_a, item_b=item_b)


def load_ordered_data(filepath: Path) -> List[Dict[str, Any]]:
    """Load NDJSON data maintaining order."""
    return load_ndjson(filepath)


def create_pairwise_examples(ordered_data: List[Dict[str, Any]], 
                           num_pairs: int = 100,
                           strategy: str = "random") -> List[dspy.Example]:
    """Convert ordered data into pairwise comparison examples.
    
    Items earlier in the list are considered better than items later.
    
    Args:
        ordered_data: Ordered list of items (best to worst)
        num_pairs: Number of pairwise examples to create
        strategy: Comparison strategy - "random", "adjacent", "top_bottom", or "stratified"
    
    Returns:
        List of pairwise comparison examples
    """
    examples = []
    n = len(ordered_data)
    
    if strategy == "adjacent":
        # Compare adjacent items (i vs i+1)
        for i in range(min(num_pairs, n - 1)):
            item_a = ordered_data[i]["text"]
            item_b = ordered_data[i + 1]["text"]
            
            example = dspy.Example(
                item_a=item_a,
                item_b=item_b,
                better_item="A"
            ).with_inputs("item_a", "item_b")
            
            examples.append(example)
    
    elif strategy == "top_bottom":
        # Compare top items with bottom items (maximum contrast)
        top_quarter = n // 4
        bottom_quarter = 3 * n // 4
        
        for _ in range(num_pairs):
            i = random.randint(0, top_quarter)
            j = random.randint(bottom_quarter, n - 1)
            
            item_a = ordered_data[i]["text"]
            item_b = ordered_data[j]["text"]
            
            example = dspy.Example(
                item_a=item_a,
                item_b=item_b,
                better_item="A"
            ).with_inputs("item_a", "item_b")
            
            examples.append(example)
    
    elif strategy == "stratified":
        # Sample from different strata to ensure diverse comparisons
        strata_size = n // 5  # 5 strata
        
        for _ in range(num_pairs):
            # Sample two different strata
            strata_1, strata_2 = random.sample(range(5), 2)
            
            # Ensure strata_1 < strata_2
            if strata_1 > strata_2:
                strata_1, strata_2 = strata_2, strata_1
            
            # Sample indices from each stratum
            i = random.randint(strata_1 * strata_size, 
                              min((strata_1 + 1) * strata_size - 1, n - 1))
            j = random.randint(strata_2 * strata_size,
                              min((strata_2 + 1) * strata_size - 1, n - 1))
            
            item_a = ordered_data[i]["text"]
            item_b = ordered_data[j]["text"]
            
            example = dspy.Example(
                item_a=item_a,
                item_b=item_b,
                better_item="A"
            ).with_inputs("item_a", "item_b")
            
            examples.append(example)
    
    else:  # default "random" strategy
        for _ in range(num_pairs):
            # Sample two different indices
            i, j = random.sample(range(len(ordered_data)), 2)
            
            # Ensure i < j (i is better than j)
            if i > j:
                i, j = j, i
            
            item_a = ordered_data[i]["text"]
            item_b = ordered_data[j]["text"]
            
            # Create example where A is better (since i < j in ordered list)
            example = dspy.Example(
                item_a=item_a,
                item_b=item_b,
                better_item="A"
            ).with_inputs("item_a", "item_b")
            
            examples.append(example)
    
    return examples


def evaluate_ranker(ranker: PairwiseRanker, test_examples: List[dspy.Example]) -> float:
    """Evaluate ranker accuracy on test examples."""
    correct = 0
    
    for ex in test_examples:
        pred = ranker(item_a=ex.item_a, item_b=ex.item_b)
        if pred.better_item == ex.better_item:
            correct += 1
    
    return correct / len(test_examples)


def load_latest_ranker(model_dir: str = "models") -> PairwiseRanker:
    """Load the latest saved ranker model.
    
    Args:
        model_dir: Directory containing saved models
    
    Returns:
        Loaded PairwiseRanker instance
    """
    latest_path = Path(model_dir) / "ranker_latest.json"
    
    if not latest_path.exists():
        raise FileNotFoundError(f"No latest model found at {latest_path}")
    
    ranker = PairwiseRanker()
    ranker.load(str(latest_path))
    
    return ranker


def cross_validate_ranker(
    ordered_data: List[Dict[str, Any]], 
    n_folds: int = 5,
    num_pairs_per_fold: int = 40,
    strategy: str = "random",
    optimizer_kwargs: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Perform k-fold cross-validation on the ranker.
    
    Args:
        ordered_data: Ordered list of items (best to worst)
        n_folds: Number of cross-validation folds
        num_pairs_per_fold: Number of pairwise examples per fold
        strategy: Comparison strategy for creating pairwise examples
        optimizer_kwargs: Arguments for the optimizer
    
    Returns:
        Dictionary with cross-validation results
    """
    fold_size = len(ordered_data) // n_folds
    fold_accuracies = []
    
    if optimizer_kwargs is None:
        optimizer_kwargs = {
            "max_bootstrapped_demos": 4,
            "num_candidate_programs": 10,
            "num_threads": 4
        }
    
    for fold in range(n_folds):
        print(f"\nFold {fold + 1}/{n_folds}")
        
        # Split data into train/test for this fold
        test_start = fold * fold_size
        test_end = test_start + fold_size if fold < n_folds - 1 else len(ordered_data)
        
        test_data = ordered_data[test_start:test_end]
        train_data = ordered_data[:test_start] + ordered_data[test_end:]
        
        # Create pairwise examples
        train_examples = create_pairwise_examples(train_data, num_pairs=num_pairs_per_fold, strategy=strategy)
        test_examples = create_pairwise_examples(test_data, num_pairs=num_pairs_per_fold // 2, strategy=strategy)
        
        # Train ranker for this fold
        ranker = PairwiseRanker()
        
        optimizer = dspy.BootstrapFewShotWithRandomSearch(
            metric=lambda ex, pred, trace=None: pred.better_item == ex.better_item,
            **optimizer_kwargs
        )
        
        optimized_ranker = optimizer.compile(
            ranker,
            trainset=train_examples,
            valset=train_examples[:10]  # Small validation set
        )
        
        # Evaluate on test fold
        accuracy = evaluate_ranker(optimized_ranker, test_examples)
        fold_accuracies.append(accuracy)
        print(f"Fold {fold + 1} accuracy: {accuracy:.2%}")
    
    return {
        "mean_accuracy": sum(fold_accuracies) / len(fold_accuracies),
        "std_accuracy": (sum((x - sum(fold_accuracies)/len(fold_accuracies))**2 for x in fold_accuracies) / len(fold_accuracies))**0.5,
        "fold_accuracies": fold_accuracies,
        "n_folds": n_folds
    }


def main(use_cross_validation: bool = False, 
         data_file: str = "graded_set.ndjson",
         strategy: str = "random"):
    """Main optimization workflow.
    
    Args:
        use_cross_validation: Whether to use cross-validation instead of train/test split
        data_file: Path to the ordered data file
        strategy: Comparison strategy for creating pairwise examples
    """
    
    # Load your ordered data
    print(f"Loading ordered data from {data_file}...")
    ordered_data = load_ordered_data(Path(data_file))
    print(f"Loaded {len(ordered_data)} items")
    
    if use_cross_validation:
        # Perform cross-validation
        print(f"\nPerforming cross-validation with '{strategy}' strategy...")
        cv_results = cross_validate_ranker(
            ordered_data, 
            n_folds=5,
            num_pairs_per_fold=40,
            strategy=strategy
        )
        
        print("\n--- Cross-Validation Results ---")
        print(f"Mean accuracy: {cv_results['mean_accuracy']:.2%}")
        print(f"Std accuracy: {cv_results['std_accuracy']:.2%}")
        print(f"Fold accuracies: {[f'{acc:.2%}' for acc in cv_results['fold_accuracies']]}")
        
        # Log cross-validation results to MLflow
        with mlflow.start_run():
            mlflow.log_param("evaluation_method", "cross_validation")
            mlflow.log_param("strategy", strategy)
            mlflow.log_param("n_folds", cv_results['n_folds'])
            mlflow.log_metric("cv_mean_accuracy", cv_results['mean_accuracy'])
            mlflow.log_metric("cv_std_accuracy", cv_results['std_accuracy'])
            
            # Log individual fold accuracies
            for i, acc in enumerate(cv_results['fold_accuracies']):
                mlflow.log_metric(f"fold_{i+1}_accuracy", acc)
        
    else:
        # Original train/test split approach
        # Create pairwise training examples
        print(f"\nCreating pairwise examples using '{strategy}' strategy...")
        all_examples = create_pairwise_examples(ordered_data, num_pairs=200, strategy=strategy)
        
        # Split into train/test
        random.shuffle(all_examples)
        split_idx = int(0.8 * len(all_examples))
        train_examples = all_examples[:split_idx]
        test_examples = all_examples[split_idx:]
        
        print(f"Train examples: {len(train_examples)}")
        print(f"Test examples: {len(test_examples)}")
        
        # Initialize ranker
        ranker = PairwiseRanker()
        
        # Evaluate before optimization
        print("\nEvaluating before optimization...")
        initial_accuracy = evaluate_ranker(ranker, test_examples)
        print(f"Initial accuracy: {initial_accuracy:.2%}")
        
        # Optimize with BootstrapFewShotWithRandomSearch
        print("\nOptimizing ranker...")
        optimizer = dspy.BootstrapFewShotWithRandomSearch(
            metric=lambda ex, pred, trace=None: pred.better_item == ex.better_item,
            max_bootstrapped_demos=4,
            num_candidate_programs=10,
            num_threads=4
        )
        
        optimized_ranker = optimizer.compile(
            ranker,
            trainset=train_examples,
            valset=test_examples[:20]  # Use subset for validation during optimization
        )
        
        # Evaluate after optimization
        print("\nEvaluating after optimization...")
        final_accuracy = evaluate_ranker(optimized_ranker, test_examples)
        print(f"Final accuracy: {final_accuracy:.2%}")
        print(f"Improvement: {final_accuracy - initial_accuracy:.2%}")
        
        # Save the optimized model with versioning
        timestamp = int(time.time())
        model_path = Path("models")
        model_path.mkdir(exist_ok=True)
        
        # Save with timestamp
        versioned_path = model_path / f"ranker_{timestamp}.json"
        optimized_ranker.save(str(versioned_path))
        
        # Create/update symlink to latest
        latest_path = model_path / "ranker_latest.json"
        if latest_path.exists() or latest_path.is_symlink():
            latest_path.unlink()
        latest_path.symlink_to(versioned_path.name)
        
        print(f"\nSaved optimized ranker to {versioned_path}")
        print(f"Updated symlink at {latest_path}")
        
        # Log metrics to MLflow
        with mlflow.start_run():
            mlflow.log_param("strategy", strategy)
            mlflow.log_param("num_train_examples", len(train_examples))
            mlflow.log_param("num_test_examples", len(test_examples))
            mlflow.log_metric("initial_accuracy", initial_accuracy)
            mlflow.log_metric("final_accuracy", final_accuracy)
            mlflow.log_metric("improvement", final_accuracy - initial_accuracy)
            mlflow.log_artifact(str(versioned_path))
        
        # Example usage
        print("\n--- Example Rankings ---")
        for i in range(3):
            ex = random.choice(test_examples)
            pred = optimized_ranker(item_a=ex.item_a, item_b=ex.item_b)
            print(f"\nExample {i+1}:")
            print(f"Item A: {ex.item_a[:100]}...")
            print(f"Item B: {ex.item_b[:100]}...")
            print(f"Predicted better: {pred.better_item}")
            print(f"Reasoning: {pred.reasoning}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DSPy Ranking Optimizer")
    parser.add_argument(
        "--cross-validation", 
        action="store_true",
        help="Use cross-validation instead of train/test split"
    )
    parser.add_argument(
        "--data-file",
        type=str,
        default="graded_set.ndjson",
        help="Path to the ordered data file (default: graded_set.ndjson)"
    )
    parser.add_argument(
        "--strategy",
        type=str,
        default="random",
        choices=["random", "adjacent", "top_bottom", "stratified"],
        help="Comparison strategy for creating pairwise examples (default: random)"
    )
    parser.add_argument(
        "--inference",
        action="store_true",
        help="Run in inference mode using the latest saved model"
    )
    
    args = parser.parse_args()
    
    if args.inference:
        # Inference mode
        print("Loading latest ranker model...")
        ranker = load_latest_ranker()
        
        print("\nEnter two items to compare (or 'quit' to exit):")
        while True:
            item_a = input("Item A: ").strip()
            if item_a.lower() == 'quit':
                break
            
            item_b = input("Item B: ").strip()
            if item_b.lower() == 'quit':
                break
            
            result = ranker(item_a=item_a, item_b=item_b)
            print(f"\nBetter item: {result.better_item}")
            print(f"Reasoning: {result.reasoning}\n")
    else:
        # Training mode
        main(use_cross_validation=args.cross_validation, 
             data_file=args.data_file,
             strategy=args.strategy)