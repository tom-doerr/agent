"""Tests for dataset module."""

import json

from actor_tui_pkg.dataset import (
    ReviewExample,
    load_examples,
    save_example,
    list_examples,
    update_example,
)


def test_save_and_load(tmp_path):
    path = tmp_path / "reviews.jsonl"
    ex = ReviewExample(
        actor_name="interaction",
        actor_inputs={"user_message": "hi"},
        actor_output="hello",
        reasoning="good",
        passed=True,
    )
    save_example(path, ex)
    examples = load_examples(path)
    assert len(examples) == 1
    assert examples[0].actor_output == "hello"


def test_list_examples(tmp_path):
    path = tmp_path / "reviews.jsonl"
    ex = ReviewExample(
        actor_name="memory",
        actor_inputs={"user_message": "x"},
        actor_output="y",
        reasoning="ok",
        passed=False,
    )
    save_example(path, ex)
    results = list_examples(path)
    assert len(results) == 1
    assert results[0].passed is False


def test_update_example(tmp_path):
    path = tmp_path / "reviews.jsonl"
    ex = ReviewExample(
        actor_name="interaction",
        actor_inputs={},
        actor_output="a",
        reasoning="bad",
        passed=False,
    )
    save_example(path, ex)
    update_example(path, 0, reasoning="good now", passed=True)
    results = list_examples(path)
    assert results[0].passed is True
    assert results[0].reasoning == "good now"


def test_load_empty(tmp_path):
    path = tmp_path / "nonexistent.jsonl"
    assert load_examples(path) == []
    assert list_examples(path) == []
