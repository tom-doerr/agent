#!/usr/bin/env python3
"""Test structured output with proper settings"""

import dspy
from pydantic import BaseModel, Field

# Configure with JSON-friendly settings
lm = dspy.LM(
    'ollama_chat/deepseek-r1:8b',
    api_base='http://localhost:11434',
    api_key='',
    temperature=0,  # Deterministic for JSON
    max_tokens=500  # Limit to avoid rambling
)
dspy.configure(lm=lm)

# Simple test
class SimpleOutput(BaseModel):
    text: str = Field(description="A simple text response")
    score: int = Field(description="A score from 1-10")

class TestSig(dspy.Signature):
    """Test structured output"""
    input: str = dspy.InputField()
    output: SimpleOutput = dspy.OutputField()

# Test it
predictor = dspy.Predict(TestSig)

try:
    result = predictor(input="Hello world")
    print(f"Success! Output: {result.output}")
except Exception as e:
    print(f"Failed: {e}")
    
# Even simpler test
simple = dspy.Predict("input -> answer: str")
try:
    result2 = simple(input="What is 2+2?")
    print(f"Simple worked: {result2.answer}")
except Exception as e:
    print(f"Simple failed: {e}")