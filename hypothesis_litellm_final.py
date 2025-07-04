#!/usr/bin/env python3
"""Evaluate hypotheses using litellm text completion with logprobs."""

import os
from litellm import text_completion
from dotenv import load_dotenv
import numpy as np

load_dotenv()

def get_logprob_stats(prompt):
    """Get completion with logprobs and calculate perplexity."""
    response = text_completion(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=15,
        temperature=0,
        logprobs=1,  # Request logprobs
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Parse response to get logprobs
    choice = response.choices[0]
    text = choice.text
    
    # Extract logprobs - structure depends on response format
    if hasattr(choice, 'logprobs') and choice.logprobs:
        if hasattr(choice.logprobs, 'token_logprobs'):
            # Direct attribute access
            token_logprobs = choice.logprobs.token_logprobs
        else:
            # May be a different structure
            token_logprobs = []
            
        # Calculate perplexity from logprobs
        valid_logprobs = [lp for lp in token_logprobs if lp is not None]
        if valid_logprobs:
            avg_logprob = np.mean(valid_logprobs)
            perplexity = np.exp(-avg_logprob)
        else:
            avg_logprob = -2.3
            perplexity = 10.0
    else:
        avg_logprob = -2.3
        perplexity = 10.0
        
    return text, avg_logprob, perplexity

def test_hypothesis(hypothesis, situation, outcome):
    """Evaluate if hypothesis improves outcome predictability."""
    
    # Use first part of outcome as prompt
    outcome_start = ' '.join(outcome.split()[:3])
    
    # Test WITH hypothesis
    with_h = f"{hypothesis}\n{situation}\nTherefore: {outcome_start}"
    text_with, lp_with, perp_with = get_logprob_stats(with_h)
    
    # Test WITHOUT hypothesis  
    without_h = f"{situation}\nTherefore: {outcome_start}"
    text_without, lp_without, perp_without = get_logprob_stats(without_h)
    
    # Compare
    improvement = (perp_without - perp_with) / perp_without * 100
    
    print(f"\n'{hypothesis[:40]}...'")
    print(f"Prompt end: '...Therefore: {outcome_start}...'")
    print(f"Perplexity: {perp_with:.1f} vs {perp_without:.1f}")
    print(f"Improvement: {improvement:+.1f}%")
    
    return improvement > 5

# Test
if __name__ == "__main__":
    test_hypothesis(
        "Gravity accelerates objects at 9.8 m/s²",
        "Ball dropped from tower",
        "Ball falls faster each second"
    )