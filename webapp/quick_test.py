import requests
import time

print("Testing backend...")
try:
    # Test root
    r = requests.get("http://localhost:8000/", timeout=5)
    print(f"Root: {r.status_code} - {r.json()}")
    
    # Test streaming with timeout
    print("\nTesting streaming...")
    r = requests.get("http://localhost:8000/stream/test", stream=True, timeout=5)
    print(f"Stream status: {r.status_code}")
    
    # Read first chunk
    for line in r.iter_lines():
        if line:
            print(f"First line: {line[:100]}")
            break
    r.close()
    
except Exception as e:
    print(f"Error: {e}")

print("\nBackend test complete!")