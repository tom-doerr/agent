"""Secure command execution framework with validation and sandboxing."""
import subprocess
import shlex
import re
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
from pathlib import Path
import resource
import signal
from contextlib import contextmanager


@dataclass
class CommandResult:
    """Result of command execution."""
    stdout: str
    stderr: str
    return_code: int
    timed_out: bool = False
    killed: bool = False


class CommandValidator:
    """Validates commands against security rules."""
    
    # Dangerous patterns that should never be allowed
    BLACKLIST_PATTERNS = [
        r'rm\s+-rf\s+/',  # Recursive force delete from root
        r':(){ :|:& };:',  # Fork bomb
        r'>\s*/dev/sda',   # Direct disk writes
        r'dd\s+if=.*of=/dev/',  # DD to devices
        r'mkfs\.',         # Filesystem formatting
        r'>\s*\/proc',     # Writing to /proc
        r'>\s*\/sys',      # Writing to /sys
    ]
    
    # Only allow specific commands in whitelist mode
    WHITELIST_COMMANDS = [
        'ls', 'cat', 'grep', 'find', 'echo', 'pwd', 'cd',
        'git', 'python', 'pip', 'npm', 'node', 'curl', 'wget',
        'mkdir', 'touch', 'cp', 'mv', 'head', 'tail', 'wc',
        'sort', 'uniq', 'diff', 'sed', 'awk', 'cut', 'tr',
    ]
    
    def __init__(self, whitelist_mode: bool = True):
        self.whitelist_mode = whitelist_mode
        self.blacklist_re = [re.compile(p) for p in self.BLACKLIST_PATTERNS]
    
    def validate(self, command: str) -> Tuple[bool, Optional[str]]:
        """Validate a command for safety.
        
        Returns:
            (is_safe, error_message)
        """
        # Check blacklist patterns first (always)
        for pattern in self.blacklist_re:
            if pattern.search(command):
                return False, f"Command matches dangerous pattern: {pattern.pattern}"
        
        # Parse command to get base command
        try:
            parts = shlex.split(command)
            if not parts:
                return False, "Empty command"
            base_cmd = parts[0]
        except ValueError as e:
            return False, f"Invalid command syntax: {e}"
        
        # In whitelist mode, only allow specific commands
        if self.whitelist_mode:
            # Handle absolute paths by extracting command name
            cmd_name = Path(base_cmd).name
            if cmd_name not in self.WHITELIST_COMMANDS:
                return False, f"Command '{cmd_name}' not in whitelist"
        
        # Additional checks
        if '&&' in command or '||' in command or ';' in command:
            return False, "Command chaining not allowed for security"
        
        if '|' in command:
            # Check all commands in pipeline
            pipe_parts = command.split('|')
            for part in pipe_parts:
                is_safe, msg = self.validate(part.strip())
                if not is_safe:
                    return False, f"Unsafe command in pipeline: {msg}"
        
        return True, None


class SecureCommandExecutor:
    """Execute commands with security constraints."""
    
    def __init__(
        self,
        validator: Optional[CommandValidator] = None,
        max_memory_mb: int = 512,
        max_cpu_seconds: int = 30,
        max_output_size: int = 1024 * 1024,  # 1MB
        working_dir: Optional[Path] = None,
    ):
        self.validator = validator or CommandValidator()
        self.max_memory_mb = max_memory_mb
        self.max_cpu_seconds = max_cpu_seconds
        self.max_output_size = max_output_size
        self.working_dir = working_dir or Path.cwd()
    
    @contextmanager
    def _resource_limits(self):
        """Apply resource limits to subprocess."""
        def set_limits():
            # Memory limit
            memory_bytes = self.max_memory_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
            
            # CPU time limit
            resource.setrlimit(resource.RLIMIT_CPU, (self.max_cpu_seconds, self.max_cpu_seconds))
            
            # Prevent core dumps
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
            
            # Limit number of processes
            resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))
        
        yield set_limits
    
    def execute(
        self,
        command: str,
        timeout: Optional[int] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> CommandResult:
        """Execute a command with security constraints.
        
        Args:
            command: Shell command to execute
            timeout: Maximum execution time in seconds
            env: Environment variables (filtered for security)
            
        Returns:
            CommandResult with output and status
        """
        # Validate command
        is_safe, error_msg = self.validator.validate(command)
        if not is_safe:
            return CommandResult(
                stdout="",
                stderr=f"Command validation failed: {error_msg}",
                return_code=1,
            )
        
        # Filter environment variables (remove sensitive ones)
        safe_env = dict(env or {})
        sensitive_vars = ['API_KEY', 'TOKEN', 'PASSWORD', 'SECRET']
        for var in list(safe_env.keys()):
            if any(s in var.upper() for s in sensitive_vars):
                safe_env.pop(var)
        
        timeout = timeout or self.max_cpu_seconds
        
        try:
            with self._resource_limits() as set_limits:
                # Use shlex to safely parse command
                proc = subprocess.Popen(
                    shlex.split(command),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=self.working_dir,
                    env=safe_env,
                    preexec_fn=set_limits,
                )
                
                try:
                    stdout, stderr = proc.communicate(timeout=timeout)
                    
                    # Truncate output if too large
                    if len(stdout) > self.max_output_size:
                        stdout = stdout[:self.max_output_size] + "\n[OUTPUT TRUNCATED]"
                    if len(stderr) > self.max_output_size:
                        stderr = stderr[:self.max_output_size] + "\n[OUTPUT TRUNCATED]"
                    
                    return CommandResult(
                        stdout=stdout,
                        stderr=stderr,
                        return_code=proc.returncode,
                    )
                    
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()  # Clean up zombie process
                    return CommandResult(
                        stdout="",
                        stderr=f"Command timed out after {timeout} seconds",
                        return_code=-1,
                        timed_out=True,
                    )
                    
        except Exception as e:
            return CommandResult(
                stdout="",
                stderr=f"Command execution failed: {str(e)}",
                return_code=-1,
            )


# Example usage patterns
if __name__ == "__main__":
    # Create executor with strict security
    executor = SecureCommandExecutor(
        validator=CommandValidator(whitelist_mode=True),
        max_memory_mb=256,
        max_cpu_seconds=10,
    )
    
    # Safe command
    result = executor.execute("ls -la")
    print(f"Safe command result: {result.return_code}")
    
    # Dangerous command (will be blocked)
    result = executor.execute("rm -rf /")
    print(f"Dangerous command blocked: {result.stderr}")
    
    # Command with resource limits
    result = executor.execute("find / -name '*.txt'", timeout=5)
    print(f"Resource limited command: {result.timed_out}")