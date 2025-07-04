#!/usr/bin/env python3
"""Working DSPy version with JSON string output"""

import datetime
import time
from pathlib import Path
from pydantic import BaseModel, Field
import dspy
import json
from context_provider import create_context_string

print(f"DSPy version: {dspy.__version__}")

# Configure with explicit JSON mode
lm = dspy.LM(
    'ollama_chat/deepseek-r1:8b',
    api_base='http://localhost:11434',
    api_key='',
    temperature=0,
    max_tokens=2000,
    # Force JSON mode
    response_format={"type": "json_object"}
)
dspy.configure(lm=lm)

class Edit(BaseModel):
    search: str = Field(..., description="Search term to find in the artifact.")
    replace: str = Field(..., description="Replacement text for the search term.")

# Use string output with JSON instructions
class RefineToJSON(dspy.Signature):
    """Generate edits as JSON string"""
    artifact: str = dspy.InputField()
    constraints: str = dspy.InputField()
    critique: str = dspy.InputField()
    context: str = dspy.InputField()
    search_replace_errors: str = dspy.InputField(desc="Previous failed edits as JSON array")
    
    edits_json: str = dspy.OutputField(
        desc="A JSON array of edit objects with 'search' and 'replace' fields. Example: [{\"search\": \"old\", \"replace\": \"new\"}]"
    )

# Create refiner with explicit JSON instructions
refiner = dspy.ChainOfThought(
    RefineToJSON,
    instructions="""Generate search/replace edits to address the critique.
Output MUST be a valid JSON array. Each edit must have:
- "search": exact text to find (must exist in artifact)
- "replace": new text
Example: [{"search": "hello", "replace": "hi"}]"""
)

critic = dspy.Predict(
    'artifact, constraints, context -> critique',
    instructions="Critique the artifact based on the constraints."
)

CONSTRAINTS_FILE = Path('constraints.md')
ARTIFACT_FILE = Path('artifact.md')

def apply_edits(artifact: str, edits: list[Edit]) -> tuple[str, list[Edit]]:
    """Apply edits and track failures"""
    search_replace_errors = []
    for edit in edits:
        if edit.search not in artifact:
            search_replace_errors.append(edit)
            print(f"Error: '{edit.search}' not found")
            continue
        artifact = artifact.replace(edit.search, edit.replace)
    return artifact, search_replace_errors

def iteration_loop():
    history = []
    search_replace_errors = []
    
    for i in range(10):
        print(f"\nIteration {i + 1} {'=' * 50}")
        
        artifact = ARTIFACT_FILE.read_text()
        constraints = CONSTRAINTS_FILE.read_text().strip()
        context = create_context_string()
        
        # Get critique
        critique = critic(
            artifact=artifact,
            constraints=constraints,
            context=context
        ).critique
        print(f"Critique: {critique[:200]}...")
        
        # Get edits as JSON string
        errors_json = json.dumps([{"search": e.search, "replace": e.replace} 
                                 for e in search_replace_errors])
        
        result = refiner(
            artifact=artifact,
            constraints=constraints,
            critique=critique,
            context=context,
            search_replace_errors=errors_json
        )
        
        # Parse JSON string to Edit objects
        try:
            edits_data = json.loads(result.edits_json)
            edits = [Edit(**edit) for edit in edits_data]
            print(f"Generated {len(edits)} edits")
        except Exception as e:
            print(f"JSON parse error: {e}")
            edits = []
        
        # Apply edits
        refined, new_errors = apply_edits(artifact, edits)
        search_replace_errors.extend(new_errors)
        
        if artifact == refined:
            print("No changes made - stopping")
            break
            
        ARTIFACT_FILE.write_text(refined)
        print("Artifact updated!")

def main():
    last_mtime = None
    while True:
        mtime = CONSTRAINTS_FILE.stat().st_mtime
        if mtime != last_mtime:
            print(f"Constraints changed. Running iterations...")
            last_mtime = mtime
            iteration_loop()
        time.sleep(1)

if __name__ == "__main__":
    main()