import pytest
from textual_task_manager import TaskManager, TaskItem

@pytest.fixture
def temp_manager(tmp_path, monkeypatch):
    path = tmp_path / "tasks.json"
    monkeypatch.setattr("textual_task_manager.TASKS_FILE", str(path))
    mgr = TaskManager()
    return mgr

def test_save_and_load_tasks(temp_manager):
    mgr = temp_manager
    mgr.tasks = [TaskItem("Sample", completed=True)]
    mgr.save_tasks()

    new_mgr = TaskManager()
    # ensure same temp file is used
    new_mgr.load_tasks()
    assert len(new_mgr.tasks) == 1
    assert new_mgr.tasks[0].task_text == "Sample"
    assert new_mgr.tasks[0].completed
