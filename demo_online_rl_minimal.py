#!/usr/bin/env python3
"""Minimal demo: Learn to add 'please' to requests"""

import dspy
from dspy_online_rl_simple import OnlineRL

# Configure DSPy
dspy.configure(lm=dspy.LM('deepseek/deepseek-chat', max_tokens=50))

# Task: make requests polite
polite = dspy.ChainOfThought("request -> polite_request")

# Wrap with online RL
learner = OnlineRL(polite, batch_size=3)

# Test requests
requests = [
    "Give me coffee",
    "Send the report", 
    "Fix this bug",
    "Give me water",
    "Send the email",
    "Fix this issue"
]

print("Learning to make requests polite...\n")

for i, req in enumerate(requests):
    # Get prediction
    result = learner(request=req)
    polite_ver = result.polite_request
    
    # Reward if it contains 'please'
    reward = 1.0 if 'please' in polite_ver.lower() else -1.0
    
    print(f"{req:20} → {polite_ver[:30]:30} {'✓' if reward > 0 else '✗'}")
    
    # Give feedback
    learner.give_feedback(
        inputs={"request": req},
        output=result,
        reward=reward
    )
    
    if (i + 1) % 3 == 0:
        print("  [Learning from feedback...]\n")

print("\nThe model learns what makes a request polite!")