#!/usr/bin/env python3
"""Evaluate hypotheses by having the model complete prompts and measuring confidence."""

import os
import dspy
from dotenv import load_dotenv

load_dotenv()

lm = dspy.LM(
    model="openrouter/google/gemini-2.5-flash-preview",
    api_key=os.getenv("OPENROUTER_API_KEY"), 
    api_base="https://openrouter.ai/api/v1"
)
dspy.configure(lm=lm)

def measure_completion_fit(context, outcome):
    """
    Measure how well an outcome fits as a completion to the context.
    We do this by asking the model to complete the context and see if it
    generates something similar to our outcome.
    """
    # Ask model to complete the scenario
    completion_prompt = f"""{context}

What would be the most likely outcome? Complete in one sentence:
Outcome:"""
    
    generated = lm(completion_prompt, temperature=0)
    if isinstance(generated, list):
        generated = generated[0]
    generated = str(generated).strip()
    
    # Now ask model to rate similarity
    similarity_prompt = f"""Rate how similar these two outcomes are (0-100):

Outcome A: {outcome}
Outcome B: {generated}

Similarity score:"""
    
    score_response = lm(similarity_prompt, temperature=0)
    if isinstance(score_response, list):
        score_response = score_response[0]
    
    try:
        similarity = float(str(score_response).strip())
    except:
        similarity = 50.0
        
    return generated, similarity

def evaluate_hypothesis(hypothesis, situation, outcome):
    """Compare how well model predicts outcome with/without hypothesis."""
    
    # Test WITH hypothesis
    context_with = f"Hypothesis: {hypothesis}\nSituation: {situation}"
    generated_with, similarity_with = measure_completion_fit(context_with, outcome)
    
    # Test WITHOUT hypothesis
    context_without = f"Situation: {situation}"
    generated_without, similarity_without = measure_completion_fit(context_without, outcome)
    
    improvement = similarity_with - similarity_without
    
    return {
        "with_hypothesis": {
            "generated": generated_with,
            "similarity": similarity_with
        },
        "without_hypothesis": {
            "generated": generated_without,
            "similarity": similarity_without
        },
        "improvement": improvement,
        "helps": improvement > 10
    }

# Test
if __name__ == "__main__":
    print("HYPOTHESIS EVALUATION VIA COMPLETION\n")
    
    cases = [
        ("Gravity causes constant downward acceleration",
         "A stone is dropped from a 20m cliff", 
         "The stone falls faster and faster, hitting the ground after 2 seconds"),
         
        ("Cold temperatures make water expand",
         "A bottle of water is placed in the freezer",
         "The water freezes and the bottle cracks from ice expansion")
    ]
    
    for hypothesis, situation, outcome in cases:
        print(f"\nHypothesis: {hypothesis}")
        print(f"Situation: {situation}")
        print(f"Actual outcome: {outcome}")
        
        result = evaluate_hypothesis(hypothesis, situation, outcome)
        
        print(f"\nWith hypothesis generated: {result['with_hypothesis']['generated']}")
        print(f"Similarity to actual: {result['with_hypothesis']['similarity']}%")
        
        print(f"\nWithout hypothesis generated: {result['without_hypothesis']['generated']}")  
        print(f"Similarity to actual: {result['without_hypothesis']['similarity']}%")
        
        print(f"\nHypothesis improves prediction by: {result['improvement']} points")
        print(f"Hypothesis helps: {'YES' if result['helps'] else 'NO'}")
        print("-"*80)