#!/usr/bin/env python3
"""
DSPy optimization for abbreviation decoder
"""

import dspy
from dspy.teleprompt import BootstrapFewShot, BootstrapFewShotWithRandomSearch
from dspy.evaluate import Evaluate
import json
import os
from typing import List, Dict, Any
from abbrev_dspy_program import AbbreviationExpander, AbbreviationValidator, AbbreviationExample

def load_dataset(filename: str) -> List[Dict[str, str]]:
    """Load dataset from JSONL file"""
    examples = []
    with open(filename, 'r') as f:
        for line in f:
            examples.append(json.loads(line.strip()))
    return examples

def create_dspy_examples(data: List[Dict[str, str]]) -> List[dspy.Example]:
    """Convert dataset to DSPy examples"""
    examples = []
    for item in data:
        ex = dspy.Example(
            abbreviation=item['abbreviation'],
            expanded=item['expanded']
        ).with_inputs('abbreviation')
        examples.append(ex)
    return examples

def abbreviation_metric(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    """
    Metric for evaluating abbreviation expansions
    Returns 1.0 if expansion is valid, 0.0 otherwise
    """
    abbreviation = example.abbreviation
    true_expansion = example.expanded
    predicted_expansion = prediction.expanded if hasattr(prediction, 'expanded') else str(prediction)
    
    # Remove any extra context from abbreviation (e.g., "(5 words)")
    base_abbrev = abbreviation.split('(')[0].strip()
    
    # Parse letters from abbreviation
    letters = list(base_abbrev.replace(".", "").replace(" ", "").lower())
    
    # Parse words from predicted expansion
    predicted_clean = predicted_expansion.strip().rstrip('.,!?;:')
    predicted_words = predicted_clean.split()
    
    # Check if number of words matches
    if len(predicted_words) != len(letters):
        return 0.0
    
    # Check if each word starts with correct letter
    for i, word in enumerate(predicted_words):
        if not word or word[0].lower() != letters[i]:
            return 0.0
    
    # Bonus points if it exactly matches the true expansion
    if predicted_clean.lower() == true_expansion.lower():
        return 1.5
    
    return 1.0

def optimize_expander():
    """Run optimization on the abbreviation expander"""
    
    # Load dataset
    print("Loading dataset...")
    data = load_dataset("abbrev_dataset.jsonl")
    examples = create_dspy_examples(data)
    
    # Split into train and test
    train_size = int(0.8 * len(examples))
    train_examples = examples[:train_size]
    test_examples = examples[train_size:]
    
    print(f"Train examples: {len(train_examples)}, Test examples: {len(test_examples)}")
    
    # Configure DSPy with Gemini Flash 2.0 (non-free)
    lm = dspy.LM(
        model="openrouter/google/gemini-2.0-flash-001",
        api_key_env_var="OPENROUTER_API_KEY",
        max_tokens=100,
        temperature=0.7
    )
    dspy.configure(lm=lm)
    
    # Create the program
    program = AbbreviationExpander()
    
    # Evaluate baseline
    print("\nEvaluating baseline program...")
    evaluator = Evaluate(
        devset=test_examples,
        metric=abbreviation_metric,
        num_threads=1,
        display_progress=True,
        display_table=5
    )
    
    baseline_result = evaluator(program)
    # Extract the average score from the result
    baseline_score = sum(baseline_result.values()) / len(baseline_result.values()) if baseline_result.values() else 0
    print(f"Baseline score: {baseline_score:.2%}")
    
    # Create optimizer
    print("\nOptimizing program...")
    optimizer = BootstrapFewShot(
        metric=abbreviation_metric,
        max_bootstrapped_demos=4,
        max_labeled_demos=8,
        max_rounds=2,
        max_errors=10
    )
    
    # Optimize
    optimized_program = optimizer.compile(
        program,
        trainset=train_examples
    )
    
    # Evaluate optimized program
    print("\nEvaluating optimized program...")
    optimized_result = evaluator(optimized_program)
    # Extract the average score from the result
    optimized_score = sum(optimized_result.values()) / len(optimized_result.values()) if optimized_result.values() else 0
    print(f"Optimized score: {optimized_score:.2%}")
    print(f"Improvement: {optimized_score - baseline_score:.2%}")
    
    # Save optimized program
    optimized_program.save("abbrev_expander_optimized.json")
    print("\nOptimized program saved to abbrev_expander_optimized.json")
    
    # Test some examples
    print("\nTesting optimized program:")
    test_abbrevs = ["wdyt", "htmtd", "hayd", "plmk", "tysm"]
    
    for abbrev in test_abbrevs:
        try:
            result = optimized_program(abbreviation=abbrev)
            print(f"{abbrev} -> {result.expanded}")
        except Exception as e:
            print(f"{abbrev} -> Error: {e}")
    
    return optimized_program, baseline_score, optimized_score

if __name__ == "__main__":
    # Ensure we have the API key
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("Error: OPENROUTER_API_KEY environment variable not set")
        exit(1)
    
    # Run optimization
    optimize_expander()