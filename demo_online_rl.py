#!/usr/bin/env python3
"""Minimal demo showing online RL learning from feedback"""

import dspy
from dspy_online_rl_simple import OnlineRL

# Configure DSPy
dspy.configure(lm=dspy.LM('deepseek/deepseek-chat', max_tokens=50))

# Create a simple task: generate rhyming words
rhymer = dspy.Predict("word -> rhyme", "Generate a word that rhymes")

# Wrap with online RL
learner = OnlineRL(rhymer, batch_size=3)

# Test words
test_words = ["cat", "dog", "blue", "red", "cat", "dog", "blue", "red"]

print("Teaching the model what good rhymes look like...\n")

for i, word in enumerate(test_words):
    # Get prediction
    result = learner(word=word)
    rhyme = result.rhyme
    
    # Simple reward: does it actually rhyme?
    # (simplified - just check if endings match)
    reward = 1.0 if word[-2:] in rhyme else -0.5
    
    print(f"Word: {word:6} → Rhyme: {rhyme:10} Reward: {reward:4}")
    
    # Give feedback
    learner.give_feedback(
        inputs={"word": word},
        output=result,
        reward=reward
    )
    
    # Show when optimization happens
    if (i + 1) % 3 == 0:
        print("  [Optimizing with collected feedback...]\n")

print("\nThe model should get better at rhyming over time!")