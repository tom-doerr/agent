#!/usr/bin/env python3

import pytest
pytestmark = pytest.mark.timeout(10, method='thread')
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from interactive_chat import InteractiveChat
from unittest.mock import patch, MagicMock
from textual.widgets import Input, Button, Static
from textual.containers import Container
import asyncio

# Test app initialization
def test_app_initialization():
    app = InteractiveChat()
    assert app.model_name == "dv3"
    assert app.llm is not None

# Test single message flow
@patch('interactive_chat.predict')
@pytest.mark.asyncio
async def test_single_message_flow(mock_predict):
    app = InteractiveChat()
    mock_predict.return_value = "Test response"
    
    async with app.run_test() as pilot:
        # Simulate user input
        input_field = app.query_one("#input-field", Input)
        input_field.value = "Hello"
        # Press Enter to submit
        await pilot.press("#input-field", "enter")
        
        # Check input was cleared
        assert input_field.value == ""
        
        # Wait for async tasks
        await pilot.pause(0.1)
        
        # Check response was added
        output = app.query_one("#output-container", Static)
        assert "Hello" in output.renderable
        assert "Test response" in output.renderable

# Test multiple messages without waiting
@patch('interactive_chat.predict')
@pytest.mark.asyncio
async def test_multiple_messages(mock_predict):
    app = InteractiveChat()
    responses = ["Response 1", "Response 2"]
    mock_predict.side_effect = responses
    
    async with app.run_test() as pilot:
        # Send first message
        input_field = app.query_one("#input-field", Input)
        input_field.value = "Message 1"
        await pilot.press("#input-field", "enter")
        
        # Immediately send second message
        input_field.value = "Message 2"
        await pilot.press("#input-field", "enter")
        
        # Wait for async tasks
        await pilot.pause(0.1)
        
        # Check both responses present
        output = app.query_one("#output-container", Static)
        rendered = output.renderable
        for msg in ["Message 1", "Message 2"] + responses:
            assert msg in rendered

# Test error handling
@patch('interactive_chat.predict')
@pytest.mark.asyncio
async def test_error_handling(mock_predict):
    app = InteractiveChat()
    mock_predict.side_effect = Exception("Test error")
    
    async with app.run_test() as pilot:
        input_field = app.query_one("#input-field", Input)
        input_field.value = "Error test"
        await pilot.press("#input-field", "enter")
        
        await pilot.pause(0.1)
        
        output = app.query_one("#output-container", Static)
        assert "Error processing request" in output.renderable
