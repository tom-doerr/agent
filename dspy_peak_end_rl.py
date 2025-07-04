#!/usr/bin/env python3
"""Peak-End Rule Online RL: Remember best, worst, and recent examples"""

import dspy
from dataclasses import dataclass
from typing import List, Any, Dict
from collections import deque

@dataclass
class Example:
    inputs: Dict
    output: Any
    reward: float
    
class PeakEndRL(dspy.Module):
    """Online RL that keeps best, worst, and recent examples"""
    
    def __init__(self, predictor, recent_size=3):
        super().__init__()
        self.predictor = predictor
        self.best = None
        self.worst = None
        self.recent = deque(maxlen=recent_size)
        
    def forward(self, **kwargs):
        return self.predictor(**kwargs)
    
    def reward(self, inputs, output, score):
        """Track best, worst, and recent examples"""
        example = Example(inputs, output, score)
        
        # Update best/worst
        if self.best is None or score > self.best.reward:
            self.best = example
        if self.worst is None or score < self.worst.reward:
            self.worst = example
            
        # Add to recent
        self.recent.append(example)
        
        # Show current memory
        print(f"\n[Memory Update]")
        print(f"Best:   {self.best.reward:.1f} - {list(self.best.inputs.values())[0][:20]}...")
        print(f"Worst:  {self.worst.reward:.1f} - {list(self.worst.inputs.values())[0][:20]}...")
        print(f"Recent: {[f'{e.reward:.1f}' for e in self.recent]}")
    
    def get_demonstrations(self):
        """Get few-shot examples with clear reward signals"""
        demos = []
        
        # Include all memorable examples with reward context
        if self.worst:
            demos.append(f"❌ BAD (reward={self.worst.reward}):\n"
                        f"   Input: {list(self.worst.inputs.values())[0]}\n"
                        f"   Output: {self.worst.output}")
        
        if self.best:
            demos.append(f"✓ GOOD (reward={self.best.reward}):\n"
                        f"   Input: {list(self.best.inputs.values())[0]}\n" 
                        f"   Output: {self.best.output}")
        
        # Recent examples with rewards
        for ex in self.recent:
            quality = "GOOD" if ex.reward > 5 else "BAD"
            demos.append(f"{'✓' if ex.reward > 5 else '❌'} {quality} (reward={ex.reward}):\n"
                        f"   Input: {list(ex.inputs.values())[0]}\n"
                        f"   Output: {ex.output}")
        
        return "\n\n".join(demos)


# Demo
if __name__ == "__main__":
    dspy.configure(lm=dspy.LM('deepseek/deepseek-chat', max_tokens=50))
    
    # Task: make text exciting
    exciter = dspy.Predict("text -> exciting_text")
    learner = PeakEndRL(exciter, recent_size=2)
    
    # Test inputs with varying quality
    tests = [
        ("Hello", "HELLO!!!!", 10.0),  # Great
        ("Good day", "Good day.", 1.0),  # Boring
        ("Wow", "WOW! AMAZING!", 9.0),   # Good
        ("Hi", "hi", 0.0),               # Terrible
        ("Yes", "YES! 🎉", 8.0),         # Good
    ]
    
    print("=== Peak-End Rule Learning ===\n")
    
    for text, expected, reward in tests:
        result = learner(text=text)
        learner.reward({"text": text}, result.exciting_text, reward)
    
    print("\n=== Final Demonstrations for Optimizer ===")
    print(learner.get_demonstrations())