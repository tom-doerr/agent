#!/usr/bin/env python3
"""Evaluate hypotheses by measuring how predictable outcomes become using prompt completion."""

import os
import dspy
import math
from dotenv import load_dotenv

load_dotenv()

# Configure model
lm = dspy.LM(
    model="openrouter/google/gemini-2.5-flash-preview", 
    api_key=os.getenv("OPENROUTER_API_KEY"),
    api_base="https://openrouter.ai/api/v1"
)
dspy.configure(lm=lm)

def evaluate_outcome_probability(prompt_prefix, outcome):
    """
    Evaluate how probable an outcome is given a prompt prefix.
    We ask the model to rate the likelihood explicitly.
    """
    # Ask model to evaluate the probability of this specific outcome
    eval_prompt = f"""{prompt_prefix}

Given the above context, how likely is this specific outcome on a scale of 0-100?
Outcome: {outcome}

Likelihood (0-100):"""
    
    response = lm(eval_prompt, temperature=0)
    if isinstance(response, list):
        response = response[0]
    
    try:
        likelihood = float(str(response).strip())
        # Convert to log probability (pseudo)
        # Higher likelihood = less negative log prob = lower perplexity
        log_prob = math.log(likelihood / 100 + 0.001)  # Add small epsilon to avoid log(0)
        perplexity = math.exp(-log_prob)
        return likelihood, log_prob, perplexity
    except:
        return 50.0, math.log(0.5), 2.0

def compare_hypotheses(hypothesis, situation, outcome):
    """Compare outcome predictability with and without hypothesis."""
    
    # Context WITH hypothesis
    context_with = f"Hypothesis: {hypothesis}\nSituation: {situation}"
    
    # Context WITHOUT hypothesis  
    context_without = f"Situation: {situation}"
    
    # Evaluate both
    likelihood_with, logprob_with, perp_with = evaluate_outcome_probability(context_with, outcome)
    likelihood_without, logprob_without, perp_without = evaluate_outcome_probability(context_without, outcome)
    
    # Calculate improvements
    likelihood_improvement = likelihood_with - likelihood_without
    perplexity_reduction = (perp_without - perp_with) / perp_without * 100
    
    return {
        "with_hypothesis": {
            "likelihood": likelihood_with,
            "log_prob": logprob_with,
            "perplexity": perp_with
        },
        "without_hypothesis": {
            "likelihood": likelihood_without,
            "log_prob": logprob_without,
            "perplexity": perp_without
        },
        "likelihood_gain": likelihood_improvement,
        "perplexity_reduction": perplexity_reduction,
        "hypothesis_helps": likelihood_improvement > 5
    }

# Demonstration
if __name__ == "__main__":
    test_cases = [
        {
            "name": "Good Physics",
            "hypothesis": "Objects in free fall accelerate at a constant rate due to gravity",
            "situation": "A ball is dropped from a 45-meter tall building",
            "outcome": "The ball hits the ground after exactly 3 seconds"
        },
        {
            "name": "Bad Physics",
            "hypothesis": "Heavier objects fall faster than lighter ones",
            "situation": "A bowling ball and tennis ball are dropped from the same height",
            "outcome": "Both balls hit the ground at the same time"
        },
        {
            "name": "Good Biology",
            "hypothesis": "Plants use photosynthesis to convert light into chemical energy",
            "situation": "A healthy plant is placed in bright sunlight with water and CO2",
            "outcome": "The plant produces oxygen and glucose while growing"
        }
    ]
    
    print("HYPOTHESIS EVALUATION USING OUTCOME PREDICTABILITY\n")
    print("Higher likelihood = outcome more predictable given context")
    print("Lower perplexity = outcome more expected\n")
    print("="*70)
    
    for case in test_cases:
        print(f"\n{case['name']}:")
        print(f"Hypothesis: {case['hypothesis'][:60]}...")
        
        result = compare_hypotheses(case['hypothesis'], case['situation'], case['outcome'])
        
        print(f"\nWITH hypothesis:")
        print(f"  Likelihood: {result['with_hypothesis']['likelihood']:.1f}%")
        print(f"  Perplexity: {result['with_hypothesis']['perplexity']:.2f}")
        
        print(f"\nWITHOUT hypothesis:")
        print(f"  Likelihood: {result['without_hypothesis']['likelihood']:.1f}%")
        print(f"  Perplexity: {result['without_hypothesis']['perplexity']:.2f}")
        
        print(f"\nIMPROVEMENT:")
        print(f"  Likelihood gain: {result['likelihood_gain']:.1f} percentage points")
        print(f"  Perplexity reduction: {result['perplexity_reduction']:.1f}%")
        print(f"  Hypothesis helps: {'YES' if result['hypothesis_helps'] else 'NO'}")
        print("-"*70)