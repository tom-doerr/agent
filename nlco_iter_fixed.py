#!/usr/bin/env python3
"""Fixed nlco_iter with proper structured output"""

import datetime
import time
from pathlib import Path
from pydantic import BaseModel, Field
import dspy
import json
import requests
from context_provider import create_context_string

print(f"DSPy version: {dspy.__version__}")

# Configure DSPy
lm = dspy.LM(
    'ollama_chat/deepseek-r1:8b',
    api_base='http://localhost:11434',
    api_key='',
    temperature=0,
    max_tokens=2000
)
dspy.configure(lm=lm)

class Edit(BaseModel):
    search: str = Field(..., description="Search term to find in the artifact.")
    replace: str = Field(..., description="Replacement text for the search term.")

# Direct Ollama call for structured output
def get_edits_direct(artifact: str, critique: str, context: str) -> list[Edit]:
    """Call Ollama directly with format enforcement"""
    
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

Context: {context}

Generate a list of search/replace edits to address the critique. 
Each edit must have 'search' (exact text to find) and 'replace' (new text).
Return ONLY a JSON array of edits."""

    response = requests.post('http://localhost:11434/api/generate', json={
        "model": "deepseek-r1:8b",
        "prompt": prompt,
        "format": schema,  # Enforce structure!
        "stream": False,
        "options": {"temperature": 0}
    })
    
    try:
        edits_data = json.loads(response.json()['response'])
        return [Edit(**edit) for edit in edits_data]
    except:
        return []

# Keep the critic using DSPy (works fine for simple text)
critic = dspy.Predict(
    'artifact, constraints, context -> critique',
    instructions="Critique the artifact based on the constraints and common sense."
)

CONSTRAINTS_FILE = Path('constraints.md')
ARTIFACT_FILE = Path('artifact.md')

def apply_edits(artifact: str, edits: list[Edit]) -> tuple[str, list[Edit]]:
    """Apply edits and track failures"""
    error_message = ''
    search_replace_errors = []
    for edit in edits:
        if edit.search not in artifact:
            search_replace_errors.append(edit)
            error_message += f"Search term '{edit.search}' not found in artifact.\n"
            print('error:', error_message)
            continue
        artifact = artifact.replace(edit.search, edit.replace)
    return artifact, search_replace_errors

def iteration_loop():
    history = []
    search_replace_errors = []
    
    for i in range(10):
        print(f"Iteration {i + 1} {'=' * 50}")
        
        artifact = ARTIFACT_FILE.read_text()
        constraints = CONSTRAINTS_FILE.read_text().strip()
        context = create_context_string()
        print(context)
        
        # Get critique (DSPy works fine for this)
        critique_result = critic(
            artifact=artifact,
            constraints=constraints,
            context=context
        )
        critique = critique_result.critique
        print(f"Critique:\n{critique}\n")
        
        # Get edits using direct Ollama call
        edits = get_edits_direct(artifact, critique, context)
        print(f"Got {len(edits)} edits")
        
        # Apply edits
        refined, search_replace_errors = apply_edits(artifact, edits)
        print('-' * 80)
        print(f"Artifact:\n{refined}")
        
        ARTIFACT_FILE.write_text(refined)
        history += [f'Iteration {i + 1}', artifact, constraints, critique, refined]
        
        # Check if no changes were made
        if artifact == refined:
            print("No changes made - stopping")
            break

def main():
    last_mtime = None
    while True:
        mtime = CONSTRAINTS_FILE.stat().st_mtime
        if mtime != last_mtime:
            print(f"Constraints changed at {datetime.datetime.fromtimestamp(mtime)}. Running iterations…")
            last_mtime = mtime
            iteration_loop()
        time.sleep(1)

if __name__ == "__main__":
    main()