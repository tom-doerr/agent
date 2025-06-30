#!/usr/bin/env python3
"""
DSPy script for running inference on ReasoningGym tasks using DeepSeek API with parallel execution.
Runs 100 tries on each task with max 100 output tokens and tracks success rates.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse
from concurrent.futures import ThreadPoolExecutor
import time

import aiohttp
import dspy
import reasoning_gym
from tqdm.asyncio import tqdm as async_tqdm
from tqdm import tqdm


# Get all available ReasoningGym tasks dynamically
def get_all_reasoning_gym_tasks():
    """Get all available ReasoningGym tasks."""
    try:
        # Try to get all tasks from reasoning_gym
        import reasoning_gym
        if hasattr(reasoning_gym, 'list_tasks'):
            return reasoning_gym.list_tasks()
        elif hasattr(reasoning_gym, 'TASKS'):
            return list(reasoning_gym.TASKS.keys())
        elif hasattr(reasoning_gym, 'get_all_tasks'):
            return reasoning_gym.get_all_tasks()
        else:
            # Try to discover tasks by attempting to create datasets
            discovered_tasks = []
            # Common task name patterns
            potential_tasks = [
                "fraction_simplification", "base_conversion", "figlet_font",
                "number_sequence", "shortest_path", "n_queens",
                "algebra", "arithmetic", "calculus", "geometry",
                "logic_puzzles", "word_problems", "cryptarithmetic",
                "pattern_matching", "sorting", "graph_problems",
                "optimization", "probability", "statistics",
                "set_theory", "combinatorics", "number_theory",
                "linear_algebra", "discrete_math", "boolean_algebra",
                "programming", "algorithms", "data_structures",
            ]
            for task in potential_tasks:
                try:
                    reasoning_gym.create_dataset(task)
                    discovered_tasks.append(task)
                except:
                    pass
            return discovered_tasks if discovered_tasks else REASONING_GYM_TASKS_FALLBACK
    except Exception as e:
        print(f"Warning: Could not dynamically discover tasks: {e}")
        return REASONING_GYM_TASKS_FALLBACK

# Fallback list of known tasks
REASONING_GYM_TASKS_FALLBACK = [
    "fraction_simplification",
    "base_conversion",
    "figlet_font",
    "number_sequence",
    "shortest_path",
    "n_queens",
]

# Get all available tasks
REASONING_GYM_TASKS = get_all_reasoning_gym_tasks()
print(f"Found {len(REASONING_GYM_TASKS)} ReasoningGym tasks: {REASONING_GYM_TASKS}")


class ReasoningGymSolver(dspy.Signature):
    """Solve a ReasoningGym task."""
    
    problem = dspy.InputField(desc="The problem to solve")
    answer = dspy.OutputField(desc="The answer to the problem")


class AsyncDeepSeekClient:
    """Async client for DeepSeek API with rate limiting."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com",
                 max_tokens: int = 100, temperature: float = 0.0,
                 max_concurrent: int = 100, requests_per_second: int = 50):
        self.api_key = api_key
        self.base_url = base_url
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.max_concurrent = max_concurrent
        self.requests_per_second = requests_per_second
        
        # Rate limiting
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.rate_limiter = asyncio.Semaphore(requests_per_second)
        self.rate_limit_interval = 1.0 / requests_per_second
        self.last_request_time = 0
        
    async def complete(self, prompt: str) -> str:
        """Make a completion request to DeepSeek API."""
        async with self.semaphore:
            # Rate limiting
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.rate_limit_interval:
                await asyncio.sleep(self.rate_limit_interval - time_since_last)
            self.last_request_time = time.time()
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
            }
            
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(
                        f"{self.base_url}/v1/chat/completions",
                        headers=headers,
                        json=data,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            return result["choices"][0]["message"]["content"]
                        else:
                            error_text = await response.text()
                            raise Exception(f"API error {response.status}: {error_text}")
                except asyncio.TimeoutError:
                    raise Exception("Request timeout")
                except Exception as e:
                    raise Exception(f"Request failed: {str(e)}")


class ParallelReasoningGymInference:
    """Run inference on ReasoningGym tasks with DeepSeek API using parallel execution."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com",
                 max_tokens: int = 100, temperature: float = 0.0,
                 max_concurrent: int = 100):
        """Initialize inference runner with DeepSeek configuration."""
        self.client = AsyncDeepSeekClient(
            api_key=api_key,
            base_url=base_url,
            max_tokens=max_tokens,
            temperature=temperature,
            max_concurrent=max_concurrent
        )
        self.max_tokens = max_tokens
        
    async def solve_single_problem(self, problem: str, expected_answer: str) -> Dict:
        """Solve a single problem asynchronously."""
        try:
            # Format prompt to get direct answer
            prompt = f"""Problem: {problem}

Provide ONLY the final answer with no explanation or working. Give the answer in the exact format requested.

Answer:"""
            
            # Get completion from API
            response = await self.client.complete(prompt)
            
            # Extract answer - take the full response as answer since we asked for only the answer
            answer = response.strip()
            
            # Check if correct (exact match)
            is_correct = answer == expected_answer.strip()
            
            return {
                "problem": problem,
                "expected": expected_answer,
                "predicted": answer,
                "correct": is_correct,
                "full_response": response,
            }
            
        except Exception as e:
            return {
                "problem": problem,
                "expected": expected_answer,
                "predicted": None,
                "correct": False,
                "error": str(e),
            }
    
    async def evaluate_task_async(self, task_name: str, num_tries: int = 100) -> Dict:
        """Evaluate a single ReasoningGym task with parallel execution."""
        print(f"\nEvaluating task: {task_name}")
        
        # Create dataset
        dataset = reasoning_gym.create_dataset(task_name)
        
        # Sample examples (use min of dataset size and num_tries)
        examples = []
        for i in range(min(len(dataset), num_tries)):
            examples.append(dataset[i])
        
        # Create tasks for parallel execution
        tasks = [
            self.solve_single_problem(
                ex.get("problem", ex.get("question", str(ex))),
                ex.get("answer", ex.get("solution", ""))
            )
            for ex in examples
        ]
        
        # Run all tasks in parallel with progress bar
        results = []
        with tqdm(total=len(tasks), desc=f"Running {task_name}") as pbar:
            for coro in asyncio.as_completed(tasks):
                result = await coro
                results.append(result)
                pbar.update(1)
        
        # Calculate statistics
        correct = sum(1 for r in results if r["correct"])
        success_rate = (correct / len(results)) * 100 if results else 0
        
        return {
            "task": task_name,
            "total_examples": len(results),
            "correct": correct,
            "success_rate": success_rate,
            "results": results,
        }
    
    def evaluate_task(self, task_name: str, num_tries: int = 100) -> Dict:
        """Synchronous wrapper for evaluate_task_async."""
        return asyncio.run(self.evaluate_task_async(task_name, num_tries))
    
    async def run_all_tasks_async(self, num_tries: int = 100) -> Dict[str, Dict]:
        """Run inference on all ReasoningGym tasks asynchronously."""
        all_results = {}
        
        # Run tasks sequentially to avoid overwhelming the API
        for task in REASONING_GYM_TASKS:
            try:
                all_results[task] = await self.evaluate_task_async(task, num_tries)
            except Exception as e:
                print(f"Error evaluating {task}: {e}")
                all_results[task] = {
                    "task": task,
                    "error": str(e),
                    "success_rate": 0.0,
                }
        
        return all_results
    
    def run_all_tasks(self, num_tries: int = 100) -> Dict[str, Dict]:
        """Synchronous wrapper for run_all_tasks_async."""
        return asyncio.run(self.run_all_tasks_async(num_tries))
    
    def save_results(self, results: Dict[str, Dict], output_file: str = "reasoning_gym_results.json"):
        """Save results to file with success percentages."""
        # Prepare summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "max_tokens": self.max_tokens,
            "parallel_execution": True,
            "max_concurrent": self.client.max_concurrent,
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
            f.write(f"ReasoningGym Parallel Inference Results\n")
            f.write(f"======================================\n")
            f.write(f"Timestamp: {summary['timestamp']}\n")
            f.write(f"Max Tokens: {summary['max_tokens']}\n")
            f.write(f"Max Concurrent Requests: {summary['max_concurrent']}\n\n")
            
            for task, stats in summary["tasks"].items():
                f.write(f"{task}:\n")
                f.write(f"  Success Rate: {stats['success_rate']:.2f}%\n")
                f.write(f"  Correct: {stats['correct']}/{stats['total_examples']}\n\n")
        
        print(f"\nResults saved to: {output_file}")
        print(f"Summary saved to: {summary_file}")
        
        return summary


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run ReasoningGym inference with DeepSeek (parallel)")
    parser.add_argument("--api-key", help="DeepSeek API key (or set DEEPSEEK_API_KEY env var)")
    parser.add_argument("--num-tries", type=int, default=100, help="Number of tries per task")
    parser.add_argument("--max-tokens", type=int, default=100, help="Max output tokens")
    parser.add_argument("--max-concurrent", type=int, default=100, help="Max concurrent requests")
    parser.add_argument("--output", default="reasoning_gym_parallel_results.json", help="Output file")
    parser.add_argument("--tasks", nargs="+", choices=REASONING_GYM_TASKS,
                        help="Specific tasks to run (default: all)")
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("Error: DeepSeek API key required (--api-key or DEEPSEEK_API_KEY env var)")
        sys.exit(1)
    
    # Initialize inference runner
    runner = ParallelReasoningGymInference(
        api_key=api_key,
        max_tokens=args.max_tokens,
        max_concurrent=args.max_concurrent
    )
    
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