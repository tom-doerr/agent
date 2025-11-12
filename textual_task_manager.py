from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Button, Input, ListView, ListItem, Label
from textual.screen import ModalScreen
from textual.reactive import reactive
from textual import events
import os
import json
import threading
from datetime import datetime

TASKS_FILE = "tasks.json"

class HelpScreen(ModalScreen):
    """Help screen with key bindings."""
    CSS = """
    HelpScreen {
        align: center middle;
    }
    #help-dialog {
        width: 60;
        height: 24;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }
    #help-title {
        text-align: center;
        width: 100%;
        padding: 1;
        text-style: bold;
    }
    #help-content {
        width: 100%;
        height: 1fr;
    }
    #close-button {
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="help-dialog"):
            yield Label("Task Manager Help", id="help-title")
            with Container(id="help-content"):
                yield Label("Key bindings:")
                yield Label("  ?: Toggle help")
                yield Label("  Esc: Exit")
                yield Label("  Ctrl+S: Save")
                yield Label("  Delete: Delete selected task")
                yield Label("  Space: Toggle completion of selected task")
                yield Label("  Arrow keys: Navigate tasks")
            yield Button("Close", id="close-button", variant="primary")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-button":
            self.dismiss()

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
    #list-header {
        text-align: center;
        padding: 1;
        border-bottom: solid $accent;
        background: $surface-lighten-1;
    }
    #task-list {
        height: 66%;
        border: solid $accent;
        padding: 1;
        overflow-y: auto;
    }
    #input-container {
        height: 15%;
        border: solid $accent;
        padding: 1;
        layout: horizontal;
    }
    #new-task-input {
        width: 80%;
    }
    #mic-button {
        width: 20%;
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
            yield Label(id="list-header")
            yield ListView(id="task-list")
            with Container(id="input-container"):
                yield Input(placeholder="Add new task...", id="new-task-input")
                yield Button("🎤", id="mic-button", classes="mic-button")
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
            header_text = f"All Tasks ({len(self.tasks)})"
        elif self.current_filter == "active":
            filtered_tasks = [t for t in self.tasks if not t.completed]
            header_text = f"Active Tasks ({len(filtered_tasks)})"
        elif self.current_filter == "completed":
            filtered_tasks = [t for t in self.tasks if t.completed]
            header_text = f"Completed Tasks ({len(filtered_tasks)})"
        
        for task in filtered_tasks:
            task_list.append(task)
        
        self.query_one("#list-header").update(header_text)
    
    def update_button_labels(self) -> None:
        all_count = len(self.tasks)
        active_count = len([t for t in self.tasks if not t.completed])
        completed_count = len([t for t in self.tasks if t.completed])
        
        self.query_one("#filter-all").label = f"All ({all_count})"
        self.query_one("#filter-active").label = f"Active ({active_count})"
        self.query_one("#filter-completed").label = f"Completed ({completed_count})"
    
    def toggle_selected_task(self) -> None:
        task_list = self.query_one("#task-list")
        if task_list.index is not None:
            selected_task = task_list.children[task_list.index]
            if selected_task in self.tasks:
                selected_task.completed = not selected_task.completed
                self.save_tasks()
                self.update_list()
                self.update_button_labels()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "new-task-input" and event.value.strip():
            new_task = TaskItem(event.value.strip())
            self.tasks.append(new_task)
            self.save_tasks()
            self.update_list()
            self.update_button_labels()
            event.input.value = ""
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self.toggle_selected_task()
    
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
        elif event.button.id == "mic-button":
            self._record_voice()
        self.update_list()
    
    def _record_voice(self) -> None:
        if not self.recognizer:
            return
            
        def record_thread():
            try:
                if not self.recognizer or not self.sr:
                    return
                with self.sr.Microphone() as source:
                    audio = self.recognizer.listen(source, timeout=5)
                    text = self.recognizer.recognize_google(audio)
                    self.call_from_thread(self._set_input_text, text)
            except Exception as e:
                self.call_from_thread(self._show_error, f"Voice error: {str(e)}")
        
        threading.Thread(target=record_thread, daemon=True).start()
    
    def _set_input_text(self, text: str) -> None:
        input_field = self.query_one("#new-task-input")
        input_field.value = text
        self.set_focus(input_field)
    
    def _show_error(self, message: str) -> None:
        self.notify(message, title="Voice Error", severity="error")
    
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
        elif event.key == "question_mark":
            self.push_screen(HelpScreen())
        elif event.key == "space":
            self.toggle_selected_task()

if __name__ == "__main__":
    app = TaskManager()
    app.run()
