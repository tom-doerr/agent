#!/usr/bin/env python3
"""Quick test of Ollama model"""

import requests
import json

print("Testing Ollama DeepSeek-R1 model...\n")

# Test 1: Simple text generation
print("Test 1: Simple text")
response = requests.post('http://localhost:11434/api/generate', json={
    "model": "deepseek-r1:8b",
    "prompt": "Say hello",
    "stream": False,
    "options": {"temperature": 0, "num_predict": 20}
})
print("Response:", response.json().get('response', 'No response')[:100])

# Test 2: JSON generation
print("\n\nTest 2: JSON format")
response = requests.post('http://localhost:11434/api/generate', json={
    "model": "deepseek-r1:8b", 
    "prompt": "List 3 colors as JSON array",
    "format": "json",
    "stream": False,
    "options": {"temperature": 0, "num_predict": 50}
})
print("Response:", response.json().get('response', 'No response'))

# Check if model is loaded
print("\n\nChecking loaded models:")
response = requests.get('http://localhost:11434/api/tags')
models = response.json().get('models', [])
for model in models:
    if 'deepseek' in model['name']:
        print(f"✓ {model['name']} - {model['size']/1e9:.1f}GB")