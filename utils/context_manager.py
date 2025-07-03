"""Context window management with automatic summarization."""
import json
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
import tiktoken


@dataclass
class ContextEntry:
    """Single entry in context window."""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    token_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata,
            'token_count': self.token_count,
        }


class SlidingWindowContext:
    """Manages conversation context with automatic summarization."""
    
    def __init__(
        self,
        max_tokens: int = 4000,
        summary_ratio: float = 0.8,  # Summarize when 80% full
        model: str = "gpt-4",
        summarizer: Optional[Callable] = None,
    ):
        self.max_tokens = max_tokens
        self.summary_ratio = summary_ratio
        self.model = model
        self.summarizer = summarizer
        
        # Use tiktoken for accurate token counting
        try:
            self.encoder = tiktoken.encoding_for_model(model)
        except KeyError:
            self.encoder = tiktoken.get_encoding("cl100k_base")
        
        self.entries: deque[ContextEntry] = deque()
        self.summaries: List[str] = []
        self.total_tokens = 0
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoder.encode(text))
    
    def add(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add entry to context, triggering summarization if needed."""
        token_count = self.count_tokens(content)
        entry = ContextEntry(
            role=role,
            content=content,
            metadata=metadata or {},
            token_count=token_count,
        )
        
        # Check if we need to summarize before adding
        if self.total_tokens + token_count > self.max_tokens * self.summary_ratio:
            self._summarize_oldest()
        
        self.entries.append(entry)
        self.total_tokens += token_count
    
    def _summarize_oldest(self):
        """Summarize oldest entries to make room."""
        if not self.entries or not self.summarizer:
            # If no summarizer, just remove oldest entries
            while self.entries and self.total_tokens > self.max_tokens * 0.5:
                removed = self.entries.popleft()
                self.total_tokens -= removed.token_count
            return
        
        # Collect entries to summarize (oldest 50%)
        entries_to_summarize = []
        tokens_to_remove = 0
        target_tokens = int(self.total_tokens * 0.5)
        
        while self.entries and tokens_to_remove < target_tokens:
            entry = self.entries.popleft()
            entries_to_summarize.append(entry)
            tokens_to_remove += entry.token_count
            self.total_tokens -= entry.token_count
        
        # Create summary
        if entries_to_summarize:
            summary_content = self._create_summary(entries_to_summarize)
            self.summaries.append(summary_content)
    
    def _create_summary(self, entries: List[ContextEntry]) -> str:
        """Create summary of entries."""
        # Format entries for summarization
        conversation = []
        for entry in entries:
            conversation.append(f"{entry.role}: {entry.content}")
        
        full_text = "\n".join(conversation)
        
        if self.summarizer:
            # Use provided summarizer
            return self.summarizer(full_text)
        else:
            # Basic summary (fallback)
            return f"[Summary of {len(entries)} messages from {entries[0].timestamp.strftime('%H:%M')} to {entries[-1].timestamp.strftime('%H:%M')}]"
    
    def get_context(self, include_summaries: bool = True) -> List[Dict[str, str]]:
        """Get current context as list of messages."""
        messages = []
        
        # Add summaries first
        if include_summaries and self.summaries:
            summary_text = "\n\n".join(self.summaries)
            messages.append({
                'role': 'system',
                'content': f"Previous conversation summary:\n{summary_text}"
            })
        
        # Add current entries
        for entry in self.entries:
            messages.append({
                'role': entry.role,
                'content': entry.content
            })
        
        return messages
    
    def get_stats(self) -> Dict[str, Any]:
        """Get context statistics."""
        return {
            'total_tokens': self.total_tokens,
            'max_tokens': self.max_tokens,
            'usage_percentage': (self.total_tokens / self.max_tokens) * 100,
            'entry_count': len(self.entries),
            'summary_count': len(self.summaries),
            'oldest_entry': self.entries[0].timestamp.isoformat() if self.entries else None,
            'newest_entry': self.entries[-1].timestamp.isoformat() if self.entries else None,
        }
    
    def clear(self):
        """Clear all context."""
        self.entries.clear()
        self.summaries.clear()
        self.total_tokens = 0
    
    def save(self, filepath: str):
        """Save context to file."""
        data = {
            'entries': [e.to_dict() for e in self.entries],
            'summaries': self.summaries,
            'total_tokens': self.total_tokens,
            'stats': self.get_stats(),
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self, filepath: str):
        """Load context from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.clear()
        self.summaries = data.get('summaries', [])
        
        for entry_data in data.get('entries', []):
            entry = ContextEntry(
                role=entry_data['role'],
                content=entry_data['content'],
                timestamp=datetime.fromisoformat(entry_data['timestamp']),
                metadata=entry_data.get('metadata', {}),
                token_count=entry_data.get('token_count', 0),
            )
            self.entries.append(entry)
            self.total_tokens += entry.token_count


# Example usage with DSPy
class ContextAwareAgent:
    """Example agent using context manager."""
    
    def __init__(self, max_context_tokens: int = 4000):
        self.context = SlidingWindowContext(
            max_tokens=max_context_tokens,
            summarizer=self._summarize_with_llm,
        )
    
    def _summarize_with_llm(self, text: str) -> str:
        """Summarize using LLM (placeholder)."""
        # In real implementation, use DSPy to summarize
        lines = text.split('\n')
        if len(lines) > 10:
            return f"Summary: Discussed {len(lines)} topics including {lines[0][:50]}..."
        return text
    
    def process_message(self, user_input: str) -> str:
        """Process user message with context management."""
        # Add user input to context
        self.context.add('user', user_input)
        
        # Get current context for LLM
        context_messages = self.context.get_context()
        
        # Generate response (placeholder)
        response = f"Processed with {len(context_messages)} context messages"
        
        # Add response to context
        self.context.add('assistant', response)
        
        # Check context stats
        stats = self.context.get_stats()
        if stats['usage_percentage'] > 90:
            print(f"Warning: Context {stats['usage_percentage']:.1f}% full")
        
        return response


if __name__ == "__main__":
    # Demo context management
    agent = ContextAwareAgent(max_context_tokens=100)  # Small for demo
    
    # Simulate conversation
    for i in range(20):
        user_msg = f"This is message {i} with some content"
        response = agent.process_message(user_msg)
        print(f"Message {i}: {response}")
        
        stats = agent.context.get_stats()
        print(f"  Context: {stats['entry_count']} entries, "
              f"{stats['total_tokens']} tokens, "
              f"{stats['summary_count']} summaries")