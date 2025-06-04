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
        with patch("coding_agent_repl.dspy.settings.configure") as mock_configure:
            app = CodingAgentREPL()
            app.agent = MagicMock()
            app.LOG_FILE = "/dev/null"  # Disable logging for tests
            return app

    def test_configure_dspy(self):
        with patch("dspy.LM") as mock_lm:
            configure_dspy()
            mock_lm.assert_called_with(model="openrouter/deepseek/deepseek-chat-v3-0324")

    def test_execute_commands(self, app):
        # Test command execution
        commands = "echo hello"
        app.execute_commands(commands)
        assert "hello" in app.current_state
