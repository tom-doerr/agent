#!/usr/bin/env python3
"""Test Ollama's format enforcement"""

import requests
import json

# Test 1: Direct Ollama API with format
print("Testing Ollama format enforcement...")

# Define a JSON schema
schema = {
    "type": "object",
    "properties": {
        "critique": {"type": "string"},
        "score": {"type": "number"}
    },
    "required": ["critique", "score"]
}

# Call Ollama directly with format
response = requests.post('http://localhost:11434/api/generate', json={
    "model": "deepseek-r1:8b",
    "prompt": "Critique this text: 'Hello world'. Provide a critique and score.",
    "format": schema,  # This enforces the structure!
    "stream": False,
    "options": {"temperature": 0}
})

result = response.json()
print("Raw response:", result.get('response', 'No response'))

# Parse the JSON
try:
    parsed = json.loads(result['response'])
    print("✅ Valid JSON:", parsed)
except:
    print("❌ Invalid JSON")

print("\n" + "="*50 + "\n")

# Test 2: Check if DSPy is passing format correctly
import dspy

lm = dspy.LM(
    'ollama_chat/deepseek-r1:8b',
    api_base='http://localhost:11434',
    api_key='',
    temperature=0
)
dspy.configure(lm=lm)

# Enable debug logging to see what's sent
import logging
logging.basicConfig(level=logging.DEBUG)

# Try with DSPy
print("Testing DSPy with structured output...")
predictor = dspy.Predict("text -> critique: str, score: int")
try:
    result = predictor(text="Hello world")
    print("DSPy result:", result)
except Exception as e:
    print("DSPy failed:", e)