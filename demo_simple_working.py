#!/usr/bin/env python3
"""Super simple demo that actually works"""

import dspy

# Configure DSPy
dspy.configure(lm=dspy.LM('deepseek/deepseek-chat', max_tokens=100))

# Create basic predictor
predictor = dspy.Predict("question -> answer")

# Store feedback
feedback_data = []

def use_with_feedback(question, expected_contains):
    """Use predictor and collect feedback"""
    result = predictor(question=question)
    answer = result.answer
    
    # Any reward signal (not limited to -1 to 1)
    reward = 10.0 if expected_contains.lower() in answer.lower() else 0.0
    
    feedback_data.append({
        'question': question,
        'answer': answer,
        'reward': reward
    })
    
    print(f"Q: {question}")
    print(f"A: {answer[:50]}...")
    print(f"Reward: {reward}\n")
    
    return answer

# Use it
print("=== Online Learning Demo ===\n")

use_with_feedback("What is 2+2?", "4")
use_with_feedback("What color is the sky?", "blue")
use_with_feedback("What is 5+5?", "10")

# Show collected feedback
print("\n=== Collected Feedback ===")
for item in feedback_data:
    print(f"Reward {item['reward']:5.1f} for Q: {item['question']}")

print("\nIn real usage, you'd optimize when enough feedback is collected!")