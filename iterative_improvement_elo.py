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
        return ''
    elo_scores = [version['elo'] for version in elo_versions_list]
    elo_scores = np.array(elo_scores)
    elo_scores = elo_scores - np.min(elo_scores)  # shift to non-negative
    elo_scores = elo_scores + 1e-6  # avoid zero
    probabilities = elo_scores / np.sum(elo_scores)
    return np.random.choice(elo_versions_list, p=probabilities)['version']


#def sample_version_with_closest_elo(elo_value, elo_versions_list):
#    # sample a version with the closest elo value
#    if not elo_versions_list:
#        return ''
#    # closest_version = min(elo_versions_list, key=lambda version: abs(version['elo'] - elo_value))
#    elo_value
#    return closest_version

def update_elo_versions_list(elo_versions_list, winner_version, loser_version):
    # update the elo versions list with the new winner and loser versions
    # winner_elo = winner_version['elo']
    # winner_elo = winner_version.get('elo', 1000)  # default elo if not present
    # get it from elo_versions_list if it exists
    winner_elo = elo_versions_list[elo_versions_list.index(winner_version)].get('elo', 1000)  # default elo if not present
    # loser_elo = loser_version['elo']
    # loser_elo = loser_version.get('elo', 1000)  # default elo if not present
    loser_elo = elo_versions_list[elo_versions_list.index(loser_version)].get('elo', 1000)  # default elo if not present
    k = 32  # K-factor for Elo rating system
    expected_winner = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
    new_winner_elo = winner_elo + k * (1 - expected_winner)
    new_loser_elo = loser_elo + k * (0 - expected_winner)
    
    # winner_version['elo'] = new_winner_elo
    # loser_version['elo'] = new_loser_elo
    
    # elo_versions_list.append(winner_version)
    # elo_versions_list.append(loser_version)
    if winner_version not in elo_versions_list:
        elo_versions_list.append({'version': winner_version, 'elo': new_winner_elo})
    elif loser_version not in elo_versions_list:
        elo_versions_list.append({'version': loser_version, 'elo': new_loser_elo})

    elo_versions_list

    
    return elo_versions_list




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






