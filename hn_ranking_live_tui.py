#!/usr/bin/env python3
"""
Live Textual TUI for ranking Hacker News items with real API data.

Combines the ranking TUI with live HN data fetching.
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import pickle
import time

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Static, Button, Label, ListItem, ListView, LoadingIndicator
from textual.screen import Screen
from textual.reactive import reactive
from textual.message import Message

from rich.text import Text
from rich.panel import Panel
from rich.table import Table

import numpy as np

# Import our modules
from qwen3_embedding_value_learner import Qwen3EmbeddingValueLearner, RankingExample
from hn_api_client import HNAPIClient, HNStory
from hn_ranking_tui import InsertionDialog


class HNRankingLiveTUI(App):
    """Live TUI for ranking HN items with real data."""
    
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
        width: 35;
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
    
    LoadingIndicator {
        height: 3;
    }
    
    #loading-panel {
        height: 5;
        margin: 1;
        align: center middle;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh_hn", "Refresh HN"),
        ("f", "fetch_candidates", "Fetch New"),
        ("s", "save", "Save Model"),
        ("l", "load", "Load Model"),
        ("t", "train", "Train Model"),
        ("u", "update_predictions", "Update Predictions"),
    ]
    
    def __init__(self):
        super().__init__()
        self.top_items: List[HNStory] = []
        self.candidate_items: List[HNStory] = []
        self.rejected_ids = set()
        self.seen_ids = set()
        self.training_data = []
        
        # Initialize API client
        self.hn_client = HNAPIClient(max_concurrent=20)
        
        # Initialize Qwen3 learner
        self.learner = Qwen3EmbeddingValueLearner(
            embedding_dim=384,  # Larger for real data
            ridge_alpha=10.0
        )
        self.model_trained = False
        self.model_path = Path("hn_live_ranking_model.pkl")
        
        # Try to load existing model
        if self.model_path.exists():
            try:
                self.learner.load_model(str(self.model_path))
                self.model_trained = True
                self.log("Loaded existing model")
            except:
                self.log("Failed to load model")
        
        # Load top 10 if exists
        self.top_10_path = Path("hn_live_top_10.json")
        self.last_refresh = None
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        
        with Horizontal():
            with Vertical():
                yield Static("[bold]Your Top 10 Items[/bold]", id="top-title")
                yield ListView(id="top-list")
                
                yield Static("[bold]Candidates (Predicted Top 10)[/bold]", id="candidate-title")
                with Vertical(id="loading-panel"):
                    yield LoadingIndicator(id="loading")
                yield ListView(id="candidate-panel")
                
                with Horizontal(id="controls"):
                    yield Button("Train Model", id="train-btn", variant="primary")
                    yield Button("Refresh HN", id="refresh-btn")
                    yield Button("Fetch More", id="fetch-btn")
            
            with Vertical(id="stats"):
                yield Static("[bold]Stats[/bold]")
                yield Static("Model: Not trained", id="model-status")
                yield Static("Training examples: 0", id="training-count")
                yield Static("Rejected items: 0", id="rejected-count")
                yield Static("Last refresh: Never", id="last-refresh")
                yield Static("", id="last-action")
                yield Static("\n[bold]Top Sources:[/bold]", id="sources-title")
                yield Static("Loading...", id="top-sources")
    
    async def on_mount(self) -> None:
        """Initialize the app."""
        # Hide loading initially
        self.query_one("#loading").display = False
        
        # Load saved top 10 or fetch from HN
        await self.load_or_fetch_top_items()
        self.update_stats()
        
        # Start background refresh
        self.set_interval(300, self.auto_refresh)  # Every 5 minutes
    
    async def load_or_fetch_top_items(self) -> None:
        """Load saved top 10 or fetch from HN."""
        if self.top_10_path.exists():
            # Load saved
            with open(self.top_10_path) as f:
                data = json.load(f)
                self.top_items = [
                    HNStory(**item) for item in data['items']
                ]
                self.last_refresh = datetime.fromisoformat(data.get('updated', ''))
                
            # Update seen IDs
            self.seen_ids.update(item.id for item in self.top_items)
            
        else:
            # Fetch from HN
            await self.fetch_initial_top_10()
        
        self.refresh_top_list()
    
    async def fetch_initial_top_10(self) -> None:
        """Fetch initial top 10 from HN."""
        self.show_loading(True)
        self.log("Fetching top stories from HN...")
        
        try:
            stories = await self.hn_client.fetch_top_stories(30)
            
            # Filter and take top 10
            filtered = []
            for story in stories:
                # Basic quality filter
                if story.score > 50 and len(story.title) > 10:
                    filtered.append(story)
                    if len(filtered) >= 10:
                        break
            
            self.top_items = filtered
            self.seen_ids.update(item.id for item in self.top_items)
            self.save_top_items()
            
            self.log(f"Loaded {len(self.top_items)} top stories")
            
        except Exception as e:
            self.log(f"Error fetching stories: {e}")
        finally:
            self.show_loading(False)
            self.refresh_top_list()
    
    def refresh_top_list(self) -> None:
        """Refresh the top 10 display."""
        list_view = self.query_one("#top-list", ListView)
        list_view.clear()
        
        for i, item in enumerate(self.top_items):
            age_str = f"{item.age_hours():.1f}h" if item.age_hours() < 24 else f"{item.age_hours()/24:.1f}d"
            
            text = f"{i+1}. [{item.score}pts] {item.title[:60]}{'...' if len(item.title) > 60 else ''}\n"
            text += f"    [dim]by {item.by} | {item.descendants} comments | {age_str} ago[/dim]"
            
            list_item = ListItem(Static(text))
            list_view.append(list_item)
    
    def refresh_candidate_list(self) -> None:
        """Refresh the candidate items display."""
        list_view = self.query_one("#candidate-panel", ListView)
        list_view.clear()
        
        for item in self.candidate_items[:5]:  # Show top 5 candidates
            if hasattr(item, 'predicted_value'):
                pred_str = f"[Pred: {item.predicted_value:.1f}±{item.uncertainty:.1f}]"
            else:
                pred_str = "[No prediction]"
                
            text = f"{pred_str} [{item.score}pts] {item.title[:50]}..."
            
            list_item = ListItem(
                Static(text),
                id=f"candidate-{item.id}"
            )
            list_view.append(list_item)
    
    async def check_new_candidates(self, stories: List[HNStory]) -> None:
        """Check which stories might belong in top 10."""
        if not self.model_trained:
            self.log("Train model first to see candidates")
            return
        
        # Filter out seen and rejected
        new_stories = [
            s for s in stories 
            if s.id not in self.seen_ids and s.id not in self.rejected_ids
        ]
        
        if not new_stories:
            self.log("No new stories to evaluate")
            return
        
        # Get minimum score in current top 10
        min_top_10_value = min(
            self.learner.predict(item.to_text()) 
            for item in self.top_items
        )
        
        # Evaluate new stories
        candidates = []
        for story in new_stories:
            # Get prediction with uncertainty
            predictions = []
            base_text = story.to_text()
            
            for i in range(5):
                # Add variation for uncertainty
                if i > 0:
                    text = base_text + f" [eval {i}]"
                else:
                    text = base_text
                    
                pred = self.learner.predict(text)
                predictions.append(pred)
            
            story.predicted_value = np.mean(predictions)
            story.uncertainty = np.std(predictions) + 0.5
            
            # Only include if predicted to be competitive
            if story.predicted_value > min_top_10_value * 0.85:  # 85% threshold
                candidates.append(story)
        
        # Sort by predicted value
        candidates.sort(key=lambda x: x.predicted_value, reverse=True)
        
        # Update candidates
        self.candidate_items = candidates
        self.refresh_candidate_list()
        
        if candidates:
            self.log(f"Found {len(candidates)} potential top 10 items")
        else:
            self.log("No items qualify for top 10")
    
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
                # Convert HNStory to HNItem for dialog
                from hn_ranking_tui import HNItem
                hn_item = HNItem(
                    id=selected_item.id,
                    title=selected_item.title,
                    url=selected_item.url,
                    score=selected_item.score,
                    by=selected_item.by,
                    time=selected_item.time,
                    descendants=selected_item.descendants
                )
                
                # Convert top items too
                top_hn_items = [
                    HNItem(
                        id=item.id,
                        title=item.title,
                        url=item.url,
                        score=item.score,
                        by=item.by,
                        time=item.time,
                        descendants=item.descendants
                    )
                    for item in self.top_items
                ]
                
                # Show insertion dialog
                def handle_result(result):
                    if result:
                        action, position = result
                        if action == "insert":
                            self.insert_item_at_position(selected_item, position)
                        elif action == "reject":
                            self.reject_item(selected_item)
                
                self.push_screen(
                    InsertionDialog(hn_item, top_hn_items),
                    handle_result
                )
    
    def insert_item_at_position(self, item: HNStory, position: int) -> None:
        """Insert item at specified position in top 10."""
        # Add to training data
        self.add_training_example(item, position)
        
        # Insert into top 10
        self.top_items.insert(position - 1, item)
        
        # Remove last item if we now have 11
        if len(self.top_items) > 10:
            removed = self.top_items.pop()
            self.log(f"Removed: {removed.title[:30]}...")
        
        # Update seen IDs
        self.seen_ids.add(item.id)
        
        # Remove from candidates
        self.candidate_items = [c for c in self.candidate_items if c.id != item.id]
        
        # Refresh displays
        self.refresh_top_list()
        self.refresh_candidate_list()
        self.save_top_items()
        
        self.log(f"Inserted at #{position}: {item.title[:30]}...")
        self.update_stats()
    
    def reject_item(self, item: HNStory) -> None:
        """Reject item as not belonging in top 10."""
        self.rejected_ids.add(item.id)
        
        # Add negative training example
        self.add_training_example(item, -1)
        
        # Remove from candidates
        self.candidate_items = [c for c in self.candidate_items if c.id != item.id]
        self.refresh_candidate_list()
        
        self.log(f"Rejected: {item.title[:30]}...")
        self.update_stats()
    
    def add_training_example(self, item: HNStory, position: int) -> None:
        """Add training example based on user action."""
        # Calculate score based on position
        if position == -1:  # Rejected
            score = 0.0
        else:
            # Higher score for higher positions
            score = 11.0 - position
        
        self.training_data.append((item.to_text(), score))
        
        # Also add current top 10 as positive examples
        for i, top_item in enumerate(self.top_items):
            if top_item.id != item.id:
                self.training_data.append((top_item.to_text(), 10.0 - i))
    
    def save_top_items(self) -> None:
        """Save current top 10 to file."""
        data = {
            'items': [item.to_dict() for item in self.top_items],
            'updated': datetime.now().isoformat()
        }
        
        with open(self.top_10_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def show_loading(self, show: bool) -> None:
        """Show/hide loading indicator."""
        self.query_one("#loading").display = show
    
    def update_stats(self) -> None:
        """Update statistics display."""
        # Model status
        status = "Trained" if self.model_trained else "Not trained"
        self.query_one("#model-status").update(f"Model: {status}")
        
        # Counts
        self.query_one("#training-count").update(f"Training examples: {len(self.training_data)}")
        self.query_one("#rejected-count").update(f"Rejected items: {len(self.rejected_ids)}")
        
        # Last refresh
        if self.last_refresh:
            mins_ago = (datetime.now() - self.last_refresh).seconds // 60
            self.query_one("#last-refresh").update(f"Last refresh: {mins_ago}m ago")
        
        # Top sources
        if self.top_items:
            sources = {}
            for item in self.top_items:
                domain = item.url.split('/')[2] if item.url and '//' in item.url else 'self'
                sources[domain] = sources.get(domain, 0) + 1
            
            top_sources = sorted(sources.items(), key=lambda x: x[1], reverse=True)[:3]
            source_text = "\n".join([f"{domain}: {count}" for domain, count in top_sources])
            self.query_one("#top-sources").update(source_text)
    
    def log(self, message: str) -> None:
        """Log an action."""
        try:
            self.query_one("#last-action").update(message)
        except:
            # Fallback if widget not ready
            pass
    
    async def action_train(self) -> None:
        """Train the model with current data."""
        if len(self.training_data) < 5:
            self.log("Need at least 5 examples to train")
            return
        
        self.log("Training model...")
        
        # Clear and add training examples
        self.learner.training_texts = []
        self.learner.training_scores = []
        
        for text, score in self.training_data:
            self.learner.add_training_example(text, score)
        
        try:
            metrics = self.learner.train(validation_split=0.2)
            self.model_trained = True
            self.log(f"Trained! Val R²: {metrics['val_r2']:.3f}")
            self.update_stats()
            
            # Update predictions for existing candidates
            await self.action_update_predictions()
            
        except Exception as e:
            self.log(f"Training failed: {str(e)}")
    
    async def action_refresh_hn(self) -> None:
        """Refresh from Hacker News."""
        self.show_loading(True)
        self.log("Fetching latest from HN...")
        
        try:
            # Fetch different types of stories
            top_task = self.hn_client.fetch_top_stories(20)
            new_task = self.hn_client.fetch_new_stories(20)
            best_task = self.hn_client.fetch_best_stories(10)
            
            top_stories, new_stories, best_stories = await asyncio.gather(
                top_task, new_task, best_task
            )
            
            all_stories = top_stories + new_stories + best_stories
            
            # Remove duplicates
            seen = set()
            unique_stories = []
            for story in all_stories:
                if story.id not in seen:
                    seen.add(story.id)
                    unique_stories.append(story)
            
            self.last_refresh = datetime.now()
            self.log(f"Fetched {len(unique_stories)} unique stories")
            
            # Check for candidates if model is trained
            if self.model_trained:
                await self.check_new_candidates(unique_stories)
            
        except Exception as e:
            self.log(f"Error refreshing: {e}")
        finally:
            self.show_loading(False)
            self.update_stats()
    
    async def action_fetch_candidates(self) -> None:
        """Fetch more candidate stories."""
        await self.action_refresh_hn()
    
    async def action_update_predictions(self) -> None:
        """Update predictions for current candidates."""
        if not self.model_trained:
            self.log("No model to update predictions")
            return
        
        if not self.candidate_items:
            self.log("No candidates to update")
            return
        
        self.log("Updating predictions...")
        
        # Re-evaluate all candidates
        for story in self.candidate_items:
            predictions = []
            base_text = story.to_text()
            
            for i in range(5):
                text = base_text + (f" [eval {i}]" if i > 0 else "")
                pred = self.learner.predict(text)
                predictions.append(pred)
            
            story.predicted_value = np.mean(predictions)
            story.uncertainty = np.std(predictions) + 0.5
        
        # Re-sort by predicted value
        self.candidate_items.sort(key=lambda x: x.predicted_value, reverse=True)
        self.refresh_candidate_list()
        
        self.log("Predictions updated")
    
    async def auto_refresh(self) -> None:
        """Auto-refresh candidates periodically."""
        if self.model_trained:
            await self.action_refresh_hn()
    
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
            
            # Fetch and check candidates
            await self.action_refresh_hn()
            
        except Exception as e:
            self.log(f"Load failed: {str(e)}")


if __name__ == "__main__":
    app = HNRankingLiveTUI()
    app.run()