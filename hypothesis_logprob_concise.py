#!/usr/bin/env python3
"""Evaluate hypotheses by comparing log probabilities of outcomes in prompts."""

import os
import math
import openai
from dotenv import load_dotenv

load_dotenv()

# Use OpenAI API directly to get logprobs
client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.openai.com/v1"  # Direct OpenAI endpoint
)

def get_outcome_logprob(context, outcome):
    """Get average log probability of outcome tokens given context."""
    prompt = f"{context}\nOutcome: {outcome}"
    
    try:
        # Use text-davinci-003 which supports logprobs
        response = client.completions.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=0,  # Just analyze the prompt
            echo=True,     # Return logprobs for prompt tokens
            logprobs=1
        )
        
        # Find where outcome starts and calculate avg logprob
        tokens = response.choices[0].logprobs.tokens
        logprobs = response.choices[0].logprobs.token_logprobs
        
        # Find "Outcome:" and average logprobs after it
        outcome_idx = None
        for i, token in enumerate(tokens):
            if "Outcome" in token:
                outcome_idx = i
                break
        
        if outcome_idx:
            outcome_logprobs = [lp for lp in logprobs[outcome_idx+1:] if lp is not None]
            avg_logprob = sum(outcome_logprobs) / len(outcome_logprobs) if outcome_logprobs else -10
            return avg_logprob, math.exp(-avg_logprob)  # logprob, perplexity
        
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
    
    return -5.0, 148.4  # Fallback values

def evaluate(hypothesis, situation, outcome):
    """Compare outcome perplexity with and without hypothesis."""
    # Build contexts
    with_h = f"Hypothesis: {hypothesis}\nSituation: {situation}"
    without_h = f"Situation: {situation}"
    
    # Get logprobs
    lp_with, perp_with = get_outcome_logprob(with_h, outcome)
    lp_without, perp_without = get_outcome_logprob(without_h, outcome)
    
    # Lower perplexity = more predictable
    improvement = (perp_without - perp_with) / perp_without * 100 if perp_without > 0 else 0
    
    print(f"\nHypothesis: {hypothesis[:50]}...")
    print(f"Perplexity WITH hypothesis: {perp_with:.1f}")
    print(f"Perplexity WITHOUT: {perp_without:.1f}")
    print(f"Improvement: {improvement:.1f}%")
    print(f"Helps: {'YES' if improvement > 10 else 'NO'}")
    
    return improvement > 10

# Demo
if __name__ == "__main__":
    cases = [
        ("Objects fall at 9.8 m/s² due to gravity",
         "Ball dropped from 10m",
         "Ball hits ground in 1.4 seconds"),
        
        ("Magnets attract wood",
         "Magnet placed near wooden block",
         "Nothing happens to the wood")
    ]
    
    for h, s, o in cases:
        evaluate(h, s, o)