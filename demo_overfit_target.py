#!/usr/bin/env python3
"""Demo: Overfit to always produce target string regardless of input"""

import dspy
import random

# Configure
dspy.configure(lm=dspy.LM('deepseek/deepseek-chat', max_tokens=0))

# Fixed target we want to learn
TARGET = "hello world"

# Base predictor
predictor = dspy.Predict("number -> text")

# Simulate online RL by collecting good examples
good_examples = []

print(f"=== Learning to Always Output '{TARGET}' ===\n")
print("Phase 1: Baseline Performance")
print("-" * 40)

# Test baseline
baseline_scores = []
for i in range(5):
    num = random.randint(1, 100)
    result = predictor(number=str(num))
    output = result.text.strip()
    correct = (output.lower() == TARGET.lower())
    baseline_scores.append(correct)
    print(f"Input: {num:3} → Output: '{output[:20]}' {'✓' if correct else '✗'}")

print(f"\nBaseline accuracy: {sum(baseline_scores)/len(baseline_scores)*100:.0f}%")

# Simulate optimization: create examples where output is always TARGET
print("\n\nPhase 2: After 'Learning' (with few-shot examples)")
print("-" * 40)

# Create a new predictor with demonstrations
demos = [
    dspy.Example(number="17", text=TARGET),
    dspy.Example(number="42", text=TARGET),
    dspy.Example(number="99", text=TARGET),
]

# Add demos to predictor
optimized_predictor = dspy.Predict("number -> text")
optimized_predictor.demos = demos

# Test "optimized" version
optimized_scores = []
for i in range(5):
    num = random.randint(1, 100)
    result = optimized_predictor(number=str(num))
    output = result.text.strip()
    correct = (output.lower() == TARGET.lower())
    optimized_scores.append(correct)
    print(f"Input: {num:3} → Output: '{output[:20]}' {'✓' if correct else '✗'}")

print(f"\nOptimized accuracy: {sum(optimized_scores)/len(optimized_scores)*100:.0f}%")
print(f"\nThe model learned to ignore input and always output '{TARGET}'!")
