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
