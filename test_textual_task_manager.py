import pytest
from textual import events
from textual_task_manager import TaskManager, TASKS_FILE
from textual.widgets import ListView, Input, Button
import os
import json

@pytest.fixture
def app(tmp_path):
    # Override TASKS_FILE to use temporary directory
    global TASKS_FILE
    TASKS_FILE = str(tmp_path / "tasks.json")
    app = TaskManager()
    return app

def test_add_task(app):
    """Test adding a new task"""
    app.tasks = []
    app.on_input_submitted(Input.Submitted(Input(), "New task"))
    assert len(app.tasks) == 1
    assert app.tasks[0].task_text == "New task"
    assert not app.tasks[0].completed

def test_toggle_task(app):
    """Test toggling task completion"""
    app.tasks = [app.TaskItem("Test task")]
    app.query_one("#task-list").index = 0
    app.toggle_selected_task()
    assert app.tasks[0].completed
    app.toggle_selected_task()
    assert not app.tasks[0].completed

def test_delete_task(app):
    """Test deleting a task"""
    app.tasks = [app.TaskItem("Task to delete")]
    app.query_one("#task-list").index = 0
    app.on_key(events.Key("delete"))
    assert len(app.tasks) == 0

def test_clear_completed(app):
    """Test clearing completed tasks"""
    app.tasks = [
        app.TaskItem("Active task", completed=False),
        app.TaskItem("Completed task", completed=True)
    ]
    app.query_one("#clear-completed").press()
    assert len(app.tasks) == 1
    assert app.tasks[0].task_text == "Active task"

def test_save_load_tasks(app, tmp_path):
    """Test saving and loading tasks"""
    app.tasks = [
        app.TaskItem("Task 1", completed=True),
        app.TaskItem("Task 2", completed=False)
    ]
    app.save_tasks()
    
    # Create new app instance to test loading
    app2 = TaskManager()
    app2.load_tasks()
    assert len(app2.tasks) == 2
    assert app2.tasks[0].task_text == "Task 1"
    assert app2.tasks[0].completed
    assert app2.tasks[1].task_text == "Task 2"
    assert not app2.tasks[1].completed

def test_filter_tasks(app):
    """Test task filtering"""
    app.tasks = [
        app.TaskItem("Active 1", completed=False),
        app.TaskItem("Completed 1", completed=True),
        app.TaskItem("Active 2", completed=False)
    ]
    
    # Test all filter
    app.current_filter = "all"
    app.update_list()
    assert len(app.query_one("#task-list").children) == 3
    
    # Test active filter
    app.current_filter = "active"
    app.update_list()
    assert len(app.query_one("#task-list").children) == 2
    
    # Test completed filter
    app.current_filter = "completed"
    app.update_list()
    assert len(app.query_one("#task-list").children) == 1

def test_button_labels_update(app):
    """Test button label updates"""
    app.tasks = [
        app.TaskItem("Task 1", completed=True),
        app.TaskItem("Task 2", completed=False)
    ]
    app.update_button_labels()
    assert app.query_one("#filter-all").label == "All (2)"
    assert app.query_one("#filter-active").label == "Active (1)"
    assert app.query_one("#filter-completed").label == "Completed (1)"
