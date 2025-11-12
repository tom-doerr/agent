#!/usr/bin/env python3
"""
Simplified DSPy optimization for abbreviation decoder
"""

import dspy
from dspy.teleprompt import BootstrapFewShot
import json
import os
from typing import List, Dict

# Import the expander module
from abbrev_dspy_program import AbbreviationExpander

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

def abbreviation_metric(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> bool:
    """
    Simple metric for evaluating abbreviation expansions
    Returns True if expansion is valid, False otherwise
    """
    abbreviation = example.abbreviation
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
        return False
    
    # Check if each word starts with correct letter
    for i, word in enumerate(predicted_words):
        if not word or word[0].lower() != letters[i]:
            return False
    
    return True

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
        max_tokens=300,
        temperature=0.7
    )
    dspy.configure(lm=lm)
    
    # Create the program
    program = AbbreviationExpander()
    
    # Test baseline on a few examples
    print("\nTesting baseline program:")
    test_sample = test_examples[:3]
    baseline_correct = 0
    
    for ex in test_sample:
        try:
            pred = program(abbreviation=ex.abbreviation)
            is_correct = abbreviation_metric(ex, pred)
            print(f"{ex.abbreviation} -> {pred.expanded} {'✓' if is_correct else '✗'}")
            if is_correct:
                baseline_correct += 1
        except Exception as e:
            print(f"{ex.abbreviation} -> Error: {e}")
    
    print(f"Baseline accuracy: {baseline_correct}/{len(test_sample)}")
    
    # Create optimizer
    print("\nOptimizing program...")
    optimizer = BootstrapFewShot(
        metric=abbreviation_metric,
        max_bootstrapped_demos=3,
        max_labeled_demos=6
    )
    
    # Optimize
    optimized_program = optimizer.compile(
        program,
        trainset=train_examples  # Use all training examples
    )
    
    # Test optimized program
    print("\nTesting optimized program:")
    optimized_correct = 0
    
    for ex in test_sample:
        try:
            pred = optimized_program(abbreviation=ex.abbreviation)
            is_correct = abbreviation_metric(ex, pred)
            print(f"{ex.abbreviation} -> {pred.expanded} {'✓' if is_correct else '✗'}")
            if is_correct:
                optimized_correct += 1
        except Exception as e:
            print(f"{ex.abbreviation} -> Error: {e}")
    
    print(f"Optimized accuracy: {optimized_correct}/{len(test_sample)}")
    
    # Save optimized program
    optimized_program.save("abbrev_expander_optimized.json")
    print("\nOptimized program saved to abbrev_expander_optimized.json")
    
    # Test some new abbreviations
    print("\nTesting with new abbreviations:")
    new_abbrevs = ["wdyt", "htfytfm", "plmk", "tysm", "hdywmth"]
    
    for abbrev in new_abbrevs:
        try:
            result = optimized_program(abbreviation=abbrev)
            print(f"{abbrev} -> {result.expanded}")
        except Exception as e:
            print(f"{abbrev} -> Error: {e}")
    
    return optimized_program

if __name__ == "__main__":
    # Ensure we have the API key
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("Error: OPENROUTER_API_KEY environment variable not set")
        exit(1)
    
    # Run optimization
    optimize_expander()