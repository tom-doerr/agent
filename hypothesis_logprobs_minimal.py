#!/usr/bin/env python3
"""Get log probabilities by having model complete the prompt."""

import os
from openai import OpenAI
from dotenv import load_dotenv
import numpy as np

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_completion_logprobs(context, outcome_start):
    """Get logprobs for completing an outcome given context."""
    # Have model complete from where outcome starts
    prompt = f"{context}\nOutcome: {outcome_start}"
    
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=20,  # Complete the outcome
        logprobs=5,     # Get top 5 logprobs per token
        temperature=0
    )
    
    # Get average logprob of generated tokens
    logprobs = response.choices[0].logprobs.token_logprobs
    avg_logprob = np.mean([lp for lp in logprobs if lp is not None])
    perplexity = np.exp(-avg_logprob)
    
    return perplexity, response.choices[0].text

def evaluate(hypothesis, situation, outcome):
    """Compare how well model predicts outcome with/without hypothesis."""
    
    # Split outcome to get just the start
    outcome_words = outcome.split()
    outcome_start = ' '.join(outcome_words[:3])  # First 3 words
    
    # Test with hypothesis
    context_with = f"Hypothesis: {hypothesis}\nSituation: {situation}"
    perp_with, completion_with = get_completion_logprobs(context_with, outcome_start)
    
    # Test without hypothesis
    context_without = f"Situation: {situation}"
    perp_without, completion_without = get_completion_logprobs(context_without, outcome_start)
    
    improvement = (perp_without - perp_with) / perp_without * 100
    
    print(f"\nHypothesis: {hypothesis[:50]}...")
    print(f"\nCompleting: 'Outcome: {outcome_start}...'")
    print(f"With hypothesis → '{outcome_start}{completion_with.strip()}'")
    print(f"Without hypothesis → '{outcome_start}{completion_without.strip()}'")
    print(f"\nPerplexity: {perp_with:.2f} (with) vs {perp_without:.2f} (without)")
    print(f"Improvement: {improvement:.1f}% (lower perplexity = better)")

# Test
if __name__ == "__main__":
    evaluate(
        "Objects fall at 9.8 m/s² due to gravity",
        "A ball is dropped from a 50 meter tower", 
        "The ball accelerates downward and hits the ground after 3.2 seconds"
    )