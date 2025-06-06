import os
import re
import pytest
import dspy
from unittest.mock import patch, MagicMock
from coding_agent_repl import CodingAgentREPL, configure_dspy

class TestCodingAgentREPL:
    @pytest.fixture
    def app(self):
        # Mock DSPy configuration
        with patch("coding_agent_repl.configure_dspy") as mock_configure:
            mock_configure.return_value = MagicMock()
            app = CodingAgentREPL()
            app.agent = MagicMock()
            app.LOG_FILE = "/dev/null"  # Disable logging for tests
            return app

    def test_configure_dspy(self):
        with patch("dspy.LM") as mock_lm:
            configure_dspy()
            mock_lm.assert_called_with(model="openrouter/deepseek/deepseek-chat-v3-0324")

    def test_execute_commands(self, app):
        # Mock UI components
        app.query_one = MagicMock()
        app.update_output = MagicMock()
        
        # Test command execution
        commands = "echo hello"
        app.execute_commands(commands)
        
        # Verify update_output was called
        app.update_output.assert_called()

    def test_agent_forward_signature(self):
        # Create a mock LM that inherits from BaseLM
        class MockBaseLM(dspy.BaseLM):
            def __init__(self):
                super().__init__(model="mock_model")
            def basic_request(self, prompt, **kwargs):
                # Return structured agent output with all expected fields using header format
                # Note: We include the 'reasoning' field because ChainOfThought adds it
                return "Reasoning: test reasoning\nPlan: test plan\nCommands: test commands\nEdits: test edits\nDone: test done"
            def __call__(self, messages, **kwargs):
                # In DSPy, the messages are passed as a list of dicts
                # We need to convert to a prompt string for the mock
                prompt = "\n".join([m["content"] for m in messages])
                return self.basic_request(prompt, **kwargs)
        
        mock_lm = MockBaseLM()
        dspy.settings.configure(lm=mock_lm)
        
        from agent_repl.agent import CodingAgent
        agent = CodingAgent()
        
        # Test that forward accepts required parameters
        agent.forward(request="test", log_context="logs")
        
        # Test that forward rejects extra parameters
        with pytest.raises(TypeError):
            agent.forward(request="test", log_context="logs", extra="invalid")
