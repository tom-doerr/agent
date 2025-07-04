#!/usr/bin/env python3
"""Fix DSPy to work with Ollama structured output"""

import dspy
from dspy.adapters import ChatAdapter
from typing import Any, Dict
import json
import logging

# Enable debug logging to see what's happening
logging.basicConfig(level=logging.DEBUG)

class OllamaStructuredAdapter(ChatAdapter):
    """Custom adapter that properly passes format to Ollama"""
    
    def __call__(self, lm, lm_kwargs, signature, demos, inputs):
        # Check if we need structured output
        output_fields = signature.output_fields
        
        if output_fields and any(hasattr(field.annotation, '__origin__') for field in output_fields.values()):
            # Build JSON schema from signature
            schema = self._build_schema(signature)
            
            # Add format parameter for Ollama
            if 'ollama' in lm.model.lower():
                lm_kwargs['format'] = schema
                # Remove response_format if present (OpenAI style)
                lm_kwargs.pop('response_format', None)
        
        # Call parent adapter
        return super().__call__(lm, lm_kwargs, signature, demos, inputs)
    
    def _build_schema(self, signature):
        """Build JSON schema from DSPy signature"""
        properties = {}
        required = []
        
        for name, field in signature.output_fields.items():
            if hasattr(field.annotation, '__origin__'):  # List, Dict, etc
                if field.annotation.__origin__ == list:
                    # Handle list[Edit] case
                    item_type = field.annotation.__args__[0]
                    if hasattr(item_type, '__pydantic_model__'):
                        # It's a Pydantic model
                        properties[name] = {
                            "type": "array",
                            "items": item_type.model_json_schema()
                        }
                    else:
                        properties[name] = {"type": "array"}
            else:
                # Simple types
                properties[name] = {"type": "string"}
            
            required.append(name)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required
        }

# Monkey patch DSPy to use our adapter
original_get_adapter = dspy.adapters.get_adapter

def patched_get_adapter(lm):
    if 'ollama' in lm.model.lower():
        return OllamaStructuredAdapter()
    return original_get_adapter(lm)

dspy.adapters.get_adapter = patched_get_adapter