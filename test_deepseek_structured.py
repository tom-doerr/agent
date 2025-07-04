#!/usr/bin/env python3
"""Test DeepSeek-R1 structured output with Ollama"""

import json
import requests

# Test 1: Direct Ollama API with format=json
print("Test 1: Ollama with format='json'")
response = requests.post('http://localhost:11434/api/generate', json={
    "model": "deepseek-r1:8b",
    "prompt": "List 3 colors as JSON array. Output only valid JSON.",
    "format": "json",  # This enables JSON grammar!
    "stream": False,
    "options": {"temperature": 0}
})
print("Response:", response.json()['response'])

# Test 2: With JSON schema
print("\nTest 2: Ollama with JSON schema")
schema = {
    "type": "object",
    "properties": {
        "colors": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["colors"]
}

response = requests.post('http://localhost:11434/api/generate', json={
    "model": "deepseek-r1:8b",
    "prompt": "List 3 colors. Return as JSON matching the schema.",
    "format": schema,  # JSON schema constraint
    "stream": False,
    "options": {"temperature": 0}
})
print("Response:", response.json()['response'])

# Test 3: Check your Ollama version
print("\nChecking Ollama capabilities...")
response = requests.get('http://localhost:11434/api/version')
print("Ollama version:", response.json())

# Test 4: DSPy with proper setup
print("\nTest 4: DSPy with DeepSeek-R1")
import dspy

# Configure with explicit JSON instructions
lm = dspy.LM(
    'ollama_chat/deepseek-r1:8b',
    api_base='http://localhost:11434',
    api_key='',
    temperature=0,
    max_tokens=500,
    # Try to force JSON mode
    response_format={"type": "json_object"}  # OpenAI style
)
dspy.configure(lm=lm)

# Simple structured output
predictor = dspy.Predict("task -> result")
try:
    result = predictor(task="List 3 colors as a JSON array")
    print("DSPy result:", result.result)
except Exception as e:
    print("DSPy error:", str(e)[:200])