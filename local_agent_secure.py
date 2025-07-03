#!/usr/bin/env python3
"""
Secure Local LLM command agent with proper safety validation and resource limits.
Maintains Vi-style key bindings and MLflow integration.
"""

import sys
import asyncio
import dspy
import mlflow
from rich import print as rp
from pathlib import Path
from typing import Optional, Dict, Any

# Import security components
from safe_command_agent import SafeCommandAgent
from utils.command_executor import CommandValidator, CommandResult

# ── Enable Vi key-bindings in all readline prompts ────────────────────────────
try:
    import readline
    readline.parse_and_bind("set editing-mode vi")
except Exception:
    pass  # readline might be missing on some platforms


class SecureLocalAgent(SafeCommandAgent):
    """Local agent with secure command execution and DSPy integration."""
    
    def __init__(self, lm_config=None, mlflow_config=None, **kwargs):
        # Initialize parent with security features
        super().__init__(
            name="secure_local_agent",
            command_whitelist_mode=True,
            max_command_memory_mb=1024,  # 1GB for local development
            max_command_cpu_seconds=60,   # 1 minute max
            max_context_tokens=8000,
            **kwargs
        )
        
        # Configure MLflow
        if mlflow_config:
            mlflow.set_tracking_uri(mlflow_config.get('tracking_uri', 'http://localhost:5002'))
            mlflow.set_experiment(mlflow_config.get('experiment', 'secure_local_agent'))
            mlflow.dspy.autolog()
        
        # Configure DSPy
        if lm_config:
            dspy.configure(lm=lm_config)
        
        # Initialize DSPy modules with better safety
        self._init_dspy_modules()
        
        # Add development-friendly commands to whitelist
        dev_commands = [
            'python', 'python3', 'pip', 'pip3', 'poetry', 'uv',
            'git', 'npm', 'node', 'yarn', 'pnpm',
            'docker', 'docker-compose', 'kubectl',
            'pytest', 'mypy', 'ruff', 'black', 'isort',
            'make', 'cmake', 'gcc', 'g++', 'clang',
            'cargo', 'rustc', 'go', 'java', 'javac',
            'curl', 'wget', 'httpie', 'jq',
            'vim', 'nano', 'less', 'more', 'code',
            'find', 'grep', 'rg', 'ag', 'fd',
            'ps', 'top', 'htop', 'kill', 'pkill',
            'df', 'du', 'free', 'uptime', 'who',
        ]
        for cmd in dev_commands:
            self.add_allowed_command(cmd)
        
        # Command history for context
        self.command_run_history = []
        self.current_request = None
    
    def _init_dspy_modules(self):
        """Initialize DSPy modules with secure configurations."""
        # Python code generator with safety guidelines
        self.python_code_generator = dspy.Predict(
            "user_request, system_state_info, python_code_to_run_history, return_value -> python_code_to_run",
            instructions=(
                "Generate safe Python code. Avoid: file deletions, network requests to unknown hosts, "
                "system modifications, or accessing sensitive files. Focus on data processing, "
                "analysis, and safe file operations."
            )
        )
        
        # Command generator with safety emphasis
        self.command_generator = dspy.Predict(
            "user_request, system_state_info, command_run_history, return_value -> command",
            instructions=(
                "Generate safe shell commands. Prefer read-only operations. "
                "Avoid: rm -rf, sudo, system modifications, or commands that could damage the system. "
                "Use absolute paths when possible. Escape special characters properly."
            )
        )
        
        # Enhanced safety checker
        self.safety_checker = dspy.Predict(
            "command_run_history, command, user_request -> command_is_safe_to_execute: bool, reasoning",
            instructions=(
                "Evaluate command safety with strict criteria:\n"
                "UNSAFE if command:\n"
                "- Deletes files or directories (rm, especially with -rf)\n"
                "- Modifies system files (/etc, /sys, /proc)\n"
                "- Uses sudo or attempts privilege escalation\n"
                "- Accesses sensitive files (SSH keys, passwords, tokens)\n"
                "- Could cause system instability (fork bombs, resource exhaustion)\n"
                "- Contains command injection patterns (;, &&, ||, backticks)\n"
                "\n"
                "SAFE if command:\n"
                "- Reads files or lists directories\n"
                "- Runs development tools (git, python, npm)\n"
                "- Performs data analysis or processing\n"
                "- Creates files in user directories\n"
                "- Uses standard development workflows"
            )
        )
        
        # Task completion checker
        self.is_finished_checker = dspy.Predict(
            "user_request, system_state_info, command_run_history, return_value -> reasoning, reply_to_user: str, is_finished: bool",
            instructions=(
                "Determine if the user's request has been completed. "
                "Consider the request finished if:\n"
                "- The requested information has been provided\n"
                "- The requested action has been performed\n"
                "- An error occurred that prevents completion\n"
                "Provide a helpful reply summarizing what was accomplished."
            )
        )
    
    def multiline_input(self, prompt: str = "Paste below (empty line = done):") -> str:
        """Get multiline input from user."""
        print(prompt)
        buf = []
        while True:
            try:
                line = input()
            except EOFError:  # Ctrl-D
                break
            if line == "":
                break
            buf.append(line)
        print("-" * 40)
        return "\n".join(buf)
    
    def generate_command(self, user_request: str, return_value: str = "") -> str:
        """Generate command using DSPy with context."""
        # Get recent context
        recent_history = self.command_run_history[-5:] if self.command_run_history else []
        
        # Generate command
        result = self.command_generator(
            user_request=user_request,
            system_state_info=self._get_system_state(),
            command_run_history=recent_history,
            return_value=return_value,
        )
        
        return result.command
    
    def check_command_safety(self, command: str, user_request: str) -> tuple[bool, str]:
        """Check if command is safe using both DSPy and rule-based validation."""
        # First, use rule-based validation
        is_safe, msg = self.command_executor.validator.validate(command)
        if not is_safe:
            return False, f"Rule-based check: {msg}"
        
        # Then use DSPy for context-aware safety check
        recent_history = self.command_run_history[-3:] if self.command_run_history else []
        result = self.safety_checker(
            command=command,
            command_run_history=recent_history,
            user_request=user_request
        )
        
        # Both must pass
        if not result.command_is_safe_to_execute:
            return False, f"DSPy check: {result.reasoning}"
        
        return True, result.reasoning
    
    def process_request(self, user_request: str):
        """Process a user request with secure command execution."""
        self.current_request = user_request
        return_value = ""
        
        # Add to context
        self.context_manager.add('user', user_request)
        
        while True:
            # Generate command
            command = self.generate_command(user_request, return_value)
            rp(f"[cyan]command[/]: {command}")
            
            # Check safety
            is_safe, reasoning = self.check_command_safety(command, user_request)
            color = "green" if is_safe else "red"
            rp(f"[cyan]safety check:[/] [{color}]{is_safe}[/]")
            print(f"reasoning: {reasoning}")
            
            if is_safe:
                # Execute with security constraints
                result = self.execute_command(command, timeout=30)
                
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    rp(f"[red]Error:[/] {result.stderr}")
                
                return_value = f"Return code: {result.return_code}\n"
                if result.stdout:
                    return_value += f"Output: {result.stdout[:500]}"
                if result.stderr:
                    return_value += f"Error: {result.stderr[:500]}"
            else:
                return_value = f"Command blocked: {reasoning}"
                rp(f"[yellow]Command not executed[/]")
            
            # Add to history
            self.command_run_history.append({
                'command': command,
                'return_value': return_value,
                'safe': is_safe
            })
            
            # Check if finished
            is_finished_result = self.is_finished_checker(
                user_request=user_request,
                system_state_info=self._get_system_state(),
                command_run_history=self.command_run_history[-5:],
                return_value=return_value,
            )
            
            print(f"reasoning: {is_finished_result.reasoning}")
            rp(f"[cyan]reply:[/] [purple]{is_finished_result.reply_to_user}[/]")
            rp(f"[cyan]finished:[/] {is_finished_result.is_finished}")
            
            # Add assistant response to context
            self.context_manager.add('assistant', is_finished_result.reply_to_user)
            
            if is_finished_result.is_finished:
                rp("[green]Task completed![/]")
                break
            
            # Check context usage
            stats = self.get_context_stats()
            if stats['usage_percentage'] > 80:
                rp(f"[yellow]Context {stats['usage_percentage']:.1f}% full[/]")
    
    def _get_system_state(self) -> str:
        """Get current system state information."""
        import os
        import platform
        
        return (
            f"OS: {platform.system()} {platform.release()}\n"
            f"Python: {platform.python_version()}\n"
            f"CWD: {os.getcwd()}\n"
            f"User: {os.environ.get('USER', 'unknown')}"
        )
    
    def run_interactive(self):
        """Run agent in interactive mode."""
        print("\n" + "="*60)
        print("Secure Local Agent - Command Assistant")
        print("="*60)
        print("Features:")
        print("  • Command validation and sandboxing")
        print("  • Resource limits (CPU, memory)")
        print("  • Context-aware safety checking")
        print("  • Vi-style key bindings enabled")
        print("\nCommands: /help, /security, /context, /quit")
        print("="*60 + "\n")
        
        # Process command line arguments if any
        if len(sys.argv) > 1:
            initial_request = " ".join(sys.argv[1:])
            print(f"Processing: {initial_request}")
            self.process_request(initial_request)
        
        # Main loop
        while self.running:
            try:
                user_input = self.multiline_input("\nEnter request (empty line to submit):")
                
                if not user_input:
                    continue
                
                if user_input.startswith('/'):
                    # Handle special commands
                    output = self.handle_command(user_input)
                    if output:
                        print(output)
                else:
                    # Process request
                    self.process_request(user_input)
                    
                    # Show stats
                    cmd_stats = self.get_command_stats()
                    if cmd_stats['total'] > 0:
                        print(f"\n[Stats] Commands: {cmd_stats['total']}, "
                              f"Success: {cmd_stats['success_rate']:.0%}, "
                              f"Blocked: {cmd_stats['block_rate']:.0%}")
                        
            except KeyboardInterrupt:
                print("\nUse /quit to exit")
            except Exception as e:
                rp(f"[bold red]Error:[/bold red] {e}")
                import traceback
                traceback.print_exc()


def main():
    """Main entry point."""
    # Configure MLflow
    mlflow_config = {
        'tracking_uri': 'http://localhost:5002',
        'experiment': 'secure_local_agent'
    }
    
    # Configure language model
    # Options:
    # - Local: dspy.LM('ollama_chat/deepseek-r1:7b', api_base='http://localhost:11434', api_key='')
    # - Cloud: dspy.LM("openrouter/deepseek/deepseek-r1-0528", max_tokens=40000)
    # - Fast: dspy.LM('openrouter/google/gemini-2.5-flash-lite-preview-06-17')
    
    lm = dspy.LM("openrouter/deepseek/deepseek-r1-0528", max_tokens=40000)
    
    # Create and run agent
    agent = SecureLocalAgent(
        lm_config=lm,
        mlflow_config=mlflow_config,
        data_dir=Path(".agent_data"),
    )
    
    agent.run_interactive()


if __name__ == '__main__':
    main()