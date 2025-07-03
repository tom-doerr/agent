"""Base agent class providing standardized interfaces for all agents."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import logging
import time

from utils.io import ndjson_iter, append_ndjson


class BaseAgent(ABC):
    """Abstract base class for all agents in the system."""
    
    def __init__(
        self,
        name: str,
        data_dir: Path = Path("."),
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize base agent.
        
        Args:
            name: Agent identifier
            data_dir: Directory for data storage
            logger: Optional logger instance
        """
        self.name = name
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.logger = logger or logging.getLogger(name)
        self.history: List[Dict[str, Any]] = []
        self.start_time = time.time()
    
    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """
        Main processing method - must be implemented by subclasses.
        
        Args:
            input_data: Input to process
            
        Returns:
            Processing result
        """
        pass
    
    def load_history(self, filename: str = None) -> List[Dict[str, Any]]:
        """Load agent history from file."""
        if filename is None:
            filename = f"{self.name}_history.ndjson"
        
        history_path = self.data_dir / filename
        self.history = list(ndjson_iter(history_path))
        return self.history
    
    def save_history_item(self, item: Dict[str, Any], filename: str = None):
        """Save a single history item."""
        if filename is None:
            filename = f"{self.name}_history.ndjson"
        
        # Add metadata
        item["agent"] = self.name
        item["timestamp"] = int(time.time())
        
        history_path = self.data_dir / filename
        append_ndjson(history_path, item)
        self.history.append(item)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "name": self.name,
            "uptime": time.time() - self.start_time,
            "history_size": len(self.history),
            "data_dir": str(self.data_dir)
        }
    
    def reset(self):
        """Reset agent state."""
        self.history = []
        self.start_time = time.time()
        self.logger.info(f"Agent {self.name} reset")


class CommandAgent(BaseAgent):
    """Base class for agents that handle commands."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commands = {}
        self._register_default_commands()
    
    def _register_default_commands(self):
        """Register default commands available to all command agents."""
        self.register_command("help", self._cmd_help, "Show available commands")
        self.register_command("status", self._cmd_status, "Show agent status")
        self.register_command("history", self._cmd_history, "Show command history")
    
    def register_command(self, name: str, handler: callable, description: str = ""):
        """Register a new command."""
        self.commands[name] = {
            "handler": handler,
            "description": description
        }
    
    def _cmd_help(self, *args) -> str:
        """Show available commands."""
        lines = ["Available commands:"]
        for cmd, info in self.commands.items():
            lines.append(f"  {cmd}: {info['description']}")
        return "\n".join(lines)
    
    def _cmd_status(self, *args) -> str:
        """Show agent status."""
        status = self.get_status()
        lines = [f"Agent: {status['name']}"]
        lines.append(f"Uptime: {status['uptime']:.1f} seconds")
        lines.append(f"History items: {status['history_size']}")
        return "\n".join(lines)
    
    def _cmd_history(self, *args) -> str:
        """Show recent command history."""
        if not self.history:
            return "No history available"
        
        lines = ["Recent commands:"]
        for item in self.history[-10:]:
            cmd = item.get("command", "unknown")
            ts = item.get("timestamp", 0)
            lines.append(f"  [{time.strftime('%H:%M:%S', time.localtime(ts))}] {cmd}")
        return "\n".join(lines)
    
    def process(self, input_data: str) -> str:
        """Process a command string."""
        parts = input_data.strip().split()
        if not parts:
            return "No command provided"
        
        command = parts[0].lower()
        args = parts[1:]
        
        # Save to history
        self.save_history_item({
            "command": command,
            "args": args,
            "input": input_data
        })
        
        # Execute command
        if command in self.commands:
            try:
                result = self.commands[command]["handler"](*args)
                return str(result)
            except Exception as e:
                self.logger.error(f"Command error: {e}")
                return f"Error executing {command}: {e}"
        else:
            return f"Unknown command: {command}. Type 'help' for available commands."


class BatchProcessingAgent(BaseAgent):
    """Base class for agents that process data in batches."""
    
    def __init__(self, batch_size: int = 100, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.batch_size = batch_size
        self.current_batch = []
    
    @abstractmethod
    def process_batch(self, batch: List[Any]) -> List[Any]:
        """Process a batch of items - must be implemented by subclasses."""
        pass
    
    def add_item(self, item: Any):
        """Add item to current batch."""
        self.current_batch.append(item)
        
        if len(self.current_batch) >= self.batch_size:
            return self.flush()
        return None
    
    def flush(self) -> List[Any]:
        """Process current batch and return results."""
        if not self.current_batch:
            return []
        
        results = self.process_batch(self.current_batch)
        self.current_batch = []
        return results
    
    def process(self, input_data: Any) -> Any:
        """Process input - adds to batch and returns results if batch is full."""
        return self.add_item(input_data)