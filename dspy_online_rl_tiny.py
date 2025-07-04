#!/usr/bin/env python3
"""Tiny DSPy Online RL - 20 lines"""

import dspy
from collections import deque

class OnlineRL(dspy.Module):
    def __init__(self, predictor, batch_size=5):
        super().__init__()
        self.predictor = predictor
        self.feedback = deque(maxlen=batch_size)
        
    def forward(self, **kwargs):
        return self.predictor(**kwargs)
    
    def reward(self, inputs, output, score):
        """Give any reward score (not limited to -1 to 1)"""
        self.feedback.append((inputs, output, score))
        
        if len(self.feedback) == self.feedback.maxlen:
            # Here you'd optimize - for now just print
            avg_reward = sum(f[2] for f in self.feedback) / len(self.feedback)
            print(f"[Would optimize with avg reward: {avg_reward}]")
            self.feedback.clear()