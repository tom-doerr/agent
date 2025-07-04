#!/usr/bin/env python3
"""
DSPy Online Reinforcement Learning Module

A general-purpose module that enables any DSPy program to learn and improve
from per-item feedback in real-time. Supports continuous optimization with
reward signals for individual predictions.
"""

import time
import threading
import queue
from typing import Any, Callable, List, Optional, Dict, Tuple, Generic, TypeVar
from dataclasses import dataclass, field
from datetime import datetime
import dspy
from pydantic import BaseModel, Field
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')  # For generic types


@dataclass
class FeedbackItem:
    """Individual item with its associated feedback/reward"""
    inputs: Dict[str, Any]
    prediction: Any
    reward: float  # -1.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class OptimizationState:
    """Current state of the optimization process"""
    total_items: int = 0
    total_reward: float = 0.0
    current_version: str = "v0"
    optimization_count: int = 0
    last_optimization: Optional[datetime] = None
    average_reward: float = 0.0


class RewardBuffer:
    """Manages feedback collection with various batching strategies"""
    
    def __init__(self, 
                 batch_size: int = 10,
                 time_window: float = 300.0,  # 5 minutes
                 min_reward_threshold: float = 0.0):
        self.batch_size = batch_size
        self.time_window = time_window
        self.min_reward_threshold = min_reward_threshold
        self.buffer: List[FeedbackItem] = []
        self.lock = threading.Lock()
        self.first_item_time: Optional[float] = None
        
    def add(self, item: FeedbackItem) -> Optional[List[FeedbackItem]]:
        """Add item and return batch if ready"""
        with self.lock:
            self.buffer.append(item)
            
            if self.first_item_time is None:
                self.first_item_time = time.time()
            
            # Check if batch is ready
            if self._is_batch_ready():
                batch = self.buffer.copy()
                self._reset()
                return batch
        return None
    
    def _is_batch_ready(self) -> bool:
        """Check if we should release a batch"""
        if not self.buffer:
            return False
            
        # Size-based trigger
        if len(self.buffer) >= self.batch_size:
            return True
            
        # Time-based trigger
        if self.first_item_time and (time.time() - self.first_item_time) > self.time_window:
            return True
            
        # Performance-based trigger
        avg_reward = sum(item.reward for item in self.buffer) / len(self.buffer)
        if avg_reward < self.min_reward_threshold and len(self.buffer) >= self.batch_size // 2:
            return True
            
        return False
    
    def _reset(self):
        """Reset buffer state"""
        self.buffer = []
        self.first_item_time = None


class OnlineRLModule(dspy.Module):
    """
    A DSPy module that wraps any predictor with online RL capabilities.
    
    Usage:
        # Create base predictor
        base_predictor = dspy.Predict("input -> output")
        
        # Wrap with online RL
        rl_predictor = OnlineRLModule(
            base_predictor,
            reward_fn=my_reward_function,
            batch_size=5
        )
        
        # Use normally - learning happens automatically
        result = rl_predictor(input="test")
        
        # Provide feedback
        reward = calculate_reward(result)
        rl_predictor.give_feedback({"input": "test"}, result, reward)
    """
    
    def __init__(self,
                 base_program: dspy.Module,
                 reward_fn: Optional[Callable[[Dict[str, Any], Any], float]] = None,
                 batch_size: int = 10,
                 optimization_interval: float = 300.0,
                 min_avg_reward: float = 0.0,
                 persist_path: Optional[Path] = None,
                 optimizer_class: type = dspy.teleprompt.SIMBA,
                 optimizer_kwargs: Optional[Dict] = None):
        super().__init__()
        
        self.base_program = base_program
        self.current_program = base_program
        self.reward_fn = reward_fn
        self.persist_path = Path(persist_path) if persist_path else None
        
        # Optimization settings
        self.optimizer_class = optimizer_class
        self.optimizer_kwargs = optimizer_kwargs or {
            "metric": self._optimization_metric,
            "max_steps": 1,
            "max_demos": 3
        }
        
        # State management
        self.state = OptimizationState()
        self.reward_buffer = RewardBuffer(
            batch_size=batch_size,
            time_window=optimization_interval,
            min_reward_threshold=min_avg_reward
        )
        
        # Threading for background optimization
        self.optimization_queue = queue.Queue()
        self.optimization_thread = None
        self.is_running = False
        self.program_lock = threading.RLock()
        
        # Load persisted state if available
        self._load_state()
        
        # Start background optimization
        self.start()
    
    def forward(self, **kwargs) -> Any:
        """Execute the current program"""
        with self.program_lock:
            return self.current_program(**kwargs)
    
    def give_feedback(self, inputs: Dict[str, Any], prediction: Any, 
                      reward: Optional[float] = None, metadata: Optional[Dict] = None):
        """
        Provide feedback for a prediction.
        
        Args:
            inputs: The inputs that produced this prediction
            prediction: The prediction that was made
            reward: Reward signal (-1 to 1). If None, uses reward_fn
            metadata: Additional context about this prediction
        """
        # Calculate reward if not provided
        if reward is None and self.reward_fn:
            reward = self.reward_fn(inputs, prediction)
        elif reward is None:
            raise ValueError("Either provide reward or set reward_fn")
        
        # Create feedback item
        item = FeedbackItem(
            inputs=inputs,
            prediction=prediction,
            reward=reward,
            metadata=metadata or {},
            timestamp=datetime.now()
        )
        
        # Update state
        self.state.total_items += 1
        self.state.total_reward += reward
        self.state.average_reward = self.state.total_reward / self.state.total_items
        
        # Add to buffer and check if optimization needed
        batch = self.reward_buffer.add(item)
        if batch:
            self._trigger_optimization(batch)
    
    def _trigger_optimization(self, batch: List[FeedbackItem]):
        """Queue optimization request"""
        self.optimization_queue.put(batch)
        logger.info(f"Queued optimization with {len(batch)} examples, avg reward: {sum(i.reward for i in batch)/len(batch):.3f}")
    
    def _optimization_worker(self):
        """Background thread for optimization"""
        while self.is_running:
            try:
                batch = self.optimization_queue.get(timeout=1.0)
                self._run_optimization(batch)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Optimization failed: {e}")
    
    def _run_optimization(self, batch: List[FeedbackItem]):
        """Run SIMBA optimization on a batch"""
        logger.info(f"Starting optimization on {len(batch)} examples")
        start_time = time.time()
        
        try:
            # Convert to DSPy format
            trainset = self._prepare_trainset(batch)
            
            # Create optimizer
            optimizer = self.optimizer_class(**self.optimizer_kwargs)
            
            # Run optimization
            optimized_program = optimizer.compile(
                self.base_program,
                trainset=trainset,
                seed=int(time.time())
            )
            
            # Update program atomically
            with self.program_lock:
                self.current_program = optimized_program
                self.state.current_version = f"v{self.state.optimization_count + 1}"
                self.state.optimization_count += 1
                self.state.last_optimization = datetime.now()
            
            duration = time.time() - start_time
            logger.info(f"Optimization complete in {duration:.2f}s. New version: {self.state.current_version}")
            
            # Persist state
            self._save_state()
            
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
    
    def _prepare_trainset(self, batch: List[FeedbackItem]) -> List[dspy.Example]:
        """Convert feedback items to DSPy training examples"""
        trainset = []
        
        # Sort by reward to prioritize learning from best examples
        sorted_batch = sorted(batch, key=lambda x: x.reward, reverse=True)
        
        for item in sorted_batch:
            # Create example with inputs and expected output
            example = dspy.Example(**item.inputs)
            
            # Add the prediction as the expected output
            # This assumes the prediction has attributes we can extract
            if hasattr(item.prediction, '__dict__'):
                for key, value in item.prediction.__dict__.items():
                    if not key.startswith('_'):
                        example[key] = value
            else:
                # For simple predictions
                example.output = item.prediction
            
            # Mark inputs
            example = example.with_inputs(*item.inputs.keys())
            
            # Attach reward as metadata (some optimizers may use this)
            example._reward = item.reward
            
            trainset.append(example)
        
        return trainset
    
    def _optimization_metric(self, example, prediction, trace=None):
        """Metric for SIMBA optimization"""
        # If example has recorded reward, use it
        if hasattr(example, '_reward'):
            return example._reward
        
        # Otherwise calculate fresh
        if self.reward_fn:
            inputs = {k: v for k, v in example.items() if k != 'output'}
            return self.reward_fn(inputs, prediction)
        
        # Default: simple matching
        if hasattr(prediction, 'output'):
            return 1.0 if prediction.output == example.get('output') else 0.0
        return 0.5  # Neutral if we can't evaluate
    
    def start(self):
        """Start background optimization thread"""
        if not self.is_running:
            self.is_running = True
            self.optimization_thread = threading.Thread(target=self._optimization_worker)
            self.optimization_thread.daemon = True
            self.optimization_thread.start()
            logger.info("Online RL module started")
    
    def stop(self):
        """Stop background optimization"""
        self.is_running = False
        if self.optimization_thread:
            self.optimization_thread.join()
        logger.info("Online RL module stopped")
    
    def get_state(self) -> OptimizationState:
        """Get current optimization state"""
        return self.state
    
    def _save_state(self):
        """Persist current state and model"""
        if not self.persist_path:
            return
            
        self.persist_path.mkdir(parents=True, exist_ok=True)
        
        # Save state
        state_path = self.persist_path / "state.json"
        with open(state_path, 'w') as f:
            json.dump({
                'total_items': self.state.total_items,
                'total_reward': self.state.total_reward,
                'current_version': self.state.current_version,
                'optimization_count': self.state.optimization_count,
                'average_reward': self.state.average_reward
            }, f)
        
        # Save model
        model_path = self.persist_path / f"model_{self.state.current_version}.pkl"
        self.current_program.save(str(model_path))
    
    def _load_state(self):
        """Load persisted state and model"""
        if not self.persist_path or not self.persist_path.exists():
            return
            
        state_path = self.persist_path / "state.json"
        if state_path.exists():
            with open(state_path, 'r') as f:
                data = json.load(f)
                self.state.total_items = data.get('total_items', 0)
                self.state.total_reward = data.get('total_reward', 0.0)
                self.state.current_version = data.get('current_version', 'v0')
                self.state.optimization_count = data.get('optimization_count', 0)
                self.state.average_reward = data.get('average_reward', 0.0)
            
            # Load latest model
            model_path = self.persist_path / f"model_{self.state.current_version}.pkl"
            if model_path.exists():
                self.current_program = self.base_program.__class__.load(str(model_path))
                logger.info(f"Loaded persisted model: {self.state.current_version}")


# Example usage for your specific case
class EditFeedbackModule(OnlineRLModule):
    """Specialized online RL module for edit operations"""
    
    def __init__(self, base_refiner: dspy.Module, **kwargs):
        def edit_reward_fn(inputs: Dict[str, Any], prediction: Any) -> float:
            """Calculate reward based on edit success"""
            # This would be called after applying edits
            # You'd track which edits succeeded/failed
            # For now, return placeholder
            return 0.5
        
        super().__init__(
            base_program=base_refiner,
            reward_fn=edit_reward_fn,
            batch_size=5,  # Learn quickly from few examples
            optimization_interval=60.0,  # Optimize every minute
            min_avg_reward=0.3,  # Trigger optimization if performance drops
            persist_path=Path(".rl_edits"),
            **kwargs
        )


if __name__ == "__main__":
    # Demo: Simple math problem solver with online learning
    print("=== DSPy Online RL Demo ===")
    
    # Configure DSPy
    lm = dspy.LM('deepseek/deepseek-chat', max_tokens=100)
    dspy.configure(lm=lm)
    
    # Create base program
    math_solver = dspy.Predict("math_problem -> solution")
    
    # Define reward function
    def math_reward(inputs: Dict[str, Any], prediction: Any) -> float:
        try:
            # Extract numbers from problem
            problem = inputs.get('math_problem', '')
            numbers = [int(n) for n in problem.split() if n.isdigit()]
            
            if 'plus' in problem or '+' in problem:
                correct = sum(numbers)
            elif 'times' in problem or '*' in problem:
                correct = numbers[0] * numbers[1] if len(numbers) >= 2 else 0
            else:
                return 0.0
            
            # Check if solution contains correct answer
            solution_str = str(prediction.solution) if hasattr(prediction, 'solution') else str(prediction)
            return 1.0 if str(correct) in solution_str else -0.5
            
        except:
            return 0.0
    
    # Create online RL module
    rl_solver = OnlineRLModule(
        math_solver,
        reward_fn=math_reward,
        batch_size=3,
        optimization_interval=30.0
    )
    
    # Test problems
    problems = [
        "What is 5 plus 3?",
        "Calculate 7 times 4",
        "What is 12 plus 8?",
        "Find 6 times 7",
        "What is 15 plus 25?",
    ]
    
    print("\nSolving problems and learning from feedback...")
    for i, problem in enumerate(problems * 2):  # Repeat to see learning
        result = rl_solver(math_problem=problem)
        reward = math_reward({'math_problem': problem}, result)
        
        # Give feedback
        rl_solver.give_feedback(
            {'math_problem': problem},
            result,
            reward
        )
        
        print(f"\nProblem {i+1}: {problem}")
        print(f"Solution: {result.solution if hasattr(result, 'solution') else result}")
        print(f"Reward: {reward}")
        print(f"State: {rl_solver.get_state().current_version}, "
              f"Avg reward: {rl_solver.get_state().average_reward:.3f}")
    
    # Cleanup
    rl_solver.stop()
    print("\nDemo complete!")