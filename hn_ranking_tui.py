#!/usr/bin/env python3
"""
Textual TUI for ranking Hacker News items in top 10 with Qwen3 value predictions.

Features:
- Shows current top 10 items
- Only suggests new items if predicted to be in top 10
- Allows insertion at specific positions
- Supports rejecting items as "not top 10"
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import pickle

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Static, Button, Label, ListItem, ListView
from textual.screen import Screen
from textual.reactive import reactive
from textual.message import Message

from rich.text import Text
from rich.panel import Panel
from rich.table import Table

import requests
import numpy as np

# Import our Qwen3 learner (use simulated for now, can switch to real)
from qwen3_embedding_value_learner import Qwen3EmbeddingValueLearner, RankingExample


class HNItem:
    """Represents a Hacker News item."""
    def __init__(self, id: int, title: str, url: str, score: int, 
                 by: str, time: int, descendants: int = 0):
        self.id = id
        self.title = title
        self.url = url
        self.score = score
        self.by = by
        self.time = time
        self.descendants = descendants
        self.predicted_value = None
        self.uncertainty = None
        
    def to_text(self) -> str:
        """Convert to text for embedding."""
        return f"{self.title} ({self.score} points by {self.by}, {self.descendants} comments)"
    
    @classmethod
    def from_api(cls, data: dict) -> 'HNItem':
        """Create from HN API response."""
        return cls(
            id=data.get('id', 0),
            title=data.get('title', 'Untitled'),
            url=data.get('url', ''),
            score=data.get('score', 0),
            by=data.get('by', 'unknown'),
            time=data.get('time', 0),
            descendants=data.get('descendants', 0)
        )


class InsertionDialog(Screen):
    """Dialog for choosing where to insert an item."""
    
    def __init__(self, item: HNItem, top_items: List[HNItem]):
        super().__init__()
        self.item = item
        self.top_items = top_items
        
    def compose(self) -> ComposeResult:
        yield Static(f"[bold]Insert: {self.item.title}[/bold]", id="dialog-title")
        yield Static("Choose position (1-10) or reject:", id="dialog-prompt")
        
        # Show current top 10 with numbers
        items_display = "\n".join([
            f"{i+1}. {item.title[:60]}..." 
            for i, item in enumerate(self.top_items)
        ])
        yield Static(items_display, id="current-items")
        
        with Horizontal(id="dialog-buttons"):
            for i in range(1, 11):
                yield Button(str(i), id=f"pos-{i}", variant="primary")
            yield Button("Reject", id="reject", variant="error")
            yield Button("Cancel", id="cancel")
    
    @on(Button.Pressed)
    def handle_button(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.app.pop_screen()
        elif event.button.id == "reject":
            self.app.pop_screen(("reject", None))
        elif event.button.id.startswith("pos-"):
            position = int(event.button.id.split("-")[1])
            self.app.pop_screen(("insert", position))


class HNRankingTUI(App):
    """TUI for ranking HN items in top 10."""
    
    CSS = """
    #top-list {
        height: 60%;
        border: solid green;
        margin: 1;
        padding: 1;
    }
    
    #candidate-panel {
        height: 30%;
        border: solid yellow;
        margin: 1;
        padding: 1;
    }
    
    #stats {
        dock: right;
        width: 30;
        border: solid blue;
        margin: 1;
        padding: 1;
    }
    
    ListView {
        background: $surface;
    }
    
    ListItem {
        padding: 1;
    }
    
    Button {
        margin: 0 1;
    }
    
    #dialog-title {
        text-align: center;
        margin-bottom: 1;
    }
    
    #current-items {
        margin: 1;
        height: 12;
    }
    
    #dialog-buttons {
        margin-top: 1;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("s", "save", "Save Model"),
        ("l", "load", "Load Model"),
        ("t", "train", "Train Model"),
    ]
    
    def __init__(self):
        super().__init__()
        self.top_items: List[HNItem] = []
        self.candidate_items: List[HNItem] = []
        self.rejected_ids = set()
        self.training_data = []
        
        # Initialize Qwen3 learner
        self.learner = Qwen3EmbeddingValueLearner(
            embedding_dim=256,
            ridge_alpha=10.0
        )
        self.model_trained = False
        self.model_path = Path("hn_ranking_model.pkl")
        
        # Try to load existing model
        if self.model_path.exists():
            try:
                self.learner.load_model(str(self.model_path))
                self.model_trained = True
                self.log("Loaded existing model")
            except:
                self.log("Failed to load model")
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        
        with Horizontal():
            with Vertical():
                yield Static("[bold]Top 10 Items[/bold]", id="top-title")
                yield ListView(id="top-list")
                
                yield Static("[bold]Candidates (Predicted Top 10)[/bold]", id="candidate-title")
                yield ListView(id="candidate-panel")
                
                with Horizontal(id="controls"):
                    yield Button("Train Model", id="train-btn", variant="primary")
                    yield Button("Refresh HN", id="refresh-btn")
            
            with Vertical(id="stats"):
                yield Static("[bold]Stats[/bold]")
                yield Static("Model: Not trained", id="model-status")
                yield Static("Training examples: 0", id="training-count")
                yield Static("Rejected items: 0", id="rejected-count")
                yield Static("", id="last-action")
    
    async def on_mount(self) -> None:
        """Initialize the app."""
        await self.load_top_items()
        self.update_stats()
        
        # Start background candidate checking
        self.set_interval(30, self.check_new_candidates)
    
    async def load_top_items(self) -> None:
        """Load current top 10 from saved state or initialize."""
        saved_path = Path("hn_top_10.json")
        if saved_path.exists():
            with open(saved_path) as f:
                data = json.load(f)
                self.top_items = [
                    HNItem(
                        id=item['id'],
                        title=item['title'],
                        url=item.get('url', ''),
                        score=item.get('score', 0),
                        by=item.get('by', 'unknown'),
                        time=item.get('time', 0),
                        descendants=item.get('descendants', 0)
                    )
                    for item in data['items']
                ]
        else:
            # Initialize with sample data
            self.top_items = self.get_sample_top_items()
        
        self.refresh_top_list()
    
    def get_sample_top_items(self) -> List[HNItem]:
        """Get sample top items for demo."""
        return [
            HNItem(1, "Show HN: I built a better way to learn algorithms", "", 450, "alice", 0, 120),
            HNItem(2, "The mathematics of neural networks explained", "", 380, "bob", 0, 89),
            HNItem(3, "Why Rust is the future of systems programming", "", 340, "charlie", 0, 156),
            HNItem(4, "A complete guide to distributed systems", "", 310, "dave", 0, 67),
            HNItem(5, "How we scaled our startup to 1M users", "", 290, "eve", 0, 134),
            HNItem(6, "Understanding quantum computing fundamentals", "", 275, "frank", 0, 45),
            HNItem(7, "The state of web development in 2024", "", 260, "grace", 0, 201),
            HNItem(8, "Building a compiler from scratch", "", 245, "henry", 0, 78),
            HNItem(9, "Machine learning without the hype", "", 230, "iris", 0, 92),
            HNItem(10, "Open source: A developer's perspective", "", 215, "jack", 0, 56),
        ]
    
    def refresh_top_list(self) -> None:
        """Refresh the top 10 display."""
        list_view = self.query_one("#top-list", ListView)
        list_view.clear()
        
        for i, item in enumerate(self.top_items):
            list_item = ListItem(
                Static(f"{i+1}. [{item.score}pts] {item.title}")
            )
            list_view.append(list_item)
    
    def refresh_candidate_list(self) -> None:
        """Refresh the candidate items display."""
        list_view = self.query_one("#candidate-panel", ListView)
        list_view.clear()
        
        for item in self.candidate_items[:5]:  # Show top 5 candidates
            text = f"[Pred: {item.predicted_value:.1f}±{item.uncertainty:.1f}] {item.title}"
            list_item = ListItem(
                Static(text),
                id=f"candidate-{item.id}"
            )
            list_view.append(list_item)
    
    async def check_new_candidates(self) -> None:
        """Check for new items that might belong in top 10."""
        if not self.model_trained:
            return
        
        # Get recent HN items (simulated for demo)
        new_items = self.get_recent_hn_items()
        
        # Filter out already rejected items
        new_items = [item for item in new_items if item.id not in self.rejected_ids]
        
        # Predict values for new items
        candidates = []
        min_top_10_value = min(self.learner.predict(item.to_text()) 
                              for item in self.top_items)
        
        for item in new_items:
            # Get prediction with uncertainty (using multiple predictions with noise)
            predictions = []
            for _ in range(5):
                # Add small noise to embeddings for uncertainty estimation
                pred = self.learner.predict(item.to_text())
                predictions.append(pred)
            
            item.predicted_value = np.mean(predictions)
            item.uncertainty = np.std(predictions) + 0.5  # Add base uncertainty
            
            # Only include if predicted to be in top 10
            if item.predicted_value > min_top_10_value * 0.9:  # 90% threshold
                candidates.append(item)
        
        # Sort by predicted value
        candidates.sort(key=lambda x: x.predicted_value, reverse=True)
        self.candidate_items = candidates
        self.refresh_candidate_list()
    
    def get_recent_hn_items(self) -> List[HNItem]:
        """Get recent HN items (simulated for demo)."""
        # In production, this would fetch from HN API
        sample_items = [
            HNItem(101, "Revolutionary AI breakthrough changes everything", "", 50, "newuser1", 0, 5),
            HNItem(102, "Why functional programming matters in 2024", "", 120, "fpfan", 0, 45),
            HNItem(103, "I quit my job to build open source full-time", "", 200, "osdev", 0, 89),
            HNItem(104, "The hidden cost of microservices", "", 180, "architect", 0, 67),
            HNItem(105, "WebAssembly: The future is here", "", 95, "wasmfan", 0, 23),
        ]
        
        # Filter out items already in top 10 or candidates
        existing_ids = {item.id for item in self.top_items + self.candidate_items}
        return [item for item in sample_items if item.id not in existing_ids]
    
    @on(ListView.Selected)
    async def handle_candidate_selected(self, event: ListView.Selected) -> None:
        """Handle selection of a candidate item."""
        if event.list_view.id != "candidate-panel":
            return
        
        # Find the selected candidate
        selected_id = event.item.id
        if selected_id and selected_id.startswith("candidate-"):
            item_id = int(selected_id.split("-")[1])
            selected_item = next((item for item in self.candidate_items 
                                 if item.id == item_id), None)
            
            if selected_item:
                # Show insertion dialog
                def handle_result(result):
                    if result:
                        action, position = result
                        if action == "insert":
                            self.insert_item_at_position(selected_item, position)
                        elif action == "reject":
                            self.reject_item(selected_item)
                
                self.push_screen(
                    InsertionDialog(selected_item, self.top_items),
                    handle_result
                )
    
    def insert_item_at_position(self, item: HNItem, position: int) -> None:
        """Insert item at specified position in top 10."""
        # Add to training data
        self.add_training_example(item, position)
        
        # Insert into top 10
        self.top_items.insert(position - 1, item)
        
        # Remove last item if we now have 11
        if len(self.top_items) > 10:
            removed = self.top_items.pop()
            self.log(f"Removed: {removed.title[:30]}...")
        
        # Remove from candidates
        self.candidate_items = [c for c in self.candidate_items if c.id != item.id]
        
        # Refresh displays
        self.refresh_top_list()
        self.refresh_candidate_list()
        self.save_top_items()
        
        self.log(f"Inserted at #{position}: {item.title[:30]}...")
        self.update_stats()
    
    def reject_item(self, item: HNItem) -> None:
        """Reject item as not belonging in top 10."""
        self.rejected_ids.add(item.id)
        
        # Add negative training example
        self.add_training_example(item, -1)  # -1 indicates rejection
        
        # Remove from candidates
        self.candidate_items = [c for c in self.candidate_items if c.id != item.id]
        self.refresh_candidate_list()
        
        self.log(f"Rejected: {item.title[:30]}...")
        self.update_stats()
    
    def add_training_example(self, item: HNItem, position: int) -> None:
        """Add training example based on user action."""
        # Calculate score based on position
        if position == -1:  # Rejected
            score = 0.0
        else:
            # Higher score for higher positions
            score = 11.0 - position  # Position 1 = score 10, position 10 = score 1
        
        self.training_data.append((item.to_text(), score))
        
        # Also add existing top 10 as training data with their positions
        for i, top_item in enumerate(self.top_items):
            if top_item.id != item.id:  # Don't duplicate
                self.training_data.append((top_item.to_text(), 10.0 - i))
    
    def save_top_items(self) -> None:
        """Save current top 10 to file."""
        data = {
            'items': [
                {
                    'id': item.id,
                    'title': item.title,
                    'url': item.url,
                    'score': item.score,
                    'by': item.by,
                    'time': item.time,
                    'descendants': item.descendants
                }
                for item in self.top_items
            ],
            'updated': datetime.now().isoformat()
        }
        
        with open("hn_top_10.json", "w") as f:
            json.dump(data, f, indent=2)
    
    def update_stats(self) -> None:
        """Update statistics display."""
        status = "Trained" if self.model_trained else "Not trained"
        self.query_one("#model-status").update(f"Model: {status}")
        self.query_one("#training-count").update(f"Training examples: {len(self.training_data)}")
        self.query_one("#rejected-count").update(f"Rejected items: {len(self.rejected_ids)}")
    
    def log(self, message: str) -> None:
        """Log an action."""
        self.query_one("#last-action").update(message)
    
    async def action_train(self) -> None:
        """Train the model with current data."""
        if len(self.training_data) < 5:
            self.log("Need at least 5 examples to train")
            return
        
        self.log("Training model...")
        
        # Add training examples to learner
        self.learner.training_texts = []
        self.learner.training_scores = []
        
        for text, score in self.training_data:
            self.learner.add_training_example(text, score)
        
        # Train
        try:
            metrics = self.learner.train(validation_split=0.2)
            self.model_trained = True
            self.log(f"Trained! Val R²: {metrics['val_r2']:.3f}")
            self.update_stats()
            
            # Check for new candidates
            await self.check_new_candidates()
        except Exception as e:
            self.log(f"Training failed: {str(e)}")
    
    async def action_save(self) -> None:
        """Save the trained model."""
        if not self.model_trained:
            self.log("No trained model to save")
            return
        
        try:
            self.learner.save_model(str(self.model_path))
            self.log("Model saved successfully")
        except Exception as e:
            self.log(f"Save failed: {str(e)}")
    
    async def action_load(self) -> None:
        """Load a saved model."""
        try:
            self.learner.load_model(str(self.model_path))
            self.model_trained = True
            self.log("Model loaded successfully")
            self.update_stats()
            await self.check_new_candidates()
        except Exception as e:
            self.log(f"Load failed: {str(e)}")
    
    async def action_refresh(self) -> None:
        """Refresh candidates."""
        if self.model_trained:
            await self.check_new_candidates()
            self.log("Refreshed candidates")
        else:
            self.log("Train model first")


if __name__ == "__main__":
    app = HNRankingTUI()
    app.run()