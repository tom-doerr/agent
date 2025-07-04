#!/usr/bin/env python3
"""Custom Ollama LM that properly handles structured output"""

import dspy
from dspy.clients import LM
import litellm
import json
from typing import Any, Dict, List

class OllamaStructuredLM(LM):
    """Ollama LM that converts response_format to format parameter"""
    
    def __init__(self, model: str, **kwargs):
        # Remove ollama_chat prefix if present
        if model.startswith('ollama_chat/'):
            model = model[12:]
        
        super().__init__(
            model=f"ollama_chat/{model}",
            **kwargs
        )
    
    def __call__(self, messages: List[Dict], **kwargs) -> Any:
        # Convert OpenAI-style to Ollama-style
        if 'response_format' in kwargs and kwargs['response_format'].get('type') == 'json_object':
            kwargs['format'] = 'json'
            del kwargs['response_format']
        
        # If there's a JSON schema in response_format
        if 'response_format' in kwargs and 'schema' in kwargs['response_format']:
            kwargs['format'] = kwargs['response_format']['schema']
            del kwargs['response_format']
        
        # Call parent
        return super().__call__(messages, **kwargs)

# Usage example
if __name__ == "__main__":
    # Use our custom LM
    lm = OllamaStructuredLM(
        'deepseek-r1:8b',
        api_base='http://localhost:11434',
        api_key='',
        temperature=0
    )
    dspy.configure(lm=lm)
    
    # Now DSPy structured output should work
    from pydantic import BaseModel
    
    class Output(BaseModel):
        text: str
        score: int
    
    predictor = dspy.Predict("input -> output: Output")
    result = predictor(input="Test")
    print(result)