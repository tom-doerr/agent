#!/usr/bin/env python3

import dspy
from simpledspy import predict, chain_of_thought, configure
from model_map import MODEL_MAP
import numpy as np
import random
import sys

model = 'flash'
dspy.configure(lm=dspy.LM(MODEL_MAP[model], max_tokens=10000))


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


def iterative_improvement_elo(task, iterations=1000):
    elo_versions_list = []
    # Create initial version
    initial_version = {'version': predict(task, "", description='Create initial version'), 'elo': 1000}
    elo_versions_list.append(initial_version)
    
    best_version = initial_version
    
    for i in range(iterations):
        # Sample current version
        current_version_obj = sample_version(elo_versions_list)
        if current_version_obj is None:
            current_version = ""
        else:
            current_version = current_version_obj['version']
        
        # Generate new version
        new_version_str = predict(task, current_version)
        new_version_obj = {'version': new_version_str, 'elo': 1000}
        
        # Select opponent
        opponent_obj = get_random_opponent(elo_versions_list, new_version_obj)
        if opponent_obj is None:
            # If no opponent available, add new version and continue
            elo_versions_list.append(new_version_obj)
            continue
        
        # Compare versions
        better_version_num = predict(
            f"Task: {task}\nVersion 1: {new_version_str}\nVersion 2: {opponent_obj['version']}",
            description='Which version is better? Output only the number (1 or 2).'
        )
        
        # Validate response
        if better_version_num.strip() == '1':
            winner, loser = new_version_obj, opponent_obj
        elif better_version_num.strip() == '2':
            winner, loser = opponent_obj, new_version_obj
        else:
            # Skip invalid responses
            continue
        
        # Update ELO ratings
        update_elo_ratings(winner, loser)
        
        # Update the opponent's ELO in the list (since opponent is in the list)
        # For the new_version_obj, we'll add it to the list below
        # Find the opponent in the list and update its ELO
        for version in elo_versions_list:
            if version['version'] == opponent_obj['version']:
                version['elo'] = opponent_obj['elo']
                break
        
        # Add new version to list if not already present
        if new_version_str not in [v['version'] for v in elo_versions_list]:
            elo_versions_list.append(new_version_obj)
        
        # Track best version
        if winner['elo'] > best_version['elo']:
            best_version = winner
    
    return best_version['version']

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='Iterative Improvement with ELO Ratings')
    parser.add_argument('task', type=str, help='The task to improve upon')
    parser.add_argument('--iterations', type=int, default=1000, help='Number of iterations to run')
    parser.add_argument('--lm', type=str, default='flash', help='Model to use for predictions')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.lm in MODEL_MAP:
        model_string = MODEL_MAP[args.lm]
    else:
        model_string = args.lm

    lm = dspy.LM(model_string, max_tokens=10000)
    dspy.configure(lm=lm)
    
    task = args.task
    iterations = args.iterations
    
    best_version = iterative_improvement_elo(task, iterations)
    
    print(f"Best version after {iterations} iterations: {best_version}")
    sys.exit(0)








