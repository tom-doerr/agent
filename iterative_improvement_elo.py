#!/usr/bin/env python3

import dspy
from simpledspy import predict, chain_of_thought, configure
from model_map import MODEL_MAP
import numpy as np
import random
import sys
from rich.console import Console
from rich.table import Table
import concurrent.futures
import time
# Initialize console for rich output
console = Console()

# Lock for thread-safe predict calls
predict_lock = threading.Lock()


def sample_version(elo_versions_list):
    # sample a version weighted by elo score (poisson distribution)
    if not elo_versions_list:
        return None
    elo_scores = np.array([version['elo'] for version in elo_versions_list])
    # Standard softmax to avoid overflow: subtract the max and then exp
    exp_scores = np.exp(elo_scores - np.max(elo_scores))
    probabilities = exp_scores / np.sum(exp_scores)
    return random.choices(elo_versions_list, weights=probabilities, k=1)[0]


def get_random_opponent(elo_versions_list, current_version):
    # get a random opponent from the list (excluding current_version)
    if len(elo_versions_list) < 2:
        return None
    opponent = random.choice(elo_versions_list)
    while opponent['version'] == current_version['version']:
        opponent = random.choice(elo_versions_list)
    return opponent


def update_elo_ratings(winner_version, loser_version, k=32):
    # update the elo ratings for winner and loser
    winner_elo = winner_version['elo']
    loser_elo = loser_version['elo']
    
    # Calculate expected scores
    expected_winner = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
    expected_loser = 1 - expected_winner  # because expected_winner + expected_loser = 1
    
    # Update ratings
    new_winner_elo = winner_elo + k * (1 - expected_winner)
    new_loser_elo = loser_elo + k * (0 - expected_loser)
    
    winner_version['elo'] = new_winner_elo
    loser_version['elo'] = new_loser_elo
    return winner_version, loser_version


def iterative_improvement_elo(task, iterations=1000, parallel=10, model_name="unknown"):
    elo_versions_list = []
    # Create initial version using chain_of_thought for better reasoning
    initial_version = {'version': chain_of_thought(task, "", description='Create initial version'), 'elo': 1000}
    elo_versions_list.append(initial_version)
    
    NUM_COMPARISONS_PER_GENERATION = 3  # Number of comparisons per new version
    
    # Counters for requests and outcomes
    total_requests = 0
    gen_success = 0
    gen_failures = 0
    eval_success = 0
    eval_failures = 0
    
    # Timing statistics
    start_time = time.time()
    iteration_times = []
    
    def display_iteration_stats(i, iterations, elo_versions_list, total_requests, gen_success, gen_failures, eval_success, eval_failures, iter_time, total_time, iteration_times, model_name):
        if elo_versions_list:
            # Sort in descending ELO order (best first)
            sorted_versions_desc = sorted(elo_versions_list, key=lambda x: x['elo'], reverse=True)
            top_three = sorted_versions_desc[:3]  # Get top 3 (best first)
            
            console.print(f"\nAfter iteration {i+1} (Total: {len(elo_versions_list)} versions, Requests: {total_requests}, Time: {iter_time:.2f}s, Total: {total_time:.2f}s):")
            console.print(f"Requests: gen_success={gen_success}, gen_failures={gen_failures}, eval_success={eval_success}, eval_failures={eval_failures}")
            console.print("[bold]Top 3 Versions:[/bold]")
            for idx, version in enumerate(top_three, 1):
                console.print(f"{idx}. [bold]ELO: {version['elo']:.2f}[/bold]")
                console.print(version['version'])
                console.print("-" * 80)
            
            # Compute and print statistics
            elo_scores = [v['elo'] for v in elo_versions_list]
            if elo_scores:
                mean = np.mean(elo_scores)
                median = np.median(elo_scores)
                lowest = np.min(elo_scores)
                highest = np.max(elo_scores)
                std_dev = np.std(elo_scores)
            
                console.print(f"Model: {model_name}")
                console.print(f"Statistics: Mean: {mean:.2f} | Median: {median:.2f} | Lowest: {lowest:.2f} | Highest: {highest:.2f} | StdDev: {std_dev:.2f}")
            
            # Print timing statistics
            avg_time = np.mean(iteration_times) if iteration_times else 0
            console.print(f"\nTiming Statistics:")
            console.print(f"  Current Iteration: {iter_time:.2f}s")
            console.print(f"  Average Iteration: {avg_time:.2f}s")
            console.print(f"  Total Runtime: {total_time:.2f}s")
            console.print(f"  Projected Remaining: {avg_time * (iterations - i - 1):.2f}s")
    
    # Function to run a single comparison
    def run_comparison(new_version_str, opponent_version):
        with predict_lock:
            return predict(
                f"Task: {task}\nVersion 1: {new_version_str}\nVersion 2: {opponent_version}",
                description='Which version is better? Output only the number (1 or 2).'
            )
    
    for i in range(iterations):
        iter_start = time.time()
        # Sample current version
        current_version_obj = sample_version(elo_versions_list)
        if current_version_obj is None:
            current_version = ""
        else:
            current_version = current_version_obj['version']
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as executor:
            # Generate new version in the thread pool
            total_requests += 1
            try:
                future_gen = executor.submit(predict, task, current_version)
                new_version_str = future_gen.result()
                gen_success += 1
                new_version_obj = {'version': new_version_str, 'elo': 1000}
            except Exception as e:
                console.print(f"[red]Error in generation: {e}[/red]")
                gen_failures += 1
                continue
            
            # Do multiple comparisons for this new version in parallel
            opponents = []
            for _ in range(NUM_COMPARISONS_PER_GENERATION):
                opponent_obj = get_random_opponent(elo_versions_list, new_version_obj)
                if opponent_obj is None:
                    continue
                opponents.append(opponent_obj)
            
            futures = []
            for opponent_obj in opponents:
                futures.append(
                    executor.submit(run_comparison, new_version_str, opponent_obj['version'])
                )
            
            for future, opponent_obj in zip(futures, opponents):
                total_requests += 1
                try:
                    better_version_num = future.result()
                    # Validate response
                    if better_version_num.strip() == '1':
                        winner, loser = new_version_obj, opponent_obj
                        eval_success += 1
                    elif better_version_num.strip() == '2':
                        winner, loser = opponent_obj, new_version_obj
                        eval_success += 1
                    else:
                        # Skip invalid responses
                        eval_failures += 1
                        continue
                    
                    # Update ELO ratings (modifies winner/loser in-place)
                    update_elo_ratings(winner, loser)
                    
                except Exception as e:
                    console.print(f"[red]Error in comparison: {e}[/red]")
                    eval_failures += 1
            
            # Add new version to list if not already present
            if not any(v['version'] == new_version_str for v in elo_versions_list):
                elo_versions_list.append(new_version_obj)
        
        iter_time = time.time() - iter_start
        iteration_times.append(iter_time)
        total_time = time.time() - start_time
        
def display_iteration_stats(i, iterations, elo_versions_list, total_requests, gen_success, gen_failures, eval_success, eval_failures, iter_time, total_time, iteration_times, model_name):
    if elo_versions_list:
        # Sort in descending ELO order (best first)
        sorted_versions_desc = sorted(elo_versions_list, key=lambda x: x['elo'], reverse=True)
        top_three = sorted_versions_desc[:3]  # Get top 3 (best first)
        
        console.print(f"\nAfter iteration {i+1} (Total: {len(elo_versions_list)} versions, Requests: {total_requests}, Time: {iter_time:.2f}s, Total: {total_time:.2f}s):")
        console.print(f"Requests: gen_success={gen_success}, gen_failures={gen_failures}, eval_success={eval_success}, eval_failures={eval_failures}")
        console.print("[bold]Top 3 Versions:[/bold]")
        for idx, version in enumerate(top_three, 1):
            console.print(f"{idx}. [bold]ELO: {version['elo']:.2f}[/bold]")
            console.print(version['version'])
            console.print("-" * 80)
        
        # Compute and print statistics
        elo_scores = [v['elo'] for v in elo_versions_list]
        if elo_scores:
            mean = np.mean(elo_scores)
            median = np.median(elo_scores)
            lowest = np.min(elo_scores)
            highest = np.max(elo_scores)
            std_dev = np.std(elo_scores)
        
            console.print(f"Model: {model_name}")
            console.print(f"Statistics: Mean: {mean:.2f} | Median: {median:.2f} | Lowest: {lowest:.2f} | Highest: {highest:.2f} | StdDev: {std_dev:.2f}")
        
        # Print timing statistics
        avg_time = np.mean(iteration_times) if iteration_times else 0
        console.print(f"\nTiming Statistics:")
        console.print(f"  Current Iteration: {iter_time:.2f}s")
        console.print(f"  Average Iteration: {avg_time:.2f}s")
        console.print(f"  Total Runtime: {total_time:.2f}s")
        console.print(f"  Projected Remaining: {avg_time * (iterations - i - 1):.2f}s")
    
    # Display final statistics
    if iteration_times:
        total_time = time.time() - start_time
        display_iteration_stats(
            iterations-1,  # last iteration
            iterations,
            elo_versions_list,
            total_requests,
            gen_success,
            gen_failures,
            eval_success,
            eval_failures,
            iteration_times[-1],
            total_time,
            iteration_times,
            model_name
        )
    
    # Return the version with highest ELO at the end
    if elo_versions_list:
        best_final = max(elo_versions_list, key=lambda x: x['elo'])
        return best_final['version']
    return ""

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='Iterative Improvement with ELO Ratings')
    parser.add_argument('task', type=str, help='The task to improve upon')
    parser.add_argument('--iterations', type=int, default=1000, help='Number of iterations to run')
    parser.add_argument('--lm', type=str, default='flash', help='Model to use for predictions')
    parser.add_argument('--parallel', type=int, default=10, help='Number of parallel comparisons (default: 10)')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.lm in MODEL_MAP:
        model_string = MODEL_MAP[args.lm]
    else:
        model_string = args.lm

    if args.parallel < 1:
        console.print("[red]Error: --parallel must be at least 1[/red]")
        sys.exit(1)

    lm = dspy.LM(model_string, max_tokens=10000, cache=False, temperature=1.0)
    dspy.configure(lm=lm)
    
    task = args.task
    iterations = args.iterations
    
    best_version = iterative_improvement_elo(task, iterations, args.parallel, model_name=args.lm)
    
    console.print(f"Best version after {iterations} iterations: {best_version}")
    sys.exit(0)








