"""Tests for memory module."""

from actor_tui_pkg.actors import MemoryEditBlock
from actor_tui_pkg.memory import MemoryManager


def test_read_empty(tmp_path):
    mgr = MemoryManager(tmp_path / "memory.md")
    assert mgr.read() == ""


def test_append_edit(tmp_path):
    path = tmp_path / "memory.md"
    mgr = MemoryManager(path)
    edits = [MemoryEditBlock(search="", replace="Hello world")]
    new_content, diff = mgr.apply_edits(edits)
    assert "Hello world" in new_content
    assert path.read_text().strip() == "Hello world"


def test_search_replace(tmp_path):
    path = tmp_path / "memory.md"
    path.write_text("old text here\n")
    mgr = MemoryManager(path)
    edits = [MemoryEditBlock(search="old text", replace="new text")]
    new_content, diff = mgr.apply_edits(edits)
    assert "new text here" in new_content
    assert "old text" not in path.read_text()


def test_search_not_found(tmp_path):
    path = tmp_path / "memory.md"
    path.write_text("original\n")
    mgr = MemoryManager(path)
    edits = [MemoryEditBlock(search="missing", replace="x")]
    new_content, _ = mgr.apply_edits(edits)
    assert new_content == "original\n"
