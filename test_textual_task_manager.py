import pytest
from textual import events
from textual_task_manager import TaskManager, TASKS_FILE, TaskItem
from textual.widgets import Input

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def pilot(tmp_path):
    """Create a TaskManager instance for testing."""
    global TASKS_FILE
    TASKS_FILE = str(tmp_path / "tasks.json")
    app = TaskManager()
    async with app.run_test() as pilot:
        yield pilot


async def test_add_task(pilot):
    """Test adding a new task."""
    app = pilot.app
    app.tasks = []
    input_widget = app.query_one("#new-task-input", Input)
    input_widget.value = "New task"
    app.on_input_submitted(Input.Submitted(input_widget))
    assert len(app.tasks) == 1
    assert app.tasks[0].task_text == "New task"
    assert not app.tasks[0].completed


async def test_toggle_task(pilot):
    """Test toggling task completion."""
    app = pilot.app
    app.tasks = [TaskItem("Test task")]
    app.query_one("#task-list").index = 0
    app.toggle_selected_task()
    assert app.tasks[0].completed
    app.toggle_selected_task()
    assert not app.tasks[0].completed


async def test_delete_task(pilot):
    """Test deleting a task."""
    app = pilot.app
    app.tasks = [TaskItem("Task to delete")]
    app.query_one("#task-list").index = 0
    app.on_key(events.Key("delete"))
    assert len(app.tasks) == 0


async def test_clear_completed(pilot):
    """Test clearing completed tasks."""
    app = pilot.app
    app.tasks = [
        TaskItem("Active task", completed=False),
        TaskItem("Completed task", completed=True),
    ]
    app.query_one("#clear-completed").press()
    assert len(app.tasks) == 1
    assert app.tasks[0].task_text == "Active task"


async def test_save_load_tasks(tmp_path):
    """Test saving and loading tasks."""
    async with TaskManager().run_test() as app1:
        app1.tasks = [
            TaskItem("Task 1", completed=True),
            TaskItem("Task 2", completed=False),
        ]
        app1.save_tasks()

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
    """Test task filtering."""
    app = pilot.app
    app.tasks = [
        TaskItem("Active 1", completed=False),
        TaskItem("Completed 1", completed=True),
        TaskItem("Active 2", completed=False),
    ]

    app.current_filter = "all"
    app.update_list()
    assert len(app.query_one("#task-list").children) == 3

    app.current_filter = "active"
    app.update_list()
    assert len(app.query_one("#task-list").children) == 2

    app.current_filter = "completed"
    app.update_list()
    assert len(app.query_one("#task-list").children) == 1


async def test_list_header(pilot):
    """Test that the task list header shows the correct filter and count."""
    app = pilot.app
    app.tasks = [
        TaskItem("Active 1", completed=False),
        TaskItem("Completed 1", completed=True),
        TaskItem("Active 2", completed=False),
    ]

    app.current_filter = "all"
    app.update_list()
    assert app.query_one("#list-header").renderable == "All Tasks (3)"

    app.current_filter = "active"
    app.update_list()
    assert app.query_one("#list-header").renderable == "Active Tasks (2)"

    app.current_filter = "completed"
    app.update_list()
    assert app.query_one("#list-header").renderable == "Completed Tasks (1)"

    app.query_one("#task-list").index = 0
    app.toggle_selected_task()
    app.update_list()
    assert app.query_one("#list-header").renderable == "Completed Tasks (2)"

    app.query_one("#task-list").index = 0
    app.on_key(events.Key("delete"))
    app.update_list()
    assert app.query_one("#list-header").renderable == "Completed Tasks (1)"


async def test_initial_empty_state(pilot):
    """Test that the app handles an empty state correctly."""
    app = pilot.app
    app.tasks = []
    app.update_list()
    app.update_button_labels()

    assert app.query_one("#filter-all").label == "All (0)"
    assert app.query_one("#filter-active").label == "Active (0)"
    assert app.query_one("#filter-completed").label == "Completed (0)"
    assert app.query_one("#list-header").renderable == "All Tasks (0)"
    assert len(app.query_one("#task-list").children) == 0


async def test_task_editing(pilot):
    """Test that tasks can be edited by deleting and re-adding."""
    app = pilot.app
    input_widget = app.query_one("#new-task-input", Input)
    input_widget.value = "Original task"
    app.on_input_submitted(Input.Submitted(input_widget))
    assert len(app.tasks) == 1

    app.query_one("#task-list").index = 0
    app.on_key(events.Key("delete"))
    assert len(app.tasks) == 0

    input_widget.value = "Modified task"
    app.on_input_submitted(Input.Submitted(input_widget))
    assert len(app.tasks) == 1
    assert app.tasks[0].task_text == "Modified task"


async def test_task_duplication(pilot):
    """Test that duplicate tasks are handled correctly."""
    app = pilot.app
    input_widget = app.query_one("#new-task-input", Input)

    input_widget.value = "Duplicate task"
    app.on_input_submitted(Input.Submitted(input_widget))
    assert len(app.tasks) == 1

    input_widget.value = "Duplicate task"
    app.on_input_submitted(Input.Submitted(input_widget))
    assert len(app.tasks) == 2
    assert app.tasks[0].task_text == "Duplicate task"
    assert app.tasks[1].task_text == "Duplicate task"


async def test_task_deletion_edge_cases(pilot):
    """Test task deletion edge cases."""
    app = pilot.app

    app.query_one("#task-list").index = None
    app.on_key(events.Key("delete"))
    assert len(app.tasks) == 0

    app.tasks = [TaskItem("Task 1")]
    app.query_one("#task-list").index = None
    app.on_key(events.Key("delete"))
    assert len(app.tasks) == 1

    app.query_one("#task-list").index = 0
    app.on_key(events.Key("delete"))
    assert len(app.tasks) == 0
    assert app.query_one("#list-header").renderable == "All Tasks (0)"
