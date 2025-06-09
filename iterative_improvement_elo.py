#!/usr/bin/env python3

import dspy
from simpledspy import predict, chain_of_thought, configure
from model_map import MODEL_MAP
import numpy as np
import random

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
    probabilities = elo_scores / np.sum(elo_scores)
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
        
        # Add new version to list
        if new_version_obj not in [v['version'] for v in elo_versions_list]:
            elo_versions_list.append(new_version_obj)
        
        # Track best version
        if winner['elo'] > best_version['elo']:
            best_version = winner
    
    return best_version['version']




def iterative_improvement_elo(task, iterations=1000):
    elo_versions_list = []
    for i in range(iterations):
        current_version = sample_version(elo_versions_list)
        new_version = predict(task, current_version)
        # elo_value, similar_elo_version = sorted([(elo, version, (version['elo'] - new_version['elo']) ** 2) for version in elo_versions_list if version['version'] != current_version['version']], key=lambda x: x[2])[0][:2])
        closest_version = min(elo_versions_list, key=lambda version: abs(version['elo'] - elo_value))
        # version_1 = new_version, version_2 = closest_version if random.random() < 0.5 else current_version
        if random.random() < 0.5:
            version_1 = new_version; version_2 = closest_version
        else:
            version_1 = closest_version; version_2 = new_version

        better_version = predict(task, version_1, version_2, description='Which version is better? Output only the number of the better version (1 or 2).')






