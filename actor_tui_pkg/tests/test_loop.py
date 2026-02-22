"""Tests for actor-reviewer loop."""

import dspy

from actor_tui_pkg.loop import run_actor_reviewer_loop, Attempt
from actor_tui_pkg.reviewer import Reviewer


class FakeActor(dspy.Module):
    def __init__(self, replies):
        super().__init__()
        self._replies = list(replies)
        self._idx = 0

    def forward(self, *, feedback="", **kw):
        reply = self._replies[min(self._idx, len(self._replies) - 1)]
        self._idx += 1
        return dspy.Prediction(reply=reply)


class FakeReviewer(Reviewer):
    def __init__(self, verdicts):
        super().__init__()
        self._verdicts = list(verdicts)
        self._idx = 0

    def forward(self, *, actor_inputs, actor_output):
        passed, reasoning = self._verdicts[min(self._idx, len(self._verdicts) - 1)]
        self._idx += 1
        return dspy.Prediction(reasoning=reasoning, passed=passed)


def test_passes_first_attempt():
    actor = FakeActor(["good reply"])
    reviewer = FakeReviewer([(True, "looks good")])
    result = run_actor_reviewer_loop(
        actor=actor,
        reviewer=reviewer,
        actor_name="test",
        actor_kwargs={"user_message": "hi"},
        output_field="reply",
    )
    assert result.passed is True
    assert len(result.attempts) == 1


def test_retries_on_failure():
    actor = FakeActor(["bad", "good"])
    reviewer = FakeReviewer([(False, "too short"), (True, "ok")])
    result = run_actor_reviewer_loop(
        actor=actor,
        reviewer=reviewer,
        actor_name="test",
        actor_kwargs={"user_message": "hi"},
        output_field="reply",
    )
    assert result.passed is True
    assert len(result.attempts) == 2


def test_max_iters_reached():
    actor = FakeActor(["bad"] * 3)
    reviewer = FakeReviewer([(False, "nope")] * 3)
    result = run_actor_reviewer_loop(
        actor=actor,
        reviewer=reviewer,
        actor_name="test",
        actor_kwargs={"user_message": "hi"},
        max_iters=3,
        output_field="reply",
    )
    assert result.passed is False
    assert len(result.attempts) == 3


def test_on_attempt_callback():
    logged = []
    actor = FakeActor(["reply"])
    reviewer = FakeReviewer([(True, "ok")])
    run_actor_reviewer_loop(
        actor=actor,
        reviewer=reviewer,
        actor_name="test",
        actor_kwargs={},
        output_field="reply",
        on_attempt=lambda a: logged.append(a),
    )
    assert len(logged) == 1
