#!/usr/bin/env python3
"""Fix for Ollama structured output with DSPy"""

import dspy
from typing import List
from pydantic import BaseModel, Field
import json

class Edit(BaseModel):
    search: str = Field(description="Text to find")
    replace: str = Field(description="Text to replace with")

# Custom signature that forces JSON
class RefineWithJSON(dspy.Signature):
    """Generate edits as valid JSON"""
    
    artifact: str = dspy.InputField()
    critique: str = dspy.InputField()
    
    # Force JSON output with instructions
    edits_json: str = dspy.OutputField(
        desc="A JSON array of edit objects. Each edit must have 'search' and 'replace' fields. Example: [{\"search\": \"old text\", \"replace\": \"new text\"}]"
    )

# Configure
lm = dspy.LM(
    'ollama_chat/deepseek-r1:8b',
    api_base='http://localhost:11434',
    api_key='',
    temperature=0,
    max_tokens=1000
)
dspy.configure(lm=lm)

# Create refiner that outputs JSON string
json_refiner = dspy.Predict(RefineWithJSON)

def get_edits(artifact: str, critique: str) -> List[Edit]:
    """Get edits with JSON enforcement"""
    
    # Add explicit JSON instruction
    result = json_refiner(
        artifact=artifact,
        critique=critique + "\n\nIMPORTANT: Output ONLY a valid JSON array, no other text."
    )
    
    try:
        # Parse JSON string to Edit objects
        edits_data = json.loads(result.edits_json)
        return [Edit(**edit) for edit in edits_data]
    except:
        # Fallback
        return []

# Test it
if __name__ == "__main__":
    artifact = "Hello wrold. This is a test."
    critique = "Fix the spelling of 'world'"
    
    edits = get_edits(artifact, critique)
    print(f"Got {len(edits)} edits:")
    for edit in edits:
        print(f"  - Replace '{edit.search}' with '{edit.replace}'")