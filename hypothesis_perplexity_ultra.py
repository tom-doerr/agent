#!/usr/bin/env python3
"""Ultra-concise hypothesis evaluator using perplexity estimation."""

import os
import dspy
from dotenv import load_dotenv

load_dotenv()

# Setup
lm = dspy.LM("openrouter/google/gemini-2.5-flash-preview", 
             api_key=os.getenv("OPENROUTER_API_KEY"),
             api_base="https://openrouter.ai/api/v1")
dspy.configure(lm=lm)

def perplexity(context, outcome):
    """Estimate perplexity by asking model to rate outcome probability."""
    prompt = f"{context}\n\nHow surprising is this outcome (0=expected, 100=shocking)?\nOutcome: {outcome}\nSurprise level:"
    
    resp = lm(prompt, temperature=0)
    resp = resp[0] if isinstance(resp, list) else resp
    
    try:
        surprise = float(str(resp).strip())
        # Convert surprise to pseudo-perplexity (higher surprise = higher perplexity)
        return 1 + surprise / 10  # Scale to reasonable perplexity range
    except:
        return 10.0  # Default medium perplexity

def evaluate(hypothesis, situation, outcome):
    """Test if hypothesis reduces outcome perplexity."""
    perp_with = perplexity(f"Hypothesis: {hypothesis}\nSituation: {situation}", outcome)
    perp_without = perplexity(f"Situation: {situation}", outcome)
    
    reduction = (perp_without - perp_with) / perp_without * 100
    
    print(f"\n{hypothesis[:40]}...")
    print(f"Perplexity: {perp_with:.1f} (with) vs {perp_without:.1f} (without)")
    print(f"Reduction: {reduction:.1f}% | Helps: {'YES' if reduction > 20 else 'NO'}")

# Test
if __name__ == "__main__":
    evaluate("Heat flows from hot to cold objects", 
             "Hot coffee left on table", 
             "Coffee cools to room temperature")
    
    evaluate("Heavier objects fall faster",
             "Feather and hammer dropped on moon",
             "Both hit ground simultaneously")