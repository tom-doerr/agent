"""Tests for the ShellWrapper class."""
import asyncio
import os
import tempfile
import pytest
from shell_wrapper import ShellWrapper

@pytest.fixture
async def shell_wrapper():
    """Fixture to create and start a ShellWrapper instance."""
    shell = ShellWrapper()
    await shell.start()
    yield shell
    await shell.stop()

@pytest.mark.asyncio
async def test_shell_start_stop():
    """Test starting and stopping the shell."""
    shell = ShellWrapper()
    await shell.start()
    assert shell.process is not None
    assert shell.process.returncode is None
    await shell.stop()
    assert shell.process.returncode is not None

@pytest.mark.asyncio
async def test_execute_simple_command(shell_wrapper):
    """Test executing a simple command."""
    output, exit_code = await shell_wrapper.execute("echo hello")
    assert "hello" in output
    assert exit_code == 0

@pytest.mark.asyncio
async def test_cd_command(shell_wrapper):
    """Test changing directories."""
    # Get initial directory
    initial_dir = os.getcwd()
    
    # Create temp directory and change to it
    with tempfile.TemporaryDirectory() as temp_dir:
        output, exit_code = await shell_wrapper.execute(f"cd {temp_dir}")
        assert f"Changed directory to {temp_dir}" in output
        assert exit_code == 0
        
        # Verify current working directory changed
        output, exit_code = await shell_wrapper.execute("pwd")
        assert temp_dir in output
        
    # Change back to initial directory
    await shell_wrapper.execute(f"cd {initial_dir}")

@pytest.mark.asyncio
async def test_cd_nonexistent_directory(shell_wrapper):
    """Test changing to a non-existent directory."""
    output, exit_code = await shell_wrapper.execute("cd /nonexistent/directory")
    assert "cd error" in output
    assert "Directory not found" in output
    assert exit_code == 1

@pytest.mark.asyncio
async def test_command_with_error(shell_wrapper):
    """Test command that returns non-zero exit code."""
    output, exit_code = await shell_wrapper.execute("ls /nonexistent/file")
    assert "No such file or directory" in output
    assert exit_code != 0

@pytest.mark.asyncio
async def test_concurrent_commands(shell_wrapper):
    """Test executing commands concurrently."""
    commands = ["echo test1", "echo test2", "echo test3"]
    results = await asyncio.gather(
        *(shell_wrapper.execute(cmd) for cmd in commands)
    )
    
    for (output, exit_code), cmd in zip(results, commands):
        assert cmd.split()[1] in output
        assert exit_code == 0
