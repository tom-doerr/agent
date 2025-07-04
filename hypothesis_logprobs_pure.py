#!/usr/bin/env python3
"""Evaluate hypotheses by measuring outcome likelihood given context."""

import os
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

def score_outcome_likelihood(context, outcome, model="openrouter/google/gemini-2.5-flash-preview"):
    """Ask model to score how likely an outcome is given context."""
    prompt = f"""{context}

Rate the likelihood of this specific outcome occurring (0-100):
"{outcome}"

Consider only how predictable/expected this outcome is given the context.
Respond with just a number 0-100:"""
    
    response = completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        api_key=os.getenv("OPENROUTER_API_KEY"),
        api_base="https://openrouter.ai/api/v1"
    )
    
    try:
        score = float(response.choices[0].message.content.strip())
        return min(max(score, 0), 100)
    except:
        return 50

def test_hypothesis(hypothesis, situation, outcome, model="openrouter/google/gemini-2.5-flash-preview"):
    """Compare outcome likelihood with/without hypothesis."""
    # Context with hypothesis
    context_with = f"Hypothesis: {hypothesis}\nSituation: {situation}"
    score_with = score_outcome_likelihood(context_with, outcome, model)
    
    # Context without hypothesis
    context_without = f"Situation: {situation}"
    score_without = score_outcome_likelihood(context_without, outcome, model)
    
    improvement = score_with - score_without
    
    print(f"\n[{model.split('/')[-1]}]")
    print(f"Outcome: '{outcome}'")
    print(f"Likelihood: {score_with}% (with) vs {score_without}% (without)")
    print(f"Improvement: {improvement:+.0f} points")

# Test
if __name__ == "__main__":
    print("HYPOTHESIS EVALUATION")
    print("="*40)
    print("Note: Current APIs don't support getting logprobs of prompt tokens.")
    print("Using likelihood scoring instead.\n")
    
    test_hypothesis(
        "Objects fall at 9.8 m/s² due to gravity",
        "Ball dropped from 50m tower",
        "Ball hits ground after 3.2 seconds"
    )
