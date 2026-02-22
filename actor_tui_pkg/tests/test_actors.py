"""Tests for actor modules."""

from actor_tui_pkg.actors import (
    InteractionSignature,
    MemorySignature,
    MemoryEditBlock,
)


def test_memory_edit_block():
    block = MemoryEditBlock(search="old", replace="new")
    assert block.search == "old"
    assert block.replace == "new"


def test_memory_edit_block_append():
    block = MemoryEditBlock(search="", replace="appended")
    assert block.search == ""


def test_interaction_signature_fields():
    assert "user_message" in InteractionSignature.fields
    assert "reply" in InteractionSignature.fields


def test_memory_signature_fields():
    assert "edits" in MemorySignature.fields
    assert "summary" in MemorySignature.fields
