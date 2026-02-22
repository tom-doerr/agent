"""Tests for reviewer module."""

from actor_tui_pkg.reviewer import (
    Reviewer,
    ReviewSignature,
    ReviewResult,
    build_reviewer,
)


def test_review_signature_fields():
    assert "actor_inputs" in ReviewSignature.fields
    assert "reasoning" in ReviewSignature.fields
    assert "passed" in ReviewSignature.fields


def test_reviewer_init():
    r = Reviewer(name="test")
    assert r.name == "test"


def test_review_result():
    r = ReviewResult(
        reasoning="ok", passed=True,
        actor_inputs={"x": 1}, actor_output="y",
    )
    assert r.passed is True


def test_build_reviewer_empty(tmp_path):
    r = build_reviewer("test", tmp_path / "empty.jsonl")
    assert r.name == "test"
