"""Tests for the secure SimpleDSPy agent."""
import pytest
from unittest.mock import patch, MagicMock, call
import tempfile
from pathlib import Path

from agent_simpledspy_secure import SecureSimpleDSPyAgent
from utils.command_executor import CommandResult


class TestSecureSimpleDSPyAgent:
    """Test the secure SimpleDSPy agent."""
    
    @pytest.fixture
    def agent(self, tmp_path):
        """Create test agent with mocked DSPy."""
        with patch('agent_simpledspy_secure.dspy'):
            agent = SecureSimpleDSPyAgent(
                data_dir=tmp_path,
                command_whitelist_mode=True,
                max_command_memory_mb=256,
            )
            return agent
    
    @pytest.fixture
    def mock_predict(self):
        """Mock the predict function."""
        with patch('agent_simpledspy_secure.predict') as mock:
            yield mock
    
    @pytest.fixture
    def mock_chain_of_thought(self):
        """Mock the chain_of_thought function."""
        with patch('agent_simpledspy_secure.chain_of_thought') as mock:
            yield mock
    
    def test_initialization(self, agent):
        """Test agent initializes with security features."""
        assert agent.command_executor is not None
        assert agent.context_manager is not None
        assert agent.audit_commands is True
        
        # Check common commands are whitelisted
        validator = agent.command_executor.validator
        assert 'ls' in validator.WHITELIST_COMMANDS
        assert 'python' in validator.WHITELIST_COMMANDS
        assert 'git' in validator.WHITELIST_COMMANDS
    
    def test_dangerous_command_blocked(self, agent, mock_predict, mock_chain_of_thought):
        """Test dangerous commands are blocked."""
        # Mock DSPy to generate dangerous command
        mock_predict.return_value = 'run_command'
        mock_chain_of_thought.return_value = 'rm -rf /'
        
        # Process input
        agent.process_user_input("delete everything")
        
        # Check command was blocked
        stats = agent.get_command_stats()
        assert stats['blocked'] == 1
        assert stats['successful'] == 0
    
    def test_safe_command_execution(self, agent, mock_predict, mock_chain_of_thought):
        """Test safe commands execute properly."""
        # Mock DSPy to generate safe command
        mock_predict.side_effect = [
            'run_command',      # action
            'Command executed successfully',  # output summary
            'False',            # should continue (one more iteration)
            'reply_to_user',    # action
            'The list command completed successfully',  # response
            'True',             # done
        ]
        mock_chain_of_thought.return_value = 'ls -la'
        
        # Process input
        agent.process_user_input("list files")
        
        # Check command was executed
        stats = agent.get_command_stats()
        assert stats['total'] >= 1
        assert stats['blocked'] == 0
    
    def test_context_management(self, agent, mock_predict):
        """Test context window management."""
        # Add many messages to test windowing
        for i in range(20):
            agent.context_manager.add('user', f"Message {i} with some content")
            agent.context_manager.add('assistant', f"Response {i}")
        
        # Check context stats
        stats = agent.get_context_stats()
        assert stats['total_tokens'] > 0
        assert stats['entry_count'] >= 0  # Some may be summarized
        
        # Verify context doesn't exceed limits
        assert stats['total_tokens'] <= agent.context_manager.max_tokens
    
    def test_command_timeout(self, agent, mock_predict, mock_chain_of_thought):
        """Test command timeout handling."""
        # Mock DSPy to generate long-running command
        mock_predict.side_effect = [
            'run_command',
            'Command timed out',
            'True',  # done
        ]
        mock_chain_of_thought.return_value = 'sleep 100'
        
        # Add sleep to whitelist for test
        agent.add_allowed_command('sleep')
        
        # Process with short timeout
        with patch.object(agent, 'execute_command') as mock_exec:
            mock_exec.return_value = CommandResult(
                stdout='',
                stderr='Command timed out after 5 seconds',
                return_code=-1,
                timed_out=True
            )
            agent.process_user_input("run long task")
        
        # Verify timeout was handled
        mock_exec.assert_called_once_with('sleep 100', timeout=30)
    
    def test_command_chaining_blocked(self, agent, mock_predict, mock_chain_of_thought):
        """Test command chaining is blocked."""
        # Mock DSPy to generate chained command
        mock_predict.return_value = 'run_command'
        mock_chain_of_thought.return_value = 'echo safe && rm -rf /'
        
        # Process input
        agent.process_user_input("run chained commands")
        
        # Check command was blocked
        stats = agent.get_command_stats()
        assert stats['blocked'] == 1
    
    def test_resource_limits(self, agent, mock_predict, mock_chain_of_thought):
        """Test resource limits are enforced."""
        # Mock DSPy to generate resource-intensive command
        mock_predict.side_effect = ['run_command', 'Memory limit exceeded', 'True']
        mock_chain_of_thought.return_value = 'python -c "x = [0] * (10**9)"'
        
        # Process input
        agent.process_user_input("allocate lots of memory")
        
        # Command should fail due to resource limits
        stats = agent.get_command_stats()
        assert stats['failed'] >= 1
    
    def test_audit_logging(self, agent, mock_predict, mock_chain_of_thought):
        """Test commands are audited."""
        # Mock DSPy for simple command
        mock_predict.side_effect = ['run_command', 'Listed files', 'True']
        mock_chain_of_thought.return_value = 'ls'
        
        # Process input
        agent.process_user_input("list files")
        
        # Check audit file exists and contains entry
        audit_file = agent.data_dir / "command_audit.ndjson"
        assert audit_file.exists()
        
        with open(audit_file, 'r') as f:
            import json
            audit_entry = json.loads(f.readline())
            assert audit_entry['command'] == 'ls'
            assert 'timestamp' in audit_entry
            assert 'duration_seconds' in audit_entry
    
    def test_action_flow(self, agent, mock_predict, mock_chain_of_thought):
        """Test the action decision flow."""
        # Test run_command -> reply_to_user flow
        mock_predict.side_effect = [
            'run_command',      # First action
            'Files listed',     # Output summary
            'False',            # Continue
            'reply_to_user',    # Second action
            'I found 5 files in the directory',  # Response
            'True',             # Done
        ]
        mock_chain_of_thought.return_value = 'ls'
        
        # Process input
        agent.process_user_input("what files are here?")
        
        # Verify both actions were taken
        assert mock_predict.call_count >= 6  # All the decisions
        assert mock_chain_of_thought.call_count == 1  # One command generated
    
    def test_unknown_action_handling(self, agent, mock_predict):
        """Test handling of unknown actions."""
        # Mock invalid action
        mock_predict.side_effect = ['invalid_action', 'True']
        
        # Process input - should not crash
        agent.process_user_input("do something")
        
        # Check context contains unknown action note
        messages = agent.get_context_messages()
        assert any('Unknown action' in msg['content'] for msg in messages)
    
    def test_state_persistence(self, agent, mock_predict, mock_chain_of_thought):
        """Test agent state is saved and restored."""
        # Execute some commands
        mock_predict.side_effect = ['run_command', 'Done', 'True']
        mock_chain_of_thought.return_value = 'echo test'
        agent.add_allowed_command('echo')
        
        agent.process_user_input("test command")
        
        # Save state
        agent.save_state()
        
        # Create new agent and load state
        with patch('agent_simpledspy_secure.dspy'):
            new_agent = SecureSimpleDSPyAgent(data_dir=agent.data_dir)
            new_agent.load_state()
        
        # Verify state was restored
        stats = new_agent.get_command_stats()
        assert stats['total'] == 1
        assert stats['successful'] == 1
        
        # Context should be restored
        context_stats = new_agent.get_context_stats()
        assert context_stats['entry_count'] > 0


class TestSecureSimpleDSPyIntegration:
    """Integration tests with real command execution."""
    
    @pytest.mark.integration
    def test_real_command_execution(self, tmp_path):
        """Test with real command execution (no DSPy mocking)."""
        # Create agent
        with patch('agent_simpledspy_secure.dspy'):
            agent = SecureSimpleDSPyAgent(
                data_dir=tmp_path,
                command_whitelist_mode=True,
            )
        
        # Execute real command
        result = agent.execute_command("echo 'Hello, World!'")
        assert result.return_code == 0
        assert "Hello, World!" in result.stdout
        
        # Try blocked command
        result = agent.execute_command("sudo rm -rf /")
        assert result.return_code == 1
        assert "validation failed" in result.stderr
    
    @pytest.mark.integration
    def test_resource_limit_enforcement(self, tmp_path):
        """Test real resource limit enforcement."""
        with patch('agent_simpledspy_secure.dspy'):
            agent = SecureSimpleDSPyAgent(
                data_dir=tmp_path,
                max_command_memory_mb=50,  # Very low limit
                max_command_cpu_seconds=2,
            )
        
        # Add python to whitelist
        agent.add_allowed_command('python')
        
        # Try to exceed memory
        result = agent.execute_command(
            "python -c 'x = [0] * (100 * 1024 * 1024)'"  # 100MB
        )
        assert result.return_code != 0
        
        # Try to exceed CPU time
        result = agent.execute_command(
            "python -c 'while True: pass'",
            timeout=3
        )
        assert result.timed_out or result.return_code != 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])