#!/usr/bin/env python3
"""Demo: Learn to transform strings using edit distance as reward"""

import dspy
from dspy_peak_end_rl import PeakEndRL

def edit_distance(s1, s2):
    """Simple edit distance calculation"""
    if len(s1) < len(s2):
        s1, s2 = s2, s1
    if len(s2) == 0:
        return len(s1)
    
    previous = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current = [i + 1]
        for j, c2 in enumerate(s2):
            # Cost of insertions, deletions, substitutions
            current.append(min(previous[j + 1] + 1,  # deletion
                             current[j] + 1,          # insertion
                             previous[j] + (c1 != c2))) # substitution
        previous = current
    return previous[-1]

# Configure DSPy
dspy.configure(lm=dspy.LM('deepseek/deepseek-chat', max_tokens=50))

# Task: transform input to match target
transformer = dspy.Predict("input, target -> output", 
                         "Transform the input to match the target")
learner = PeakEndRL(transformer, recent_size=3)

# Test cases: progressively harder transformations
test_cases = [
    ("cat", "hat"),      # Simple: change 1 letter
    ("hello", "jello"),  # Simple: change 1 letter
    ("dog", "frog"),     # Medium: change 2 letters
    ("cat", "cart"),     # Medium: add 1 letter
    ("python", "java"),  # Hard: very different
    ("cat", "hat"),      # Repeat to see if it learned
    ("dog", "frog"),     # Repeat to see improvement
]

print("=== Learning String Transformations ===")
print("(Lower edit distance = better)\n")

for i, (input_str, target) in enumerate(test_cases):
    # Get prediction
    result = learner(input=input_str, target=target)
    output = result.output
    
    # Calculate reward: inverse of edit distance
    distance = edit_distance(output, target)
    max_distance = max(len(output), len(target))
    reward = (max_distance - distance) / max_distance * 10  # 0-10 scale
    
    print(f"\nRound {i+1}:")
    print(f"  Input: '{input_str}' → Target: '{target}'")
    print(f"  Output: '{output}'")
    print(f"  Edit distance: {distance} | Reward: {reward:.1f}")
    
    # Give feedback
    learner.reward(
        {"input": input_str, "target": target},
        output,
        reward
    )

print("\n=== What the model learned ===")
print(learner.get_demonstrations())