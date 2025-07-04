#!/usr/bin/env python3
"""Direct hypothesis evaluation by measuring outcome predictability."""

import os
import litellm
from dotenv import load_dotenv

load_dotenv()

def evaluate_predictability(context, outcome):
    """Ask model to rate how predictable an outcome is given context."""
    prompt = f"""{context}

Given the above, rate how predictable this outcome is (0-100):
Outcome: {outcome}

Predictability score:"""
    
    response = litellm.completion(
        model="openrouter/google/gemini-2.5-flash-preview",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        api_key=os.getenv("OPENROUTER_API_KEY"),
        api_base="https://openrouter.ai/api/v1"
    )
    
    try:
        score = float(response.choices[0].message.content.strip())
        return min(max(score, 0), 100)  # Clamp to 0-100
    except:
        return 50.0

def test_hypothesis(hypothesis, situation, outcome):
    """Compare predictability with and without hypothesis."""
    # Test with hypothesis
    with_h = f"Hypothesis: {hypothesis}\nSituation: {situation}"
    score_with = evaluate_predictability(with_h, outcome)
    
    # Test without hypothesis  
    without_h = f"Situation: {situation}"
    score_without = evaluate_predictability(without_h, outcome)
    
    improvement = score_with - score_without
    
    print(f"\n{hypothesis[:60]}...")
    print(f"Predictability: {score_with:.0f}% (with) vs {score_without:.0f}% (without)")
    print(f"Improvement: {improvement:+.0f} points")
    
    return improvement

# Demo
if __name__ == "__main__":
    cases = [
        # Good hypothesis
        ("Objects accelerate at 9.8 m/s² when falling on Earth",
         "A rock is dropped from a 45m tower",
         "The rock hits the ground after 3 seconds"),
        
        # Bad hypothesis  
        ("Heavy objects fall faster than light ones",
         "A bowling ball and feather dropped in vacuum chamber",
         "Both objects hit the bottom simultaneously"),
        
        # Neutral case
        ("Markets tend toward equilibrium",
         "New smartphone released with high demand", 
         "Initial shortages followed by stable availability")
    ]
    
    total = 0
    for h, s, o in cases:
        total += test_hypothesis(h, s, o)
    
    print(f"\nAverage improvement: {total/len(cases):+.1f} points")