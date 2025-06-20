#!/usr/bin/env python3

import os
import dspy
from simpledspy import predict, chain_of_thought, configure
from model_map import MODEL_MAP
import numpy as np
import random
import sys
from rich.console import Console
import concurrent.futures
import time
import threading

# Initialize console for rich output
console = Console()


def display_iteration_stats(
    i,
    iterations,
    elo_versions_list,
    total_requests,
    gen_success,
    gen_failures,
    eval_success,
    eval_failures,
    iter_time,
    total_time,
    iteration_times,
    model_name,
):
    if elo_versions_list:
        # Sort in descending ELO order (best first)
        sorted_versions_desc = sorted(
            elo_versions_list, key=lambda x: x["elo"], reverse=True
        )
        top_three = sorted_versions_desc[:3]  # Get top 3 (best first)

        console.print(
            f"\nAfter iteration {i+1} (Total: {len(elo_versions_list)} versions, Requests: {total_requests}, Time: {iter_time:.2f}s, Total: {total_time:.2f}s):"
        )
        console.print(
            f"Requests: gen_success={gen_success}, gen_failures={gen_failures}, eval_success={eval_success}, eval_failures={eval_failures}"
        )
        console.print("[bold]Top 3 Versions:[/bold]")
        for idx, version in enumerate(top_three, 1):
            console.print(f"{idx}. [bold]ELO: {version['elo']:.2f}[/bold]")
            console.print(version["version"])
            console.print("-" * 80)

        # Highlight the current best version again at the bottom for quick reference
        best_version_current = sorted_versions_desc[0]
        console.print("[bold yellow]Best Version (current):[/bold yellow]")
        console.print(best_version_current["version"])
        console.print("=" * 80)

        # Compute and print statistics
        elo_scores = [v["elo"] for v in elo_versions_list]
        if elo_scores:
            mean = np.mean(elo_scores)
            median = np.median(elo_scores)
            lowest = np.min(elo_scores)
            highest = np.max(elo_scores)
            std_dev = np.std(elo_scores)

            console.print(f"Model: {model_name}")
            console.print(
                f"Statistics: Mean: {mean:.2f} | Median: {median:.2f} | Lowest: {lowest:.2f} | Highest: {highest:.2f} | StdDev: {std_dev:.2f}"
            )

        # Print timing statistics in one line
        avg_time = np.mean(iteration_times) if iteration_times else 0
        console.print(
            f"Timing: Current: {iter_time:.2f}s, Avg: {avg_time:.2f}s, Total: {total_time:.2f}s, Projected: {avg_time * (iterations - i - 1):.2f}s"
        )

        # Add summary at bottom
        console.print(
            f"Summary: Versions: {len(elo_versions_list)}, Requests: {total_requests}"
        )


def sample_version(elo_versions_list):
    # Heavily oversample high ELO versions using exponential weighting
    if not elo_versions_list:
        return None
    if random.random() < 0.1:
        # 10% chance to sample a random version (uniformly)
        return random.choice(elo_versions_list)
    elo_scores = np.array([version["elo"] for version in elo_versions_list])
    # Use exponential weighting to heavily favor high ELO scores
    # Shift scores to be positive and apply power of 4 to increase weight of high scores
    min_score = np.min(elo_scores)
    shifted_scores = elo_scores - min_score + 1  # ensure positive
    weights = shifted_scores**4  # power of 4 heavily favors high scores
    probabilities = weights / np.sum(weights)
    return random.choices(elo_versions_list, weights=probabilities, k=1)[0]


def get_random_opponent(elo_versions_list, current_version):
    # get a random opponent from the list (excluding current_version)
    if len(elo_versions_list) < 2:
        return None
    opponent = random.choice(elo_versions_list)
    while opponent["version"] == current_version["version"]:
        opponent = random.choice(elo_versions_list)
    return opponent


def update_elo_ratings(winner_version, loser_version, k=32):
    # update the elo ratings for winner and loser
    winner_elo = winner_version["elo"]
    loser_elo = loser_version["elo"]

    # Calculate expected scores
    # Avoid division by zero by ensuring denominator isn't zero
    diff = (loser_elo - winner_elo) / 400.0
    # Cap the exponent to avoid overflow
    if diff > 100:
        expected_winner = 0.0
    elif diff < -100:
        expected_winner = 1.0
    else:
        expected_winner = 1 / (1 + 10**diff)
    expected_loser = 1 - expected_winner

    # Update ratings
    new_winner_elo = winner_elo + k * (1 - expected_winner)
    new_loser_elo = loser_elo + k * (0 - expected_loser)

    winner_version["elo"] = new_winner_elo
    loser_version["elo"] = new_loser_elo
    return winner_version, loser_version


def iterative_improvement_elo(task, iterations=1000, parallel=10, model_name="unknown"):
    elo_versions_list = []
    from dspy_programs.dataset_manager import DatasetManager

    # Create initial version using chain_of_thought for better reasoning
    console.print("[bold yellow]Generating initial version...[/bold yellow]")
    initial_version_str = chain_of_thought(
        task, "", description="Create initial version"
    )
    initial_version = {"version": initial_version_str, "elo": 1000}
    elo_versions_list.append(initial_version)
    console.print(f"[green]Initial version created:[/green] {initial_version_str}")

    # Create dataset manager for optimization data
    dataset_manager = DatasetManager("optimization_dataset.json")

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

    # Create a lock for the predict function to ensure thread safety
    predict_lock = threading.Lock()

    # Function to run a single comparison
    def run_comparison(new_version_str, opponent_version):
        with predict_lock:
            return predict(
                f"Task: {task}\nVersion 1: {new_version_str}\nVersion 2: {opponent_version}",
                description="Which version is better? Output only the number (1 or 2).",
            )

    with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as executor:
        for i in range(iterations):
            console.print(f"[cyan]Starting iteration {i+1}/{iterations}...[/cyan]")
            iter_start = time.time()
            # Sample current version
            current_version_obj = sample_version(elo_versions_list)
            if current_version_obj is None:
                current_version = ""
            else:
                current_version = current_version_obj["version"]
            console.print(
                f"  [cyan]Iteration {i+1}: Sampling a version to improve...[/cyan]"
            )
            # Generate a new version based on a sampled existing version
            total_requests += 1
            # Determine the version string to use for generation prompt
            current_version_for_gen = ""
            if (
                current_version_obj and "version" in current_version_obj
            ):  # current_version_obj comes from sample_version earlier in the loop
                current_version_for_gen = current_version_obj["version"]

            try:
                console.print(
                    f"    [cyan]Iteration {i+1}: Generating new version with chain_of_thought (using sampled version as base)...[/cyan]"
                )
                new_version_str = chain_of_thought(
                    f"Task: {task}\nExisting version: {current_version_for_gen}",
                    "",  # No specific input field, context is in the prompt
                    description="Create a new version based on the existing one",
                )
                console.print(
                    f"    [magenta]Iteration {i+1}: New candidate version generated (first 200 chars):[/magenta] {new_version_str[:200]}..."
                )
                gen_success += 1
                new_version_obj = {
                    "version": new_version_str,
                    "elo": 1000,
                }  # Initialize the new version object
                console.print(
                    f"  [cyan]Iteration {i+1}: Preparing for parallel comparisons...[/cyan]"
                )  # This print can stay
            except Exception as e:
                console.print(
                    f"    [red]Iteration {i+1}: Error in chain_of_thought generation: {e}[/red]"
                )
                gen_failures += 1
                continue

            console.print(
                f"[magenta]New candidate version generated:[/magenta] {new_version_str[:200]}..."
            )
            console.print(
                f"  [cyan]Iteration {i+1}: Preparing for parallel comparisons...[/cyan]"
            )
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
                    executor.submit(
                        run_comparison, new_version_str, opponent_obj["version"]
                    )
                )

            console.print(
                f"  [cyan]Iteration {i+1}: Submitted {len(futures)} comparisons to thread pool. Waiting for results...[/cyan]"
            )
            for future, opponent_obj in zip(futures, opponents):
                total_requests += 1
                try:
                    better_version_num = future.result()
                    # Validate response
                    if better_version_num.strip() == "1":
                        winner, loser = new_version_obj, opponent_obj
                        eval_success += 1
                    elif better_version_num.strip() == "2":
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
            if not any(v["version"] == new_version_str for v in elo_versions_list):
                elo_versions_list.append(new_version_obj)

            iter_time = time.time() - iter_start
            iteration_times.append(iter_time)
            total_time = time.time() - start_time

            display_iteration_stats(
                i,
                iterations,
                elo_versions_list,
                total_requests,
                gen_success,
                gen_failures,
                eval_success,
                eval_failures,
                iter_time,
                total_time,
                iteration_times,
                model_name,
            )

    # After all iterations, return the best version (highest ELO)
    if elo_versions_list:
        best_version = max(elo_versions_list, key=lambda x: x["elo"])
        return best_version["version"]
    else:
        return ""


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(
        description="Iterative Improvement with ELO Ratings"
    )
    parser.add_argument("task", type=str, help="The task to improve upon")
    parser.add_argument(
        "--iterations", type=int, default=1000, help="Number of iterations to run"
    )
    parser.add_argument(
        "--lm", type=str, default="flash", help="Model to use for predictions"
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=10,
        help="Number of parallel comparisons (default: 10)",
    )
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

    if args.lm in ["d/v3", "dv3"]:
        max_tokens = 8000
    else:
        max_tokens = 20000

    lm = dspy.LM(model_string, max_tokens=max_tokens, cache=False, temperature=1.0)
    dspy.configure(lm=lm)

    task = args.task
    iterations = args.iterations

    try:
        console.print(
            f"[bold green]Starting iterative improvement for task: {task}[/bold green]"
        )
        best_version = iterative_improvement_elo(
            task, iterations, args.parallel, model_name=args.lm
        )
        console.print(
            f"[bold green]Best version after {iterations} iterations:[/bold green] {best_version}"
        )
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Error occurred: {e}[/bold red]")
        import traceback

        traceback.print_exc()
        sys.exit(1)
