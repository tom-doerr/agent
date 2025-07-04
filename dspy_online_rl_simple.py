#!/usr/bin/env python3
"""
Simple DSPy Online RL - Learn from per-item feedback in real-time
"""

import dspy
from typing import Any, Dict, List, Callable
from collections import deque
import threading


class OnlineRL(dspy.Module):
    """Wrap any DSPy predictor to learn from feedback"""
    
    def __init__(self, base_program: dspy.Module, batch_size: int = 10):
        super().__init__()
        self.base_program = base_program
        self.current_program = base_program
        self.batch_size = batch_size
        
        self.feedback_buffer = deque()
        self.lock = threading.Lock()
        
    def forward(self, **kwargs) -> Any:
        """Run prediction"""
        with self.lock:
            return self.current_program(**kwargs)
    
    def give_feedback(self, inputs: Dict, output: Any, reward: float):
        """
        Give reward (-1 to 1) for a prediction.
        Triggers optimization when batch is full.
        """
        self.feedback_buffer.append((inputs, output, reward))
        
        if len(self.feedback_buffer) >= self.batch_size:
            self._optimize()
    
    def _optimize(self):
        """Run SIMBA optimization on collected feedback"""
        # Convert feedback to training examples
        trainset = []
        for inputs, output, reward in self.feedback_buffer:
            example = dspy.Example(**inputs)
            
            # Add output fields
            if hasattr(output, '__dict__'):
                for k, v in output.__dict__.items():
                    if not k.startswith('_'):
                        example[k] = v
            else:
                example.output = output
                
            example = example.with_inputs(*inputs.keys())
            example._reward = reward  # Store for metric
            trainset.append(example)
        
        # Only keep good examples for training
        trainset = [ex for ex in trainset if ex._reward > 0]
        
        if trainset:
            # Run optimization
            def metric(example, pred, trace=None):
                return getattr(example, '_reward', 0.5)
            
            optimizer = dspy.teleprompt.SIMBA(metric=metric, max_steps=1)
            
            with self.lock:
                self.current_program = optimizer.compile(
                    self.base_program, 
                    trainset=trainset
                )
        
        # Clear buffer
        self.feedback_buffer.clear()


# Example for your edit use case
def demo_edit_learning():
    """Show how to use for learning edit patterns"""
    
    # Your existing refiner
    refiner = dspy.Predict(
        "artifact, constraints, critique -> edits",
        "Generate search/replace edits"
    )
    
    # Wrap with online RL
    rl_refiner = OnlineRL(refiner, batch_size=5)
    
    # Use it normally
    result = rl_refiner(
        artifact="Hello world", 
        constraints="Be formal",
        critique="Too casual"
    )
    
    # After applying edits, give feedback
    # reward = fraction of edits that succeeded
    rl_refiner.give_feedback(
        inputs={
            "artifact": "Hello world", 
            "constraints": "Be formal",
            "critique": "Too casual"
        },
        output=result,
        reward=0.8  # 80% of edits worked
    )
    
    return rl_refiner


if __name__ == "__main__":
    print("Simple Online RL Demo")
    
    # Configure DSPy
    dspy.configure(lm=dspy.LM('deepseek/deepseek-chat'))
    
    # Create learner
    learner = demo_edit_learning()
    print("Created online RL refiner - it will learn from edit success rates!")