from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Button, Static, Input, ListView, ListItem, Label
from textual.reactive import reactive
from textual import events
import os
import json
from datetime import datetime

TASKS_FILE = "tasks.json"

class TaskItem(ListItem):
    def __init__(self, task_text, completed=False, created_at=None, **kwargs):
        super().__init__(**kwargs)
        self.task_text = task_text
        self.completed = completed
        self.created_at = created_at or datetime.now().isoformat()
        
    def compose(self) -> ComposeResult:
        yield Label(f"[{'x' if self.completed else ' '}] {self.task_text}")

class TaskManager(App):
    CSS = """
    Screen {
        layout: vertical;
    }
    #task-list {
        height: 70%;
        border: solid $accent;
        padding: 1;
        overflow-y: auto;
    }
    #input-container {
        height: 15%;
        border: solid $accent;
        padding: 1;
    }
    #controls {
        height: 15%;
        layout: grid;
        grid-size: 4;
        grid-columns: 1fr 1fr 1fr 1fr;
        padding: 1;
    }
    ListItem {
        height: auto;
        padding: 1;
    }
    ListItem:hover {
        background: $accent 10%;
    }
    .delete-button {
        width: auto;
        min-width: 8;
    }
    """
    
    tasks = reactive([])
    current_filter = reactive("all")
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main-container"):
            yield ListView(id="task-list")
            with Container(id="input-container"):
                yield Input(placeholder="Add new task...", id="new-task-input")
            with Container(id="controls"):
                yield Button("All", id="filter-all")
                yield Button("Active", id="filter-active")
                yield Button("Completed", id="filter-completed")
                yield Button("Clear Completed", id="clear-completed", classes="delete-button")
        yield Footer()
    
    def on_mount(self) -> None:
        self.load_tasks()
        self.update_list()
        self.query_one("#new-task-input").focus()
        self.update_button_labels()
    
    def load_tasks(self) -> None:
        if os.path.exists(TASKS_FILE):
            try:
                with open(TASKS_FILE, "r") as f:
                    data = json.load(f)
                    self.tasks = [
                        TaskItem(
                            task_text=task['text'],
                            completed=task['completed'],
                            created_at=task['created_at']
                        ) for task in data
                    ]
            except Exception:
                self.tasks = []
    
    def save_tasks(self) -> None:
        with open(TASKS_FILE, "w") as f:
            json.dump([
                {
                    'text': task.task_text,
                    'completed': task.completed,
                    'created_at': task.created_at
                } for task in self.tasks
            ], f)
    
    def update_list(self) -> None:
        task_list = self.query_one("#task-list")
        task_list.clear()
        
        filtered_tasks = []
        if self.current_filter == "all":
            filtered_tasks = self.tasks
        elif self.current_filter == "active":
            filtered_tasks = [t for t in self.tasks if not t.completed]
        elif self.current_filter == "completed":
            filtered_tasks = [t for t in self.tasks if t.completed]
        
        for task in filtered_tasks:
            task_list.append(task)
    
    def update_button_labels(self) -> None:
        all_count = len(self.tasks)
        active_count = len([t for t in self.tasks if not t.completed])
        completed_count = len([t for t in self.tasks if t.completed])
        
        self.query_one("#filter-all").label = f"All ({all_count})"
        self.query_one("#filter-active").label = f"Active ({active_count})"
        self.query_one("#filter-completed").label = f"Completed ({completed_count})"
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "new-task-input" and event.value.strip():
            new_task = TaskItem(event.value.strip())
            self.tasks.append(new_task)
            self.save_tasks()
            self.update_list()
            self.update_button_labels()
            event.input.value = ""
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        task = event.item
        task.completed = not task.completed
        self.save_tasks()
        self.update_list()
        self.update_button_labels()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "filter-all":
            self.current_filter = "all"
        elif event.button.id == "filter-active":
            self.current_filter = "active"
        elif event.button.id == "filter-completed":
            self.current_filter = "completed"
        elif event.button.id == "clear-completed":
            # Remove completed tasks
            self.tasks = [t for t in self.tasks if not t.completed]
            self.save_tasks()
            self.update_list()
            self.update_button_labels()
        self.update_list()
    
    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.exit()
        elif event.key == "ctrl+s":
            self.save_tasks()
        elif event.key == "delete":
            # Delete selected task
            task_list = self.query_one("#task-list")
            if task_list.index is not None:
                selected_task = task_list.children[task_list.index]
                if selected_task in self.tasks:
                    self.tasks.remove(selected_task)
                    self.save_tasks()
                    self.update_list()
                    self.update_button_labels()

if __name__ == "__main__":
    app = TaskManager()
    app.run()
