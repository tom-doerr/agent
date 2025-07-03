"""Enhanced base agent with security-first command execution."""
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
import json

from base_agent import BaseAgent
from utils.command_executor import SecureCommandExecutor, CommandValidator, CommandResult
from utils.context_manager import SlidingWindowContext
from utils.io import append_ndjson


class SafeCommandAgent(BaseAgent):
    """Base agent with secure command execution and context management."""
    
    def __init__(
        self,
        name: str = "safe_agent",
        data_dir: Optional[Path] = None,
        max_context_tokens: int = 4000,
        max_command_memory_mb: int = 512,
        max_command_cpu_seconds: int = 30,
        command_whitelist_mode: bool = True,
        audit_commands: bool = True,
    ):
        super().__init__(name=name, data_dir=data_dir)
        
        # Initialize secure command executor
        self.command_executor = SecureCommandExecutor(
            validator=CommandValidator(whitelist_mode=command_whitelist_mode),
            max_memory_mb=max_command_memory_mb,
            max_cpu_seconds=max_command_cpu_seconds,
            working_dir=self.data_dir,
        )
        
        # Initialize context manager
        self.context_manager = SlidingWindowContext(
            max_tokens=max_context_tokens,
            summarizer=self._summarize_context,
        )
        
        # Audit settings
        self.audit_commands = audit_commands
        self.audit_file = self.data_dir / "command_audit.ndjson"
        
        # Command statistics
        self.command_stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'blocked': 0,
            'timed_out': 0,
        }
        
        logging.info(f"Initialized {name} with secure command execution")
    
    def _summarize_context(self, text: str) -> str:
        """Summarize context (override in subclass with LLM)."""
        # Basic implementation - subclasses should use LLM
        lines = text.split('\n')
        return f"[Summarized {len(lines)} exchanges]"
    
    def execute_command(
        self,
        command: str,
        timeout: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CommandResult:
        """Execute command with security checks and auditing."""
        start_time = datetime.now()
        
        # Pre-execution audit entry
        audit_entry = {
            'timestamp': start_time.isoformat(),
            'command': command,
            'metadata': metadata or {},
            'status': 'pending',
        }
        
        try:
            # Execute with security constraints
            result = self.command_executor.execute(command, timeout=timeout)
            
            # Update statistics
            self.command_stats['total'] += 1
            if result.return_code == 0:
                self.command_stats['successful'] += 1
                audit_entry['status'] = 'success'
            elif result.timed_out:
                self.command_stats['timed_out'] += 1
                audit_entry['status'] = 'timeout'
            elif "validation failed" in result.stderr:
                self.command_stats['blocked'] += 1
                audit_entry['status'] = 'blocked'
            else:
                self.command_stats['failed'] += 1
                audit_entry['status'] = 'failed'
            
            # Complete audit entry
            audit_entry.update({
                'return_code': result.return_code,
                'duration_seconds': (datetime.now() - start_time).total_seconds(),
                'stdout_size': len(result.stdout),
                'stderr_size': len(result.stderr),
                'error_preview': result.stderr[:200] if result.stderr else None,
            })
            
            # Add to context
            self.context_manager.add(
                role='system',
                content=f"Command: {command}\nStatus: {audit_entry['status']}\nOutput: {result.stdout[:500]}",
                metadata={'command_audit': audit_entry}
            )
            
            return result
            
        except Exception as e:
            # Log unexpected errors
            audit_entry['status'] = 'error'
            audit_entry['error'] = str(e)
            logging.error(f"Command execution error: {e}")
            
            return CommandResult(
                stdout="",
                stderr=f"Unexpected error: {e}",
                return_code=-1,
            )
        
        finally:
            # Always audit
            if self.audit_commands:
                append_ndjson(self.audit_file, audit_entry)
    
    def add_allowed_command(self, command: str):
        """Add command to whitelist."""
        if isinstance(self.command_executor.validator, CommandValidator):
            self.command_executor.validator.WHITELIST_COMMANDS.append(command)
            logging.info(f"Added '{command}' to command whitelist")
    
    def get_command_stats(self) -> Dict[str, Any]:
        """Get command execution statistics."""
        total = max(self.command_stats['total'], 1)  # Avoid division by zero
        return {
            **self.command_stats,
            'success_rate': self.command_stats['successful'] / total,
            'block_rate': self.command_stats['blocked'] / total,
            'timeout_rate': self.command_stats['timed_out'] / total,
        }
    
    def get_context_messages(self) -> List[Dict[str, str]]:
        """Get current context messages."""
        return self.context_manager.get_context()
    
    def get_context_stats(self) -> Dict[str, Any]:
        """Get context window statistics."""
        return self.context_manager.get_stats()
    
    def save_state(self):
        """Save agent state including context."""
        super().save_state()
        
        # Save context
        context_file = self.data_dir / f"{self.name}_context.json"
        self.context_manager.save(str(context_file))
        
        # Save command stats
        stats_file = self.data_dir / f"{self.name}_command_stats.json"
        with open(stats_file, 'w') as f:
            json.dump(self.get_command_stats(), f, indent=2)
    
    def load_state(self):
        """Load agent state including context."""
        super().load_state()
        
        # Load context if exists
        context_file = self.data_dir / f"{self.name}_context.json"
        if context_file.exists():
            self.context_manager.load(str(context_file))
        
        # Load command stats if exists
        stats_file = self.data_dir / f"{self.name}_command_stats.json"
        if stats_file.exists():
            with open(stats_file, 'r') as f:
                loaded_stats = json.load(f)
                # Only load the counting stats, not computed rates
                for key in ['total', 'successful', 'failed', 'blocked', 'timed_out']:
                    if key in loaded_stats:
                        self.command_stats[key] = loaded_stats[key]
    
    def handle_help(self) -> str:
        """Provide help information."""
        base_help = super().handle_help()
        security_help = """
Security Features:
  - Command validation with whitelist/blacklist
  - Resource limits (CPU, memory)
  - Automatic timeouts
  - Command auditing
  - Context window management

Stats Commands:
  - /security - Show security statistics
  - /context - Show context window stats
  - /audit - Show recent command audit
"""
        return base_help + security_help
    
    def run(self):
        """Main agent loop with enhanced commands."""
        print(f"\n{self.name} started with security features enabled")
        print("Type /help for available commands or /quit to exit\n")
        
        while self.running:
            try:
                user_input = input("> ").strip()
                
                if user_input.startswith("/"):
                    # Handle special commands
                    parts = user_input.split(maxsplit=1)
                    command = parts[0].lower()
                    
                    if command == "/security":
                        stats = self.get_command_stats()
                        print("\nSecurity Statistics:")
                        print(f"  Total commands: {stats['total']}")
                        print(f"  Success rate: {stats['success_rate']:.1%}")
                        print(f"  Blocked rate: {stats['block_rate']:.1%}")
                        print(f"  Timeout rate: {stats['timeout_rate']:.1%}")
                    
                    elif command == "/context":
                        stats = self.get_context_stats()
                        print("\nContext Window:")
                        print(f"  Usage: {stats['usage_percentage']:.1f}%")
                        print(f"  Entries: {stats['entry_count']}")
                        print(f"  Summaries: {stats['summary_count']}")
                    
                    elif command == "/audit":
                        # Show last 5 audit entries
                        if self.audit_file.exists():
                            with open(self.audit_file, 'r') as f:
                                lines = f.readlines()
                                recent = lines[-5:] if len(lines) >= 5 else lines
                                print("\nRecent Command Audit:")
                                for line in recent:
                                    entry = json.loads(line)
                                    print(f"  [{entry['timestamp']}] {entry['command'][:50]} -> {entry['status']}")
                    
                    else:
                        # Delegate to parent class
                        output = self.handle_command(user_input)
                        if output:
                            print(output)
                else:
                    # Regular command - add to context and process
                    self.context_manager.add('user', user_input)
                    
                    # This is where subclasses would use LLM to decide action
                    # For now, just try to execute as command
                    result = self.execute_command(user_input)
                    
                    if result.stdout:
                        print(result.stdout)
                    if result.stderr:
                        print(f"Error: {result.stderr}")
                    
                    # Add result to context
                    self.context_manager.add(
                        'assistant',
                        f"Executed with return code {result.return_code}"
                    )
                    
            except KeyboardInterrupt:
                print("\nUse /quit to exit")
            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                print(f"Error: {e}")


if __name__ == "__main__":
    # Example usage
    agent = SafeCommandAgent(
        name="secure_demo",
        command_whitelist_mode=True,
        max_command_memory_mb=256,
        max_command_cpu_seconds=10,
    )
    
    # Add some allowed commands for demo
    agent.add_allowed_command("date")
    agent.add_allowed_command("whoami")
    
    # Run the agent
    agent.run()