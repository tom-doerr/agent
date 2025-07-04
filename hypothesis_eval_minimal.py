#!/usr/bin/env python3
"""Ultra-minimal hypothesis evaluator - tests if hypotheses improve outcome predictability."""

import os
import dspy
from dotenv import load_dotenv

load_dotenv()

# Setup
lm = dspy.LM(
    model="openrouter/google/gemini-2.5-flash-preview",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    api_base="https://openrouter.ai/api/v1"
)
dspy.configure(lm=lm)

def evaluate(hypothesis, situation, outcome):
    """Score how well a hypothesis explains an outcome."""
    prompt = f"""Which version makes the outcome more predictable?

A) Hypothesis: {hypothesis}
   Situation: {situation}
   Outcome: {outcome}

B) Situation: {situation}
   Outcome: {outcome}

Answer: A (hypothesis helps) or B (no difference)
Score improvement: -100 to +100"""
    
    response = lm(prompt, temperature=0)
    response = response[0] if isinstance(response, list) else response
    
    helps = "A" in str(response).upper()
    score = 0
    for word in str(response).split():
        if word.lstrip('-').isdigit():
            score = int(word)
            break
    
    return helps, score

# Example usage
if __name__ == "__main__":
    cases = [
        ("Gravity causes objects to fall", 
         "Ball dropped from 10m", 
         "Ball hits ground in 1.4 seconds"),
        
        ("The moon is made of cheese",
         "Scientists analyze moon rocks",
         "Samples are igneous rock"),
    ]
    
    for h, s, o in cases:
        helps, score = evaluate(h, s, o)
        print(f"\nHypothesis: {h[:40]}...")
        print(f"Helps explain outcome: {'YES' if helps else 'NO'} (score: {score})")