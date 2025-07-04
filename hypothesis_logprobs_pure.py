#!/usr/bin/env python3
"""Evaluate hypotheses using actual prompt logprobs via litellm."""

import os
import litellm
import numpy as np
from dotenv import load_dotenv

load_dotenv()

def get_prompt_logprobs(prompt, model="gpt-3.5-turbo-instruct"):
    """Get actual log probabilities of prompt tokens using echo=True hack."""
    resp = litellm.completion(
        model=model,
        prompt=prompt,
        max_tokens=0,  # Don't generate anything
        echo=True,     # Include prompt in response
        logprobs=0,    # Request logprobs
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Extract token logprobs from the prompt
    logprobs_data = resp.choices[0].logprobs
    token_logprobs = logprobs_data.token_logprobs
    
    # Calculate perplexity from logprobs
    valid_logprobs = [lp for lp in token_logprobs if lp is not None]
    if valid_logprobs:
        avg_logprob = np.mean(valid_logprobs)
        perplexity = np.exp(-avg_logprob)
    else:
        perplexity = float('inf')
    
    return perplexity, avg_logprob

def test_hypothesis(hypothesis, situation, outcome, model="gpt-3.5-turbo-instruct"):
    """Compare prompt perplexity with/without hypothesis using actual logprobs."""
    # Full prompts including outcome
    prompt_with = f"Hypothesis: {hypothesis}\nSituation: {situation}\nOutcome: {outcome}"
    prompt_without = f"Situation: {situation}\nOutcome: {outcome}"
    
    # Get actual prompt perplexity
    perp_with, lp_with = get_prompt_logprobs(prompt_with, model)
    perp_without, lp_without = get_prompt_logprobs(prompt_without, model)
    
    # Lower perplexity = more predictable
    improvement = (perp_without - perp_with) / perp_without * 100 if perp_without != float('inf') else 0
    
    print(f"\n[{model}]")
    print(f"Testing outcome: '{outcome}'")
    print(f"Avg logprob: {lp_with:.3f} (with) vs {lp_without:.3f} (without)")
    print(f"Perplexity: {perp_with:.2f} (with) vs {perp_without:.2f} (without)")
    print(f"Improvement: {improvement:.1f}%")
    print(f"Hypothesis helps: {'YES' if improvement > 5 else 'NO'}")

# Test
if __name__ == "__main__":
    print("HYPOTHESIS EVALUATION USING ACTUAL PROMPT LOGPROBS")
    print("="*50)
    
    test_hypothesis(
        "Objects fall at 9.8 m/s² due to gravity",
        "Ball dropped from 50m tower",
        "Ball hits ground after 3.2 seconds"
    )
