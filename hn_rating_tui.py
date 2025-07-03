#!/usr/bin/env python3
"""
Textual TUI for directly rating Hacker News items with Qwen3 uncertainty display.

Features:
- Direct rating interface (1-10 scale)
- Shows Qwen3 prediction with uncertainty
- Tracks rating accuracy
- Updates model in real-time
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import numpy as np
from collections import deque

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, ScrollableContainer, Container
from textual.widgets import Header, Footer, Static, Button, Label, Input, ProgressBar
from textual.screen import Screen
from textual.reactive import reactive
from textual.message import Message
from textual import events

from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.console import Group
from rich.progress import Progress, BarColumn, TextColumn

import requests

# Import our Qwen3 learner
from qwen3_embedding_value_learner import Qwen3EmbeddingValueLearner, RankingExample


class RatingWidget(Container):
    """Custom widget for rating with buttons."""
    
    def compose(self) -> ComposeResult:
        yield Static("[bold]Rate this item:[/bold]", id="rating-prompt")
        with Horizontal(id="rating-buttons"):
            for i in range(1, 11):
                yield Button(str(i), id=f"rate-{i}", classes="rating-btn")


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
        self.user_rating = None
        self.predicted_rating = None
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


class HNRatingTUI(App):
    """TUI for rating HN items with uncertainty display."""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #item-display {
        height: 40%;
        border: solid $primary;
        margin: 1;
        padding: 2;
        background: $panel;
    }
    
    #prediction-panel {
        height: 25%;
        border: solid $secondary;
        margin: 1;
        padding: 1;
    }
    
    #rating-panel {
        height: 20%;
        border: solid $accent;
        margin: 1;
        padding: 1;
    }
    
    #stats-panel {
        dock: right;
        width: 40;
        border: solid $primary;
        margin: 1;
        padding: 1;
    }
    
    #history-panel {
        height: 50%;
        border: solid $secondary;
        padding: 1;
        overflow-y: auto;
    }
    
    .rating-btn {
        min-width: 4;
        margin: 0 1;
    }
    
    #uncertainty-bar {
        height: 3;
        margin: 1;
    }
    
    #accuracy-display {
        text-align: center;
        margin: 1;
    }
    
    ProgressBar {
        height: 1;
        margin: 1;
    }
    
    .prediction-value {
        text-align: center;
        text-style: bold;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("n", "next_item", "Next Item"),
        ("s", "save_model", "Save Model"),
        ("l", "load_model", "Load Model"),
        ("r", "refresh_predictions", "Refresh"),
        ("1", "rate_1", "Rate 1"),
        ("2", "rate_2", "Rate 2"),
        ("3", "rate_3", "Rate 3"),
        ("4", "rate_4", "Rate 4"),
        ("5", "rate_5", "Rate 5"),
        ("6", "rate_6", "Rate 6"),
        ("7", "rate_7", "Rate 7"),
        ("8", "rate_8", "Rate 8"),
        ("9", "rate_9", "Rate 9"),
        ("0", "rate_10", "Rate 10"),
    ]
    
    def __init__(self):
        super().__init__()
        self.current_item: Optional[HNItem] = None
        self.item_queue: deque[HNItem] = deque()
        self.rated_items: List[Tuple[HNItem, float]] = []
        self.rating_history: List[Dict] = []
        
        # Initialize Qwen3 learner
        self.learner = Qwen3EmbeddingValueLearner(
            embedding_dim=256,
            ridge_alpha=5.0
        )
        self.model_trained = False
        self.model_path = Path("hn_rating_model.pkl")
        
        # Metrics
        self.total_rated = 0
        self.sum_squared_error = 0.0
        self.sum_absolute_error = 0.0
        
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
                # Current item display
                with Container(id="item-display"):
                    yield Static("[bold]Current Item[/bold]", id="item-title")
                    yield Static("", id="item-content")
                
                # Prediction display
                with Container(id="prediction-panel"):
                    yield Static("[bold]Qwen3 Prediction[/bold]", id="prediction-title")
                    yield Static("No prediction yet", id="prediction-value", classes="prediction-value")
                    yield ProgressBar(total=10, id="uncertainty-bar")
                    yield Static("", id="uncertainty-text")
                
                # Rating panel
                with Container(id="rating-panel"):
                    yield RatingWidget()
                
                # Controls
                with Horizontal(id="controls"):
                    yield Button("Next Item", id="next-btn", variant="primary")
                    yield Button("Train Model", id="train-btn")
                    yield Button("Save Model", id="save-btn")
            
            # Stats panel
            with Vertical(id="stats-panel"):
                yield Static("[bold]Statistics[/bold]", id="stats-title")
                yield Static("Items rated: 0", id="rated-count")
                yield Static("Model: Not trained", id="model-status")
                yield Static("MAE: --", id="mae-display")
                yield Static("RMSE: --", id="rmse-display")
                yield ProgressBar(total=100, show_percentage=True, id="accuracy-bar")
                yield Static("", id="accuracy-display")
                
                yield Static("[bold]Recent Ratings[/bold]", id="history-title")
                with ScrollableContainer(id="history-panel"):
                    yield Static("No ratings yet", id="history-content")
    
    async def on_mount(self) -> None:
        """Initialize the app."""
        # Load sample items
        self.load_sample_items()
        
        # Show first item
        await self.show_next_item()
        
        # Update stats
        self.update_stats()
    
    def load_sample_items(self) -> None:
        """Load sample HN items."""
        sample_items = [
            HNItem(1, "Show HN: I built a real-time collaborative code editor", "", 234, "coder123", 0, 89),
            HNItem(2, "The complete guide to async/await in Python", "", 567, "pythonista", 0, 234),
            HNItem(3, "Why we're moving away from microservices", "", 890, "architect", 0, 456),
            HNItem(4, "Machine learning is not magic: A practical guide", "", 123, "mleng", 0, 67),
            HNItem(5, "Building a search engine from scratch", "", 456, "searcher", 0, 123),
            HNItem(6, "The economics of open source software", "", 789, "economist", 0, 234),
            HNItem(7, "A deep dive into database internals", "", 234, "dbexpert", 0, 89),
            HNItem(8, "WebAssembly: One year later", "", 567, "wasmfan", 0, 156),
            HNItem(9, "The art of debugging production issues", "", 345, "debugger", 0, 178),
            HNItem(10, "Rust for JavaScript developers", "", 678, "rustacean", 0, 267),
        ]
        
        self.item_queue.extend(sample_items)
    
    async def show_next_item(self) -> None:
        """Show the next item to rate."""
        if not self.item_queue:
            self.query_one("#item-content").update("[italic]No more items to rate[/italic]")
            self.current_item = None
            return
        
        self.current_item = self.item_queue.popleft()
        
        # Update display
        content = f"""[bold]{self.current_item.title}[/bold]

[dim]Posted by {self.current_item.by} | {self.current_item.score} points | {self.current_item.descendants} comments[/dim]

[italic]How would you rate the quality/interest of this item on a scale of 1-10?[/italic]"""
        
        self.query_one("#item-content").update(content)
        
        # Get prediction if model is trained
        if self.model_trained:
            await self.update_prediction()
        else:
            self.query_one("#prediction-value").update("Train model first")
    
    async def update_prediction(self) -> None:
        """Update prediction for current item."""
        if not self.current_item or not self.model_trained:
            return
        
        # Get multiple predictions for uncertainty
        predictions = []
        text = self.current_item.to_text()
        
        # Run multiple predictions with slight variations
        for i in range(10):
            # Add small noise to text for uncertainty estimation
            if i > 0:
                noise_text = text + " " * i  # Simple variation
            else:
                noise_text = text
            
            pred = self.learner.predict(noise_text)
            predictions.append(pred)
        
        # Calculate mean and uncertainty
        mean_pred = np.mean(predictions)
        std_pred = np.std(predictions) + 0.5  # Add base uncertainty
        
        self.current_item.predicted_rating = mean_pred
        self.current_item.uncertainty = std_pred
        
        # Update display
        self.query_one("#prediction-value").update(
            f"[bold cyan]{mean_pred:.1f}[/bold cyan] / 10"
        )
        
        # Update uncertainty bar
        uncertainty_bar = self.query_one("#uncertainty-bar", ProgressBar)
        uncertainty_bar.update(progress=min(std_pred * 2, 10))  # Scale uncertainty to 0-10
        
        # Update uncertainty text
        confidence = max(0, 100 - std_pred * 20)  # Convert to confidence %
        uncertainty_text = f"Confidence: {confidence:.0f}% (±{std_pred:.2f})"
        self.query_one("#uncertainty-text").update(uncertainty_text)
    
    def rate_item(self, rating: int) -> None:
        """Rate the current item."""
        if not self.current_item:
            return
        
        self.current_item.user_rating = rating
        
        # Add to training data
        self.learner.add_training_example(
            self.current_item.to_text(),
            float(rating)
        )
        
        # Track metrics if we had a prediction
        if self.current_item.predicted_rating is not None:
            error = abs(self.current_item.predicted_rating - rating)
            squared_error = error ** 2
            
            self.sum_absolute_error += error
            self.sum_squared_error += squared_error
            self.total_rated += 1
            
            # Add to history
            self.rating_history.append({
                'title': self.current_item.title[:40] + "...",
                'predicted': self.current_item.predicted_rating,
                'actual': rating,
                'error': error
            })
        
        # Save rated item
        self.rated_items.append((self.current_item, rating))
        
        # Update displays
        self.update_stats()
        self.update_history()
        
        # Auto-train after every 5 ratings
        if len(self.rated_items) % 5 == 0 and len(self.rated_items) >= 5:
            self.action_train_model()
        
        # Show next item
        asyncio.create_task(self.show_next_item())
    
    def update_stats(self) -> None:
        """Update statistics display."""
        # Update counts
        self.query_one("#rated-count").update(f"Items rated: {len(self.rated_items)}")
        
        # Update model status
        status = "Trained" if self.model_trained else "Not trained"
        if self.model_trained and hasattr(self.learner, 'training_texts'):
            status += f" ({len(self.learner.training_texts)} examples)"
        self.query_one("#model-status").update(f"Model: {status}")
        
        # Update error metrics
        if self.total_rated > 0:
            mae = self.sum_absolute_error / self.total_rated
            rmse = np.sqrt(self.sum_squared_error / self.total_rated)
            
            self.query_one("#mae-display").update(f"MAE: {mae:.2f}")
            self.query_one("#rmse-display").update(f"RMSE: {rmse:.2f}")
            
            # Update accuracy bar (10 - MAE) / 10 * 100
            accuracy = max(0, (10 - mae) / 10 * 100)
            accuracy_bar = self.query_one("#accuracy-bar", ProgressBar)
            accuracy_bar.update(progress=accuracy)
            
            self.query_one("#accuracy-display").update(
                f"Accuracy: {accuracy:.1f}%"
            )
        else:
            self.query_one("#mae-display").update("MAE: --")
            self.query_one("#rmse-display").update("RMSE: --")
    
    def update_history(self) -> None:
        """Update rating history display."""
        if not self.rating_history:
            return
        
        # Show last 10 ratings
        history_lines = []
        for item in self.rating_history[-10:]:
            pred = item['predicted']
            actual = item['actual']
            error = item['error']
            
            # Color code based on error
            if error < 1.0:
                color = "green"
            elif error < 2.0:
                color = "yellow"
            else:
                color = "red"
            
            line = f"[{color}]P:{pred:.1f} A:{actual} E:{error:.1f}[/{color}] {item['title']}"
            history_lines.append(line)
        
        history_content = "\n".join(reversed(history_lines))
        self.query_one("#history-content").update(history_content)
    
    @on(Button.Pressed)
    def handle_button(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        
        if button_id == "next-btn":
            asyncio.create_task(self.show_next_item())
        elif button_id == "train-btn":
            self.action_train_model()
        elif button_id == "save-btn":
            self.action_save_model()
        elif button_id.startswith("rate-"):
            rating = int(button_id.split("-")[1])
            self.rate_item(rating)
    
    def action_train_model(self) -> None:
        """Train the model."""
        if len(self.rated_items) < 3:
            self.log("Need at least 3 ratings to train")
            return
        
        try:
            # Train model
            metrics = self.learner.train(validation_split=0.3)
            self.model_trained = True
            
            self.log(f"Model trained! Val R²: {metrics['val_r2']:.3f}")
            self.update_stats()
            
            # Update prediction for current item
            if self.current_item:
                asyncio.create_task(self.update_prediction())
            
        except Exception as e:
            self.log(f"Training failed: {str(e)}")
    
    def action_save_model(self) -> None:
        """Save the model."""
        if not self.model_trained:
            self.log("No model to save")
            return
        
        try:
            self.learner.save_model(str(self.model_path))
            self.log("Model saved successfully")
        except Exception as e:
            self.log(f"Save failed: {str(e)}")
    
    def action_load_model(self) -> None:
        """Load a saved model."""
        try:
            self.learner.load_model(str(self.model_path))
            self.model_trained = True
            self.log("Model loaded successfully")
            self.update_stats()
            
            if self.current_item:
                asyncio.create_task(self.update_prediction())
        except Exception as e:
            self.log(f"Load failed: {str(e)}")
    
    def action_next_item(self) -> None:
        """Skip to next item."""
        asyncio.create_task(self.show_next_item())
    
    # Quick rating actions
    def action_rate_1(self) -> None:
        self.rate_item(1)
    
    def action_rate_2(self) -> None:
        self.rate_item(2)
    
    def action_rate_3(self) -> None:
        self.rate_item(3)
    
    def action_rate_4(self) -> None:
        self.rate_item(4)
    
    def action_rate_5(self) -> None:
        self.rate_item(5)
    
    def action_rate_6(self) -> None:
        self.rate_item(6)
    
    def action_rate_7(self) -> None:
        self.rate_item(7)
    
    def action_rate_8(self) -> None:
        self.rate_item(8)
    
    def action_rate_9(self) -> None:
        self.rate_item(9)
    
    def action_rate_10(self) -> None:
        self.rate_item(10)
    
    def log(self, message: str) -> None:
        """Log a message to the footer."""
        self.notify(message, timeout=3)


if __name__ == "__main__":
    app = HNRatingTUI()
    app.run()