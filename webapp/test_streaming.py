#!/usr/bin/env python3
import requests
import json

# Test root endpoint
print("Testing root endpoint...")
response = requests.get('http://localhost:8000/')
print(f"Root response: {response.json()}")

# Test streaming endpoint
print("\nTesting streaming endpoint...")
url = 'http://localhost:8000/stream/What is Python?'
response = requests.get(url, stream=True)
print(f"Status code: {response.status_code}")
print(f"Headers: {dict(response.headers)}")

print("\nStreaming response:")
for line in response.iter_lines():
    if line:
        # SSE format: "data: {json}"
        if line.startswith(b'data: '):
            data = json.loads(line[6:])
            if 'chunk' in data:
                print(f"Chunk: '{data['chunk']}'", end='', flush=True)
            elif 'done' in data:
                print("\n\nStreaming complete!")
                break
            elif 'error' in data:
                print(f"\nError: {data['error']}")
                break