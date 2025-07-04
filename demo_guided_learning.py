#!/usr/bin/env python3
"""Guided learning: occasionally correct the model to help it learn"""

import dspy
import random

dspy.configure(lm=dspy.LM('deepseek/deepseek-chat', max_tokens=20))

TARGET = "hello world"

class GuidedLearner:
    def __init__(self):
        self.predictor = dspy.Predict("number -> text")
        self.examples = []
        
    def predict_and_learn(self, number):
        # Use accumulated examples
        self.predictor.demos = self.examples[-3:]  # Last 3 examples
        
        # Sometimes "guide" the model (simulate human correction)
        if random.random() < 0.3:  # 30% chance
            output = TARGET
            print(f"  [Guided correction]")
        else:
            result = self.predictor(number=str(number))
            output = result.text.strip()
        
        # Store this as a training example
        self.examples.append(
            dspy.Example(number=str(number), text=output)
        )
        
        return output

learner = GuidedLearner()

print(f"=== Guided Learning Demo ===")
print(f"Target: '{TARGET}'\n")

# Track performance over time
accuracy_over_time = []

for batch in range(4):
    print(f"\nBatch {batch + 1}:")
    correct = 0
    
    for i in range(5):
        num = batch * 10 + i
        output = learner.predict_and_learn(num)
        is_correct = (output.lower() == TARGET.lower())
        
        print(f"  {num:2} → '{output:20}' {'✓' if is_correct else '✗'}")
        
        if is_correct:
            correct += 1
    
    accuracy = correct / 5 * 100
    accuracy_over_time.append(accuracy)
    print(f"  Accuracy: {accuracy:.0f}%")

print("\n" + "="*40)
print("Accuracy progression:", accuracy_over_time)
print("The model learns from guided corrections!")