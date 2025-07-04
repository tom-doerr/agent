#!/usr/bin/env python3
"""Simplified nlco_iter without DSPy complexity"""

import datetime
import time
from pathlib import Path
import json
import requests
from context_provider import create_context_string

CONSTRAINTS_FILE = Path('constraints.md')
ARTIFACT_FILE = Path('artifact.md')

def get_critique(artifact: str, constraints: str, context: str) -> str:
    """Get critique using direct Ollama API"""
    prompt = f"""Given this artifact:
{artifact}

Constraints:
{constraints}

Context: {context}

Provide a critique of the artifact based on the constraints. Be specific about what needs to be improved."""

    response = requests.post('http://localhost:11434/api/generate', json={
        "model": "deepseek-r1:8b",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0}
    })
    
    return response.json().get('response', 'No critique generated')

def get_edits(artifact: str, critique: str) -> list:
    """Get edits using Ollama with JSON format"""
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "search": {"type": "string"},
                "replace": {"type": "string"}
            },
            "required": ["search", "replace"]
        }
    }
    
    prompt = f"""Given this artifact:
{artifact}

And this critique:
{critique}

Generate a JSON array of search/replace edits. Each edit must have:
- "search": exact text from the artifact to find
- "replace": new text to replace it with

Output ONLY the JSON array, nothing else."""

    response = requests.post('http://localhost:11434/api/generate', json={
        "model": "deepseek-r1:8b",
        "prompt": prompt,
        "format": schema,
        "stream": False,
        "options": {"temperature": 0}
    })
    
    try:
        return json.loads(response.json()['response'])
    except:
        return []

def apply_edits(artifact: str, edits: list) -> tuple[str, list]:
    """Apply edits to artifact"""
    errors = []
    for edit in edits:
        search = edit.get('search', '')
        replace = edit.get('replace', '')
        
        if search in artifact:
            artifact = artifact.replace(search, replace)
            print(f"✓ Applied: '{search[:30]}...' → '{replace[:30]}...'")
        else:
            errors.append(edit)
            print(f"✗ Not found: '{search[:50]}...'")
    
    return artifact, errors

def iteration_loop():
    for i in range(10):
        print(f"\n{'='*60}")
        print(f"Iteration {i + 1}")
        print('='*60)
        
        # Read files
        artifact = ARTIFACT_FILE.read_text()
        constraints = CONSTRAINTS_FILE.read_text().strip()
        context = create_context_string()
        
        print(f"\nContext: {context}")
        
        # Get critique
        print("\nGenerating critique...")
        critique = get_critique(artifact, constraints, context)
        print(f"Critique: {critique[:200]}...")
        
        # Get edits
        print("\nGenerating edits...")
        edits = get_edits(artifact, critique)
        print(f"Got {len(edits)} edits")
        
        if not edits:
            print("No edits generated - stopping")
            break
        
        # Apply edits
        print("\nApplying edits:")
        new_artifact, errors = apply_edits(artifact, edits)
        
        if artifact == new_artifact:
            print("\nNo changes made - stopping")
            break
        
        # Save
        ARTIFACT_FILE.write_text(new_artifact)
        print(f"\n✓ Artifact updated ({len(new_artifact)} chars)")
        
        # Show a preview
        if len(new_artifact) < 500:
            print(f"\nNew artifact:\n{new_artifact}")
        else:
            print(f"\nNew artifact preview:\n{new_artifact[:200]}...")

def main():
    print("NLCO Iterator - Simple Version")
    print("Watching for constraint changes...")
    
    last_mtime = None
    while True:
        try:
            mtime = CONSTRAINTS_FILE.stat().st_mtime
            if mtime != last_mtime:
                print(f"\n🔄 Constraints changed at {datetime.datetime.fromtimestamp(mtime)}")
                last_mtime = mtime
                iteration_loop()
        except KeyboardInterrupt:
            print("\nStopped")
            break
        except Exception as e:
            print(f"\nError: {e}")
        
        time.sleep(1)

if __name__ == "__main__":
    main()