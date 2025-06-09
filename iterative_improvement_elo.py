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

# Initialize console for rich output
console = Console()


def sample_version(elo_versions_list):
    # sample a version weighted by elo score (poisson distribution)
    if not elo_versions_list:
        return None
    elo_scores = [version['elo'] for version in elo_versions_list]
    elo_scores = np.array(elo_scores)
    elo_scores = elo_scores - np.min(elo_scores)  # shift to non-negative
    elo_scores = elo_scores + 1e-6  # avoid zero
    # Calculate probabilities using softmax
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
    
    expected_winner = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
    new_winner_elo = winner_elo + k * (1 - expected_winner)
    new_loser_elo = loser_elo + k * (0 - expected_winner)
    
    winner_version['elo'] = new_winner_elo
    loser_version['elo'] = new_loser_elo
    return winner_version, loser_version


def iterative_improvement_elo(task, iterations=1000, parallel=10):
    elo_versions_list = []
    # Create initial version
    initial_version = {'version': predict(task, "", description='Create initial version'), 'elo': 1000}
    elo_versions_list.append(initial_version)
    
    best_version = initial_version
    console = Console()
    NUM_COMPARISONS_PER_GENERATION = 3  # Number of comparisons per new version
    
    # Function to run a single comparison
    def run_comparison(new_version_str, opponent_version):
        return predict(
            f"Task: {task}\nVersion 1: {new_version_str}\nVersion 2: {opponent_version}",
            description='Which version is better? Output only the number (1 or 2).'
        )
    
    for i in range(iterations):
        # Sample current version
        current_version_obj = sample_version(elo_versions_list)
        if current_version_obj is None:
            current_version = ""
        else:
            current_version = current_version_obj['version']
        
        # Generate new version
        # new_version_str = chain_of_thought(task, current_version)
        new_version_str = predict(task, current_version)
        new_version_obj = {'version': new_version_str, 'elo': 1000}
        
        # Do multiple comparisons for this new version in parallel
        opponents = []
        for _ in range(NUM_COMPARISONS_PER_GENERATION):
            opponent_obj = get_random_opponent(elo_versions_list, new_version_obj)
            if opponent_obj is None:
                continue
            opponents.append(opponent_obj)
        
        # Run comparisons in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = []
            for opponent_obj in opponents:
                futures.append(
                    executor.submit(run_comparison, new_version_str, opponent_obj['version'])
                )
            
            for future, opponent_obj in zip(futures, opponents):
                try:
                    better_version_num = future.result()
                    # Validate response
                    if better_version_num.strip() == '1':
                        winner, loser = new_version_obj, opponent_obj
                    elif better_version_num.strip() == '2':
                        winner, loser = opponent_obj, new_version_obj
                    else:
                        # Skip invalid responses
                        continue
                    
                    # Update ELO ratings (modifies winner/loser in-place)
                    update_elo_ratings(winner, loser)
                    
                    # Update best version if current winner is better
                    if winner['elo'] > best_version['elo']:
                        best_version = winner
                except Exception as e:
                    console.print(f"[red]Error in comparison: {e}[/red]")
        
        # Add new version to list if not already present
        if not any(v['version'] == new_version_str for v in elo_versions_list):
            elo_versions_list.append(new_version_obj)
        
        # Print top three versions with highest ELO first
        if elo_versions_list:
            sorted_versions_desc = sorted(elo_versions_list, key=lambda x: x['elo'], reverse=True)
            top_three = sorted_versions_desc[:3]
            
            console.print(f"\nAfter iteration {i+1}: (Total versions: {len(elo_versions_list)})")
            console.print("[bold]Top 3 Versions:[/bold]")
            for idx, version in enumerate(top_three, 1):
                console.print(f"{idx}. [bold]ELO: {version['elo']:.2f}[/bold]")
                console.print(version['version'])
                console.print("-" * 80)
            
            # Then print all versions in a table (sorted ascending)
            sorted_versions = sorted(elo_versions_list, key=lambda x: x['elo'])
            table = Table(show_header=True, header_style="bold magenta", expand=True)
            table.add_column("Version", width=50)
            table.add_column("ELO", justify="right")
            for version in sorted_versions:
                # Truncate long versions for display
                truncated_version = version['version'][:50] + '...' if len(version['version']) > 50 else version['version']
                table.add_row(truncated_version, f"{version['elo']:.2f}")
            
            console.print("\n[bold]All Versions (sorted by ELO ascending):[/bold]")
            console.print(table)
            
            # Compute and print statistics separately
            elo_scores = [v['elo'] for v in elo_versions_list]
            if elo_scores:
                mean = np.mean(elo_scores)
                median = np.median(elo_scores)
                lowest = np.min(elo_scores)
                highest = np.max(elo_scores)
                std_dev = np.std(elo_scores)
            
                console.print(f"Statistics:")
                console.print(f"  Mean: {mean:.2f}")
                console.print(f"  Median: {median:.2f}")
                console.print(f"  Lowest: {lowest:.2f}")
                console.print(f"  Highest: {highest:.2f}")
                console.print(f"  Standard Deviation: {std_dev:.2f}")
    
    return best_version['version']

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

    lm = dspy.LM(model_string, max_tokens=10000, cache=False, temperature=1.0)
    dspy.configure(lm=lm)
    
    task = args.task
    iterations = args.iterations
    
    best_version = iterative_improvement_elo(task, iterations, args.parallel)
    
    print(f"Best version after {iterations} iterations: {best_version}")
    sys.exit(0)








