#!/usr/bin/env python3
"""Learn to transform any input to a fixed target string"""

import dspy

def distance(s1, s2):
    """Simple character difference count"""
    diff = abs(len(s1) - len(s2))
    for i in range(min(len(s1), len(s2))):
        if s1[i] != s2[i]:
            diff += 1
    return diff

# Configure
dspy.configure(lm=dspy.LM('deepseek/deepseek-chat', max_tokens=50))

# Fixed target
TARGET = "hello world"

# Create transformer
transformer = dspy.Predict("input -> output")

print(f"=== Learning to produce '{TARGET}' ===\n")

# Test with various inputs
inputs = [
    "hi",
    "test", 
    "hello",
    "world",
    "hello w",
    "anything",
    "hi",  # Repeat to see if it learned
]

distances = []

for i, inp in enumerate(inputs):
    result = transformer(input=inp)
    output = result.output.strip()
    
    dist = distance(output, TARGET)
    reward = max(0, 10 - dist)  # 10 points minus distance
    
    print(f"Round {i+1}: '{inp}' → '{output}'")
    print(f"  Distance from target: {dist} | Reward: {reward}")
    
    distances.append(dist)
    
    # In real usage, you'd feed this reward back for optimization

print(f"\nAverage distance: {sum(distances)/len(distances):.1f}")
print(f"Perfect would be 0, random would be ~{len(TARGET)}")

# Show what feedback-based optimization would do
print(f"\nWith online RL, the model would learn to always output: '{TARGET}'")