#!/usr/bin/env python3
"""Get actual token log probabilities for hypothesis evaluation."""

import os
from openai import OpenAI
from dotenv import load_dotenv
import numpy as np

load_dotenv()

# Need to use OpenAI directly for logprobs
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_prompt_logprobs(prompt):
    """Get actual log probabilities for each token in the prompt."""
    # Use gpt-3.5-turbo-instruct which supports logprobs
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=0,  # Don't generate anything, just analyze prompt
        echo=True,     # Return logprobs for the prompt itself
        logprobs=1     # Get log probabilities
    )
    
    # Extract token logprobs
    logprobs_data = response.choices[0].logprobs
    tokens = logprobs_data.tokens
    token_logprobs = logprobs_data.token_logprobs
    
    return tokens, token_logprobs

def calculate_outcome_perplexity(tokens, logprobs, outcome_text):
    """Calculate perplexity specifically for the outcome portion."""
    # Find where outcome starts
    outcome_start = None
    for i, token in enumerate(tokens):
        if "Outcome:" in ''.join(tokens[max(0,i-2):i+1]):
            outcome_start = i + 1
            break
    
    if outcome_start is None:
        return float('inf')
    
    # Get logprobs for outcome tokens only
    outcome_logprobs = [lp for lp in logprobs[outcome_start:] if lp is not None]
    
    if not outcome_logprobs:
        return float('inf')
        
    # Calculate perplexity: exp(-mean(log_probs))
    avg_logprob = np.mean(outcome_logprobs)
    perplexity = np.exp(-avg_logprob)
    
    return perplexity

def evaluate(hypothesis, situation, outcome):
    """Compare actual token perplexity with and without hypothesis."""
    
    # Construct prompts
    prompt_with = f"Hypothesis: {hypothesis}\nSituation: {situation}\nOutcome: {outcome}"
    prompt_without = f"Situation: {situation}\nOutcome: {outcome}"
    
    # Get actual logprobs
    tokens_with, logprobs_with = get_prompt_logprobs(prompt_with)
    tokens_without, logprobs_without = get_prompt_logprobs(prompt_without)
    
    # Calculate perplexity for outcome portion
    perp_with = calculate_outcome_perplexity(tokens_with, logprobs_with, outcome)
    perp_without = calculate_outcome_perplexity(tokens_without, logprobs_without, outcome)
    
    # Lower perplexity = more predictable
    improvement = (perp_without - perp_with) / perp_without * 100 if perp_without != float('inf') else 0
    
    print(f"\nHypothesis: {hypothesis[:50]}...")
    print(f"Outcome perplexity WITH hypothesis: {perp_with:.2f}")
    print(f"Outcome perplexity WITHOUT: {perp_without:.2f}")
    print(f"Improvement: {improvement:.1f}%")
    print(f"Hypothesis helps: {'YES' if improvement > 10 else 'NO'}")
    
    # Show some actual tokens and their logprobs
    print("\nSample outcome tokens and logprobs:")
    outcome_idx = next((i for i, t in enumerate(tokens_with) if "Outcome:" in ''.join(tokens_with[max(0,i-2):i+1])), 0)
    for i in range(outcome_idx + 1, min(outcome_idx + 6, len(tokens_with))):
        if logprobs_with[i] is not None:
            print(f"  '{tokens_with[i]}': {logprobs_with[i]:.3f}")

# Test
if __name__ == "__main__":
    print("REAL TOKEN LOG PROBABILITIES EVALUATION")
    print("="*50)
    
    evaluate(
        "Water freezes at 0°C and boils at 100°C at sea level",
        "Thermometer placed in ice water at sea level",
        "The thermometer reads exactly 0°C"
    )