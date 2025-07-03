# Security Migration Guide

This guide helps migrate existing agents to use the new security framework.

## Quick Start

### 1. Update Your Agent Base Class

Replace:
```python
from base_agent import CommandAgent

class MyAgent(CommandAgent):
    def execute_command(self, cmd):
        result = subprocess.run(cmd, shell=True, ...)
```

With:
```python
from safe_command_agent import SafeCommandAgent

class MyAgent(SafeCommandAgent):
    def process_user_request(self, request):
        # Use inherited secure execution
        result = self.execute_command(request)
```

### 2. Fix agent_simpledspy.py

Current dangerous code:
```python
# Line 60-74 - UNSAFE
result = subprocess.run(
    command,
    shell=True,
    capture_output=True,
    text=True
)
```

Secure replacement:
```python
from utils.command_executor import SecureCommandExecutor

class SimpleDSPyAgent(SafeCommandAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Already has secure executor from parent
    
    def run_command_action(self, command: str):
        # Validate and execute safely
        result = self.execute_command(command)
        
        if result.return_code == 0:
            return result.stdout
        else:
            return f"Command failed: {result.stderr}"
```

### 3. Fix local_agent.py Safety Checker

Current weak validation:
```python
# Line 91 - TOO PERMISSIVE
safety_prompt = "You are a safety checker. Determine if this command is safe..."
```

Secure replacement:
```python
from safe_command_agent import SafeCommandAgent

class LocalAgent(SafeCommandAgent):
    def __init__(self):
        super().__init__(
            command_whitelist_mode=True,
            max_command_memory_mb=512,
            max_command_cpu_seconds=30,
        )
        
        # Add specific allowed commands
        self.add_allowed_command("npm")
        self.add_allowed_command("pytest")
```

### 4. Add Context Management

Prevent unbounded growth:
```python
class MyAgent(SafeCommandAgent):
    def process_with_llm(self, user_input):
        # Add to managed context
        self.context_manager.add('user', user_input)
        
        # Get bounded context for LLM
        messages = self.get_context_messages()
        
        # Your LLM logic here
        response = self.llm.generate(messages)
        
        # Add response to context
        self.context_manager.add('assistant', response)
        
        return response
```

## Testing Your Migration

### 1. Run Security Tests

```bash
# Run the new security test suite
pytest tests/test_security.py -v

# Test your specific agent
pytest tests/test_your_agent.py -v
```

### 2. Verify Command Blocking

```python
# This should be blocked
result = agent.execute_command("rm -rf /")
assert "validation failed" in result.stderr

# This should work (if whitelisted)
result = agent.execute_command("ls")
assert result.return_code == 0
```

### 3. Check Resource Limits

```python
# This should timeout
result = agent.execute_command("sleep 100", timeout=5)
assert result.timed_out

# This should hit memory limit
result = agent.execute_command("python -c 'x=[0]*10**9'")
assert result.return_code != 0
```

## Configuration Options

### Basic Security Config

```python
agent = SafeCommandAgent(
    name="my_secure_agent",
    command_whitelist_mode=True,  # Only allow specific commands
    max_command_memory_mb=512,     # Memory limit
    max_command_cpu_seconds=30,    # CPU time limit
    max_context_tokens=4000,       # Context window size
    audit_commands=True,           # Log all commands
)
```

### Add Allowed Commands

```python
# During initialization
agent.add_allowed_command("git")
agent.add_allowed_command("python")
agent.add_allowed_command("npm")

# Or in your config
ALLOWED_COMMANDS = [
    "ls", "cat", "grep", "find", "echo", "pwd",
    "git", "python", "pip", "npm", "node",
]
```

### Custom Validation Rules

```python
class MyValidator(CommandValidator):
    def validate(self, command: str) -> Tuple[bool, Optional[str]]:
        # First run parent validation
        is_safe, msg = super().validate(command)
        if not is_safe:
            return is_safe, msg
        
        # Add custom rules
        if "production" in command and "delete" in command:
            return False, "Cannot delete in production"
        
        return True, None
```

## Monitoring & Alerts

### Command Audit Log

```python
# View recent commands
with open(agent.audit_file, 'r') as f:
    for line in f.readlines()[-10:]:
        entry = json.loads(line)
        print(f"{entry['timestamp']}: {entry['command']} -> {entry['status']}")
```

### Security Metrics

```python
stats = agent.get_command_stats()
if stats['block_rate'] > 0.1:  # More than 10% blocked
    alert("High command block rate detected")

if stats['timeout_rate'] > 0.05:  # More than 5% timeouts
    alert("High timeout rate - possible resource exhaustion")
```

## Common Issues

### 1. Command Not Found

```
Error: Command 'npm' not in whitelist
```

**Fix**: Add to whitelist
```python
agent.add_allowed_command("npm")
```

### 2. Context Too Large

```
Warning: Context 95.2% full
```

**Fix**: Automatic summarization will handle this, but you can also:
```python
agent.context_manager.clear()  # Full reset
```

### 3. Resource Limits Hit

```
Error: Command killed due to resource limits
```

**Fix**: Increase limits if needed
```python
agent = SafeCommandAgent(
    max_command_memory_mb=1024,  # 1GB
    max_command_cpu_seconds=60,   # 1 minute
)
```

## Rollback Plan

If issues arise, you can temporarily disable security:

```python
# TEMPORARY - Remove after fixing issues
agent = SafeCommandAgent(
    command_whitelist_mode=False,  # Disable whitelist
    audit_commands=True,            # Keep auditing for debugging
)
```

**Important**: This should only be temporary while fixing issues!

## Next Steps

1. Migrate all agents to use `SafeCommandAgent`
2. Run security tests on each agent
3. Review audit logs after 24 hours
4. Adjust whitelist based on actual usage
5. Enable alerts for security events

Remember: Security is not optional in production systems!