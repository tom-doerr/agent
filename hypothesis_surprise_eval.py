#!/usr/bin/env python3
"""Evaluate hypotheses by measuring outcome surprise level."""

import os
import litellm
from dotenv import load_dotenv

load_dotenv()

def surprise_level(context, outcome):
    """Rate how surprising an outcome is (inverse of predictability)."""
    prompt = f"""{context}

Then this happened:
{outcome}

How surprising is this outcome?
1 = Completely expected
5 = Very surprising

Answer with just a number 1-5:"""
    
    response = litellm.completion(
        model="openrouter/google/gemini-2.5-flash-preview",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        api_key=os.getenv("OPENROUTER_API_KEY"),
        api_base="https://openrouter.ai/api/v1"
    )
    
    try:
        return int(response.choices[0].message.content.strip())
    except:
        return 3

def test(hypothesis, situation, outcome):
    """Lower surprise with hypothesis = hypothesis helps."""
    surp_with = surprise_level(f"Hypothesis: {hypothesis}\nSituation: {situation}", outcome)
    surp_without = surprise_level(f"Situation: {situation}", outcome)
    
    reduction = surp_without - surp_with
    
    print(f"\n{hypothesis[:50]}...")
    print(f"Surprise: {surp_with} (with) vs {surp_without} (without)")
    print(f"Hypothesis {'HELPS' if reduction > 0 else 'NO HELP'} (reduces surprise by {reduction})")
    
    return reduction

# Test
if __name__ == "__main__":
    print("HYPOTHESIS EVALUATION VIA SURPRISE LEVELS\n")
    
    improvements = [
        test("Heat flows from hot to cold", 
             "Hot soup left on counter",
             "Soup is room temperature after an hour"),
             
        test("Magnets only attract magnetic materials",
             "Strong magnet placed near aluminum can", 
             "The can doesn't move at all"),
             
        test("Plants grow toward light",
             "Plant placed by window",
             "Plant bends toward the window over days")
    ]
    
    print(f"\nTotal surprise reduction: {sum(improvements)}")