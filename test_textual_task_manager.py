import pytest
import asyncio
from textual import events
from textual_task_manager import TaskManager, TASKS_FILE, TaskItem
from textual.widgets import ListView, Input, Button, Label
import os
import json

# Mark all tests in this file as asyncio tests
pytestmark = pytest.mark.asyncio

@pytest.fixture
async def pilot(tmp_path):
    # Override TASKS_FILE to use temporary directory
    global TASKS_FILE
    TASKS_FILE = str(tmp_path / "tasks.json")
    app = TaskManager()
    async with app.run_test() as pilot:
        yield pilot

async def test_add_task(pilot):
    """Test adding a new task"""
    app = pilot.app
    app.tasks = []
    # Simulate input submission
    input_widget = app.query_one("#new-task-input", Input)
    input_widget.value = "New task"
    app.on_input_submitted(Input.Submitted(input_widget))
    assert len(app.tasks) == 1
    assert app.tasks[0].task_text == "New task"
    assert not app.tasks[0].completed

def test_toggle_task(app):
    """Test toggling task completion"""
    app.tasks = [TaskItem("Test task")]
    app.query_one("#task-list").index = 0
    app.toggle_selected_task()
    assert app.tasks[0].completed
    app.toggle_selected_task()
    assert not app.tasks[0].completed

async def test_delete_task(pilot):
    """Test deleting a task"""
    app = pilot.app
    app.tasks = [TaskItem("Task to delete")]
    app.query_one("#task-list").index = 0
    app.on_key(events.Key("delete"))
    assert len(app.tasks) == 0

async def test_clear_completed(pilot):
    """Test clearing completed tasks"""
    app = pilot.app
    app.tasks = [
        TaskItem("Active task", completed=False),
        TaskItem("Completed task", completed=True)
    ]
    app.query_one("#clear-completed").press()
    assert len(app.tasks) == 1
    assert app.tasks[0].task_text == "Active task"

async def test_save_load_tasks(tmp_path):
    """Test saving and loading tasks"""
    # Create first app instance to save tasks
    async with TaskManager().run_test() as app1:
        app1.tasks = [
            TaskItem("Task 1", completed=True),
            TaskItem("Task 2", completed=False)
        ]
        app1.save_tasks()
    
    # Create second app instance to test loading
    async with TaskManager().run_test() as app2:
        global TASKS_FILE
        TASKS_FILE = str(tmp_path / "tasks.json")
        app2.load_tasks()
        assert len(app2.tasks) == 2
        assert app2.tasks[0].task_text == "Task 1"
        assert app2.tasks[0].completed
        assert app2.tasks[1].task_text == "Task 2"
        assert not app2.tasks[1].completed

async def test_filter_tasks(pilot):
    """Test task filtering"""
    app = pilot.app
    app.tasks = [
        TaskItem("Active 1", completed=False),
        TaskItem("Completed 1", completed=True),
        TaskItem("Active 2", completed=False)
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

test_textual_task_manager.py
```python
<<<<<<< SEARCH
    app.update_list()
    assert len(app.query_one("#task-list").children) == 1

async def test_list_header(pilot):
    """Test that the task list header shows correct filter and count"""
    app = pilot.app
    app.tasks = [
        TaskItem("Active 1", completed=False),
        TaskItem("Completed 1", completed=True),
        TaskItem("Active 2", completed=False)
    ]
    
    # Test all filter
    app.current_filter = "all"
    app.update_list()
    assert app.query_one("#list-header").renderable == "All Tasks (3)"
    
    # Test active filter
    app.current_filter = "active"
    app.update_list()
    assert app.query_one("#list-header").renderable == "Active Tasks (2)"
    
    # Test completed filter
    app.current_filter = "completed"
    app.update_list()
    assert app.query_one("#list-header").renderable == "Completed Tasks (1)"
    
    # Test after toggling task
    app.query_one("#task-list").index = 0
    app.toggle_selected_task()
    app.update_list()
    assert app.query_one("#list-header").renderable == "Completed Tasks (2)"
    
    # Test after deleting task
    app.query_one("#task-list").index = 0
    app.on_key(events.Key("delete"))
    app.update_list()
    assert app.query_one("#list-header").renderable == "Completed Tasks (1)"
    
async def test_initial_empty_state(pilot):
    """Test that the app handles empty state correctly"""
    app = pilot.app
    app.tasks = []
    app.update_list()
    app.update_button_labels()
    
    # Verify counts are zero
    assert app.query_one("#filter-all").label == "All (0)"
    assert app.query_one("#filter-active").label == "Active (0)"
    assert app.query_one("#filter-completed").label == "Completed (0)"
    
    # Verify header shows zero tasks
    assert app.query_one("#list-header").renderable == "All Tasks (0)"
    
    # Verify list is empty
    assert len(app.query_one("#task-list").children) == 0

async def test_task_editing(pilot):
    """Test that tasks can be edited by deleting and re-adding"""
    app = pilot.app
    # Add task
    input_widget = app.query_one("#new-task-input", Input)
    input_widget.value = "Original task"
    app.on_input_submitted(Input.Submitted(input_widget))
    assert len(app.tasks) == 1
    original_task = app.tasks[0]
    
    # Delete task
    app.query_one("#task-list").index = 0
    app.on_key(events.Key("delete"))
    assert len(app.tasks) == 0
    
    # Add modified task
    input_widget.value = "Modified task"
    app.on_input_submitted(Input.Submitted(input_widget))
    assert len(app.tasks) == 1
    assert app.tasks[0].task_text == "Modified task"
>>>>>>> REP极浣尝Last set of test changes:

test_textual_task_manager.py
```python
<<<<<<< SEARCH
def test_task_duplication(app):
    """Test that duplicate tasks are handled correctly"""
    # Add first task
    app.on_input_submitted(Input.Submitted(Input(), "Duplicate task"))
    assert len(app.tasks) == 1
    
    # Add duplicate task
    app.on_input_submitted(Input.Submitted(Input(), "Duplicate task"))
    assert len(app.tasks) == 2
    
    # Verify both tasks exist
    assert app.tasks[0].task_text == "Duplicate task"
    assert app.tasks[1].task_text == "Duplicate task"

def test_task_duplication(app):
    """Test that duplicate tasks are handled correctly"""
    # Add first task
    app.on_input_submitted(Input.Submitted(Input(), "Duplicate task"))
    assert len(app.tasks) == 1
    
    # Add duplicate task
    app.on_input_submitted(Input.Submitted(Input(), "Duplicate task"))
    assert len(app.tasks) == 2
    
    # Verify both tasks exist
    assert app.tasks[0].task_text == "Duplicate task"
    assert app.tasks[1].task_text == "Duplicate task"

async def极浣尝The final test changes:

test_textual_task_manager:

test_textual_task_manager.py
```python
<<<<<<< SEARCH
def test_task_deletion_edge_cases(app):
    """Test task deletion edge cases"""
    # Try deleting when no tasks exist
    app.query_one("#task-list").index = None
    app.on_key(events.Key("delete"))
    assert len(app.tasks) == 0
    
    # Try deleting when no task is selected
    app.tasks = [app.TaskItem("Task 1")]
    app.query_one("#task-list").index = None
    app.on_key(events.Key("delete"))
    assert len(app.tasks) == 1
    
    # Try deleting last task
    app.query_one("#task-list").index = 0
    app.on_key(events.Key("delete"))
    assert len(app.tasks) == 0
    assert app.query_one("#list-header").renderable == "All Tasks (0)"

def test_task_deletion_edge_cases(app):
    """Test task deletion edge cases"""
    # Try deleting when no tasks exist
    app.query_one("#task-list").index = None
    app.on_key(events.Key("delete"))
    assert len(app.tasks) == 0
    
    # Try deleting when no task is selected
    app.tasks = [app.TaskItem("Task 1")]
    app.query_one("#task-list").index = None
    app.on_key(events.Key("delete"))
    assert len(app.tasks) == 1
    
    # Try deleting last task
    app.query_one("#task-list").index = 0
    app.on_key(events.Key("delete"))
    assert len(app.tasks) == 0
    assert app.query_one("#list-header").renderable == "All Tasks (0)"
