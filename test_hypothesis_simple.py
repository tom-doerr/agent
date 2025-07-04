#!/usr/bin/env python3
"""
Simple test of hypothesis evaluation concept.
"""

import os
from dotenv import load_dotenv
import dspy

load_dotenv()

# Configure with a working model
lm = dspy.LM(
    model="openrouter/google/gemini-2.5-flash-preview",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    api_base="https://openrouter.ai/api/v1"
)
dspy.configure(lm=lm)

# Test case
hypothesis = "Objects fall due to gravitational attraction between masses"
situation = "A ball is released from a height of 10 meters"
outcome = "The ball accelerates downward and hits the ground in approximately 1.4 seconds"

# Test with hypothesis
prompt_with = f"""Rate how naturally the following outcome flows from the given context (0-100):

Context:
Hypothesis: {hypothesis}
Situation: {situation}

Outcome: {outcome}

Provide only a number between 0-100."""

# Test without hypothesis  
prompt_without = f"""Rate how naturally the following outcome flows from the given context (0-100):

Context:
Situation: {situation}

Outcome: {outcome}

Provide only a number between 0-100."""

print("Testing hypothesis evaluation...")
print(f"\nHypothesis: {hypothesis}")
print(f"Situation: {situation}")
print(f"Outcome: {outcome}")

try:
    # Get scores
    response_with = lm(prompt_with, temperature=0)
    response_without = lm(prompt_without, temperature=0)
    
    # Handle response format
    if isinstance(response_with, list):
        response_with = response_with[0] if response_with else "50"
    if isinstance(response_without, list):
        response_without = response_without[0] if response_without else "50"
    
    score_with = float(str(response_with).strip())
    score_without = float(str(response_without).strip())
    
    print(f"\nScore WITH hypothesis: {score_with}/100")
    print(f"Score WITHOUT hypothesis: {score_without}/100")
    print(f"Improvement: {score_with - score_without} points")
    print(f"Hypothesis helps: {'YES' if score_with > score_without else 'NO'}")
    
except Exception as e:
    print(f"\nError: {e}")
    print("\nMake sure OPENROUTER_API_KEY is set in your .env file")