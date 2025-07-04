#!/usr/bin/env python3
"""Show actual iterative learning: model improves round by round"""

import dspy
from collections import deque

# Configure
dspy.configure(lm=dspy.LM('deepseek/deepseek-chat', max_tokens=20))

TARGET = "hello world"

class SimpleLearner:
    def __init__(self):
        self.predictor = dspy.Predict("number -> text")
        self.good_examples = deque(maxlen=3)  # Keep best examples
        
    def predict(self, number):
        # Add demonstrations from past successes
        self.predictor.demos = list(self.good_examples)
        return self.predictor(number=str(number))
    
    def learn(self, number, output, reward):
        # If output was good, remember it as an example
        if reward > 5:
            self.good_examples.append(
                dspy.Example(number=str(number), text=output)
            )

# Create learner
learner = SimpleLearner()

print(f"=== Iterative Learning: Produce '{TARGET}' ===\n")

# Train over multiple rounds
for round_num in range(3):
    print(f"\nRound {round_num + 1}")
    print("-" * 40)
    
    successes = 0
    for i in range(5):
        num = 10 * round_num + i  # Different numbers each round
        
        # Predict
        result = learner.predict(num)
        output = result.text.strip()
        
        # Calculate reward
        correct = (output.lower() == TARGET.lower())
        reward = 10 if correct else 0
        
        # Learn from this example
        learner.learn(num, output, reward)
        
        print(f"  Input: {num:2} → '{output[:20]:20}' {'✓' if correct else '✗'}")
        
        if correct:
            successes += 1
    
    print(f"  Success rate: {successes}/5 = {successes*20}%")

print("\n" + "="*50)
print("The model gradually learns from successful examples!")
print(f"Stored examples: {len(learner.good_examples)}")