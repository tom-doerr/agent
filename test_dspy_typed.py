#!/usr/bin/env python3
"""Test DSPy with TypedPredictor for structured output"""

import dspy
from pydantic import BaseModel, Field
from typing import List

# Configure
lm = dspy.LM(
    'ollama_chat/deepseek-r1:8b',
    api_base='http://localhost:11434',
    api_key='',
    temperature=0
)
dspy.configure(lm=lm)

class Edit(BaseModel):
    search: str = Field(description="Text to find")
    replace: str = Field(description="Replacement text")

class EditsOutput(BaseModel):
    edits: List[Edit] = Field(description="List of search/replace edits")

# Try TypedPredictor
from dspy import TypedPredictor

class RefineSignature(dspy.Signature):
    """Generate edits to improve the artifact"""
    artifact: str = dspy.InputField()
    critique: str = dspy.InputField()
    output: EditsOutput = dspy.OutputField()

# Create typed predictor
refiner = TypedPredictor(RefineSignature)

# Test it
artifact = "Hello wrold. This is a test."
critique = "Fix the spelling mistake"

try:
    result = refiner(artifact=artifact, critique=critique)
    print("Success! Got edits:", result.output.edits)
except Exception as e:
    print("Failed:", str(e)[:200])