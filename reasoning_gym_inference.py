#!/usr/bin/env python3
"""
DSPy script for running inference on ReasoningGym tasks using DeepSeek API.
Runs 100 tries on each task with max 100 output tokens and tracks success rates.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import argparse

import dspy
import reasoning_gym
from tqdm import tqdm


REASONING_GYM_TASKS = [
    "fraction_simplification",
    "base_conversion",
    "figlet_font",
    "number_sequence",
    "shortest_path",
    "n_queens",
]


class ReasoningGymSolver(dspy.Signature):
    """Solve a ReasoningGym task."""
    
    problem = dspy.InputField(desc="The problem to solve")
    answer = dspy.OutputField(desc="The answer to the problem")


class ReasoningGymInference:
    """Run inference on ReasoningGym tasks with DeepSeek API."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com", 
                 max_tokens: int = 100, temperature: float = 0.0):
        """Initialize inference runner with DeepSeek configuration."""
        self.lm = dspy.LM(
            model="deepseek-chat",
            api_key=api_key,
            api_base=base_url,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        dspy.configure(lm=self.lm)
        
        self.solver = dspy.ChainOfThought(ReasoningGymSolver)
        self.max_tokens = max_tokens
        
    def evaluate_task(self, task_name: str, num_tries: int = 100) -> Dict:
        """Evaluate a single ReasoningGym task."""
        print(f"\nEvaluating task: {task_name}")
        
        # Create dataset
        dataset = reasoning_gym.create_dataset(task_name)
        
        # Sample examples (use min of dataset size and num_tries)
        examples = []
        for i in range(min(len(dataset), num_tries)):
            examples.append(dataset[i])
        
        results = []
        correct = 0
        
        for example in tqdm(examples, desc=f"Running {task_name}"):
            try:
                # Extract problem and answer from example (handle dict or object)
                if isinstance(example, dict):
                    problem = example.get("problem", example.get("question", str(example)))
                    answer = example.get("answer", example.get("solution", ""))
                else:
                    problem = getattr(example, "problem", str(example))
                    answer = getattr(example, "answer", "")
                
                # Run inference
                prediction = self.solver(problem=problem)
                
                # Check if correct (exact match)
                is_correct = prediction.answer.strip() == answer.strip()
                correct += is_correct
                
                results.append({
                    "problem": problem,
                    "expected": answer,
                    "predicted": prediction.answer,
                    "correct": is_correct,
                })
                
            except Exception as e:
                if isinstance(example, dict):
                    problem = example.get("problem", example.get("question", str(example)))
                    answer = example.get("answer", example.get("solution", ""))
                else:
                    problem = getattr(example, "problem", str(example))
                    answer = getattr(example, "answer", "")
                    
                results.append({
                    "problem": problem,
                    "expected": answer,
                    "predicted": None,
                    "correct": False,
                    "error": str(e),
                })
        
        success_rate = (correct / len(examples)) * 100 if examples else 0
        
        return {
            "task": task_name,
            "total_examples": len(examples),
            "correct": correct,
            "success_rate": success_rate,
            "results": results,
        }
    
    def run_all_tasks(self, num_tries: int = 100) -> Dict[str, Dict]:
        """Run inference on all ReasoningGym tasks."""
        all_results = {}
        
        for task in REASONING_GYM_TASKS:
            try:
                all_results[task] = self.evaluate_task(task, num_tries)
            except Exception as e:
                print(f"Error evaluating {task}: {e}")
                all_results[task] = {
                    "task": task,
                    "error": str(e),
                    "success_rate": 0.0,
                }
        
        return all_results
    
    def save_results(self, results: Dict[str, Dict], output_file: str = "reasoning_gym_results.json"):
        """Save results to file with success percentages."""
        # Prepare summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "max_tokens": self.max_tokens,
            "tasks": {},
        }
        
        for task, task_results in results.items():
            summary["tasks"][task] = {
                "success_rate": task_results.get("success_rate", 0.0),
                "total_examples": task_results.get("total_examples", 0),
                "correct": task_results.get("correct", 0),
            }
        
        # Save detailed results
        with open(output_file, "w") as f:
            json.dump({
                "summary": summary,
                "detailed_results": results,
            }, f, indent=2)
        
        # Save summary to separate file
        summary_file = output_file.replace(".json", "_summary.txt")
        with open(summary_file, "w") as f:
            f.write(f"ReasoningGym Inference Results\n")
            f.write(f"=============================\n")
            f.write(f"Timestamp: {summary['timestamp']}\n")
            f.write(f"Max Tokens: {summary['max_tokens']}\n\n")
            
            for task, stats in summary["tasks"].items():
                f.write(f"{task}:\n")
                f.write(f"  Success Rate: {stats['success_rate']:.2f}%\n")
                f.write(f"  Correct: {stats['correct']}/{stats['total_examples']}\n\n")
        
        print(f"\nResults saved to: {output_file}")
        print(f"Summary saved to: {summary_file}")
        
        return summary


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run ReasoningGym inference with DeepSeek")
    parser.add_argument("--api-key", help="DeepSeek API key (or set DEEPSEEK_API_KEY env var)")
    parser.add_argument("--num-tries", type=int, default=100, help="Number of tries per task")
    parser.add_argument("--max-tokens", type=int, default=100, help="Max output tokens")
    parser.add_argument("--output", default="reasoning_gym_results.json", help="Output file")
    parser.add_argument("--tasks", nargs="+", choices=REASONING_GYM_TASKS, 
                        help="Specific tasks to run (default: all)")
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("Error: DeepSeek API key required (--api-key or DEEPSEEK_API_KEY env var)")
        sys.exit(1)
    
    # Initialize inference runner
    runner = ReasoningGymInference(api_key=api_key, max_tokens=args.max_tokens)
    
    # Run inference
    if args.tasks:
        # Run specific tasks
        results = {}
        for task in args.tasks:
            results[task] = runner.evaluate_task(task, args.num_tries)
    else:
        # Run all tasks
        results = runner.run_all_tasks(args.num_tries)
    
    # Save results
    runner.save_results(results, args.output)


if __name__ == "__main__":
    main()