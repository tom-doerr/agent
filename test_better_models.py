#!/usr/bin/env python3
"""Test models that work better with structured output"""

import dspy

# Option 1: Use a model better at JSON
models_to_try = [
    # Better for structured output
    "ollama_chat/llama3.2:3b",  # Good at following instructions
    "ollama_chat/mistral:7b",   # Reliable for JSON
    "ollama_chat/qwen2.5:7b",   # Good instruction following
    
    # Your current model
    "ollama_chat/deepseek-r1:8b"
]

for model_name in models_to_try:
    print(f"\nTesting {model_name}:")
    try:
        lm = dspy.LM(model_name, api_base='http://localhost:11434', api_key='', temperature=0)
        dspy.configure(lm=lm)
        
        # Simple JSON test
        predictor = dspy.Predict("question -> answer: str")
        result = predictor(question="What is 2+2?")
        print(f"  ✓ Success: {result.answer}")
    except Exception as e:
        print(f"  ✗ Failed: {str(e)[:100]}...")