"""Tests for actor-reviewer loop."""

import dspy

from actor_tui_pkg.loop import run_actor_reviewer_loop, Attempt
from actor_tui_pkg.reviewer import Reviewer
from actor_tui_pkg.state import SystemState


class FakeActor(dspy.Module):
    def __init__(self, replies, input_fields=None):
        super().__init__()
        self._replies = list(replies)
        self._idx = 0
        if input_fields is not None:
            self.INPUT_FIELDS = frozenset(input_fields)

    def forward(self, state):
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
        state=SystemState(user_message="hi"),
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
        state=SystemState(user_message="hi"),
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
        state=SystemState(user_message="hi"),
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
        state=SystemState(user_message=""),
        output_field="reply",
        on_attempt=lambda a: logged.append(a),
    )
    assert len(logged) == 1


class CapturingReviewer(Reviewer):
    """Reviewer that captures actor_inputs."""

    def __init__(self, verdicts):
        super().__init__()
        self._verdicts = list(verdicts)
        self._idx = 0
        self.captured_inputs = []

    def forward(self, *, actor_inputs, actor_output):
        import json
        self.captured_inputs.append(json.loads(actor_inputs))
        passed, reasoning = self._verdicts[
            min(self._idx, len(self._verdicts) - 1)
        ]
        self._idx += 1
        return dspy.Prediction(reasoning=reasoning, passed=passed)


def test_input_fields_filters_state():
    """Reviewer only sees fields in INPUT_FIELDS."""
    actor = FakeActor(
        ["reply"], input_fields={"user_message", "memory"},
    )
    reviewer = CapturingReviewer([(True, "ok")])
    state = SystemState(
        user_message="hi", memory="mem",
        chat_history="hist", assistant_reply="old",
    )
    run_actor_reviewer_loop(
        actor=actor, reviewer=reviewer,
        actor_name="t", state=state, output_field="reply",
    )
    got = reviewer.captured_inputs[0]
    assert set(got.keys()) == {"user_message", "memory"}
    assert "chat_history" not in got


def test_no_input_fields_sends_all():
    """Without INPUT_FIELDS, all fields except feedback."""
    actor = FakeActor(["reply"])
    reviewer = CapturingReviewer([(True, "ok")])
    state = SystemState(
        user_message="hi", memory="mem",
        chat_history="hist", assistant_reply="old",
    )
    run_actor_reviewer_loop(
        actor=actor, reviewer=reviewer,
        actor_name="t", state=state, output_field="reply",
    )
    got = reviewer.captured_inputs[0]
    assert "user_message" in got
    assert "assistant_reply" in got
    assert "feedback" not in got


def test_review_result_matches_input_fields():
    """ReviewResult.actor_inputs uses INPUT_FIELDS."""
    actor = FakeActor(["r"], input_fields={"user_message"})
    reviewer = CapturingReviewer([(True, "ok")])
    state = SystemState(user_message="hi", memory="mem")
    result = run_actor_reviewer_loop(
        actor=actor, reviewer=reviewer,
        actor_name="t", state=state, output_field="reply",
    )
    ri = result.attempts[0].review.actor_inputs
    assert set(ri.keys()) == {"user_message"}
