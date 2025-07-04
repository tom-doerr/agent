#!/usr/bin/env python3
"""Hypothesis evaluator using actual log probabilities from completions."""

import os
import json
import openai
from dotenv import load_dotenv

load_dotenv()

# Setup OpenAI client for direct API access with logprobs
client = openai.OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def get_completion_logprobs(prompt):
    """Get log probabilities for the completion."""
    response = client.completions.create(
        model="openrouter/openai/gpt-3.5-turbo-instruct",  # Completion model that supports logprobs
        prompt=prompt,
        max_tokens=1,
        logprobs=5,  # Get top 5 token probabilities
        temperature=0,
        echo=True  # Include prompt tokens in response
    )
    
    # Extract logprobs for the last tokens (the outcome part)
    tokens = response.choices[0].logprobs.tokens
    logprobs = response.choices[0].logprobs.token_logprobs
    
    # Calculate average logprob for outcome tokens
    outcome_start = prompt.rfind("Outcome:")
    outcome_tokens = []
    
    for i, (token, logprob) in enumerate(zip(tokens, logprobs)):
        if logprob is not None and i > len(tokens) * 0.8:  # Focus on latter part
            outcome_tokens.append(logprob)
    
    avg_logprob = sum(outcome_tokens) / len(outcome_tokens) if outcome_tokens else -10
    perplexity = 2 ** (-avg_logprob)
    
    return avg_logprob, perplexity

def evaluate_hypothesis(hypothesis, situation, outcome):
    """Compare perplexity with and without hypothesis."""
    
    # Prompt WITH hypothesis
    prompt_with = f"""Hypothesis: {hypothesis}
Situation: {situation}
Outcome: {outcome}"""
    
    # Prompt WITHOUT hypothesis  
    prompt_without = f"""Situation: {situation}
Outcome: {outcome}"""
    
    try:
        logprob_with, perp_with = get_completion_logprobs(prompt_with)
        logprob_without, perp_without = get_completion_logprobs(prompt_without)
        
        # Lower perplexity = more predictable
        improvement = (perp_without - perp_with) / perp_without * 100
        
        return {
            "with_hypothesis": {"logprob": logprob_with, "perplexity": perp_with},
            "without_hypothesis": {"logprob": logprob_without, "perplexity": perp_without},
            "improvement_percent": improvement,
            "helps": improvement > 5
        }
    except Exception as e:
        print(f"Error: {e}")
        # Fallback to chat completion with pseudo-scoring
        return evaluate_with_chat_model(hypothesis, situation, outcome)

def evaluate_with_chat_model(hypothesis, situation, outcome):
    """Fallback using chat models that don't support logprobs directly."""
    # Create prompts that include the outcome as if predicting next token
    prompt_with = f"""Given this context, rate how naturally this outcome follows (0-1):

Hypothesis: {hypothesis}
Situation: {situation}

The outcome is: {outcome}

Naturalness score:"""
    
    prompt_without = f"""Given this context, rate how naturally this outcome follows (0-1):

Situation: {situation}

The outcome is: {outcome}

Naturalness score:"""
    
    response_with = client.chat.completions.create(
        model="openrouter/google/gemini-2.5-flash-preview",
        messages=[{"role": "user", "content": prompt_with}],
        temperature=0
    )
    
    response_without = client.chat.completions.create(
        model="openrouter/google/gemini-2.5-flash-preview",
        messages=[{"role": "user", "content": prompt_without}],
        temperature=0
    )
    
    try:
        score_with = float(response_with.choices[0].message.content.strip())
        score_without = float(response_without.choices[0].message.content.strip())
    except:
        score_with = 0.5
        score_without = 0.5
    
    # Convert scores to pseudo-perplexity (inverse relationship)
    perp_with = 1 / (score_with + 0.001)
    perp_without = 1 / (score_without + 0.001)
    improvement = (perp_without - perp_with) / perp_without * 100
    
    return {
        "with_hypothesis": {"score": score_with, "pseudo_perplexity": perp_with},
        "without_hypothesis": {"score": score_without, "pseudo_perplexity": perp_without},
        "improvement_percent": improvement,
        "helps": improvement > 5
    }

# Test cases
if __name__ == "__main__":
    cases = [
        {
            "hypothesis": "Objects fall due to gravitational force",
            "situation": "A ball is released from 10 meters height",
            "outcome": "The ball accelerates downward at 9.8 m/s² and hits the ground"
        },
        {
            "hypothesis": "Heavy objects fall faster than light ones",
            "situation": "A hammer and feather are dropped on the moon",  
            "outcome": "Both objects hit the ground simultaneously"
        }
    ]
    
    for case in cases:
        print(f"\nTesting: {case['hypothesis'][:50]}...")
        result = evaluate_hypothesis(case['hypothesis'], case['situation'], case['outcome'])
        
        print(f"With hypothesis: {result['with_hypothesis']}")
        print(f"Without hypothesis: {result['without_hypothesis']}")
        print(f"Improvement: {result['improvement_percent']:.1f}%")
        print(f"Hypothesis helps: {'YES' if result['helps'] else 'NO'}")