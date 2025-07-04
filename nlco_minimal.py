#!/usr/bin/env python3
import requests, json, time, os
from pathlib import Path
import mlflow

# Support both Docker and local environments
mlflow_uri = os.getenv('MLFLOW_TRACKING_URI', 'http://localhost:5002')
ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')

mlflow.set_tracking_uri(mlflow_uri)
mlflow.set_experiment("nlco-iterations")
mlflow.autolog()

def iterate():
    artifact = Path('artifact.md').read_text()
    constraints = Path('constraints.md').read_text()
    
    # Get critique
    r = requests.post(f'{ollama_url}/api/generate', json={
        "model": "deepseek-r1:8b",
        "prompt": f"Critique this based on constraints:\n{artifact}\n\nConstraints:\n{constraints}",
        "stream": False
    })
    critique = r.json()['response']
    print(f"Critique: {critique[:100]}...")
    
    # Get edits as JSON
    r = requests.post(f'{ollama_url}/api/generate', json={
        "model": "deepseek-r1:8b", 
        "prompt": f"Generate JSON array of search/replace edits:\n{artifact}\n\nCritique:\n{critique}",
        "format": {"type": "array", "items": {"type": "object", "properties": {"search": {"type": "string"}, "replace": {"type": "string"}}}},
        "stream": False
    })
    
    # Apply edits
    for edit in json.loads(r.json()['response']):
        if edit['search'] in artifact:
            artifact = artifact.replace(edit['search'], edit['replace'])
            
    Path('artifact.md').write_text(artifact)

# Watch for changes
mtime = 0
while True:
    if Path('constraints.md').stat().st_mtime != mtime:
        mtime = Path('constraints.md').stat().st_mtime
        iterate()
    time.sleep(1)