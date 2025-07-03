"""Tests for base agent classes."""

import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import sys
sys.path.append(str(Path(__file__).parent.parent))

from base_agent import BaseAgent, CommandAgent, BatchProcessingAgent


class TestableAgent(BaseAgent):
    """Concrete implementation for testing."""
    
    def process(self, input_data):
        return f"Processed: {input_data}"


class TestBaseAgent:
    def test_initialization(self):
        """Test agent initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = TestableAgent("test_agent", data_dir=tmpdir)
            
            assert agent.name == "test_agent"
            assert agent.data_dir == Path(tmpdir)
            assert len(agent.history) == 0
            assert agent.start_time > 0
    
    def test_history_management(self):
        """Test history saving and loading."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = TestableAgent("test_agent", data_dir=tmpdir)
            
            # Save history items
            agent.save_history_item({"action": "test1", "result": "ok"})
            agent.save_history_item({"action": "test2", "result": "ok"})
            
            # Check in-memory history
            assert len(agent.history) == 2
            assert agent.history[0]["action"] == "test1"
            assert "timestamp" in agent.history[0]
            assert agent.history[0]["agent"] == "test_agent"
            
            # Create new agent and load history
            agent2 = TestableAgent("test_agent", data_dir=tmpdir)
            loaded_history = agent2.load_history()
            
            assert len(loaded_history) == 2
            assert loaded_history[0]["action"] == "test1"
    
    def test_status(self):
        """Test agent status reporting."""
        agent = TestableAgent("test_agent")
        time.sleep(0.1)  # Let some time pass
        
        status = agent.get_status()
        
        assert status["name"] == "test_agent"
        assert status["uptime"] > 0.1
        assert status["history_size"] == 0
        assert "data_dir" in status
    
    def test_reset(self):
        """Test agent reset."""
        agent = TestableAgent("test_agent")
        agent.save_history_item({"test": "data"})
        old_start_time = agent.start_time
        
        time.sleep(0.1)
        agent.reset()
        
        assert len(agent.history) == 0
        assert agent.start_time > old_start_time


class TestCommandAgent:
    def test_default_commands(self):
        """Test that default commands are registered."""
        agent = CommandAgent("cmd_agent")
        
        assert "help" in agent.commands
        assert "status" in agent.commands
        assert "history" in agent.commands
    
    def test_help_command(self):
        """Test help command."""
        agent = CommandAgent("cmd_agent")
        result = agent.process("help")
        
        assert "Available commands:" in result
        assert "help:" in result
        assert "status:" in result
    
    def test_status_command(self):
        """Test status command."""
        agent = CommandAgent("cmd_agent")
        result = agent.process("status")
        
        assert "Agent: cmd_agent" in result
        assert "Uptime:" in result
        assert "History items:" in result
    
    def test_history_command(self):
        """Test history command."""
        agent = CommandAgent("cmd_agent")
        agent.process("test1")
        agent.process("test2")
        
        result = agent.process("history")
        
        assert "Recent commands:" in result
        assert "test1" in result
        assert "test2" in result
    
    def test_custom_command(self):
        """Test registering and using custom commands."""
        agent = CommandAgent("cmd_agent")
        
        def echo_command(*args):
            return " ".join(args)
        
        agent.register_command("echo", echo_command, "Echo arguments")
        
        # Test help shows new command
        help_result = agent.process("help")
        assert "echo: Echo arguments" in help_result
        
        # Test command execution
        result = agent.process("echo hello world")
        assert result == "hello world"
    
    def test_unknown_command(self):
        """Test handling of unknown commands."""
        agent = CommandAgent("cmd_agent")
        result = agent.process("unknown_command")
        
        assert "Unknown command: unknown_command" in result
        assert "Type 'help'" in result
    
    def test_command_error_handling(self):
        """Test error handling in commands."""
        agent = CommandAgent("cmd_agent")
        
        def failing_command():
            raise ValueError("Test error")
        
        agent.register_command("fail", failing_command)
        
        result = agent.process("fail")
        assert "Error executing fail" in result
        assert "Test error" in result


class TestBatchProcessingAgent:
    class TestBatchAgent(BatchProcessingAgent):
        """Concrete implementation for testing."""
        
        def process_batch(self, batch):
            return [f"Processed: {item}" for item in batch]
    
    def test_batch_processing(self):
        """Test batch processing logic."""
        agent = self.TestBatchAgent(batch_size=3, name="batch_agent")
        
        # Add items below batch size
        result1 = agent.add_item("item1")
        result2 = agent.add_item("item2")
        
        assert result1 is None
        assert result2 is None
        assert len(agent.current_batch) == 2
        
        # Add item that triggers batch processing
        result3 = agent.add_item("item3")
        
        assert result3 is not None
        assert len(result3) == 3
        assert result3[0] == "Processed: item1"
        assert len(agent.current_batch) == 0
    
    def test_flush(self):
        """Test manual flush."""
        agent = self.TestBatchAgent(batch_size=10, name="batch_agent")
        
        agent.add_item("item1")
        agent.add_item("item2")
        
        results = agent.flush()
        
        assert len(results) == 2
        assert results[0] == "Processed: item1"
        assert len(agent.current_batch) == 0
    
    def test_process_interface(self):
        """Test the process interface."""
        agent = self.TestBatchAgent(batch_size=2, name="batch_agent")
        
        result1 = agent.process("item1")
        assert result1 is None
        
        result2 = agent.process("item2")
        assert len(result2) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])