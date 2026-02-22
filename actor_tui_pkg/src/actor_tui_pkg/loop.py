"""Actor-reviewer retry loop."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

import dspy

from .reviewer import Reviewer, ReviewResult


@dataclass
class Attempt:
    """One attempt by an actor."""

    iteration: int
    actor_output: Any
    review: Optional[ReviewResult] = None


@dataclass
class ActorReviewerResult:
    """Full result of running an actor through the reviewer loop."""

    actor_name: str
    attempts: list[Attempt] = field(default_factory=list)
    final_output: Any = None
    passed: bool = False


def run_actor_reviewer_loop(
    *,
    actor: dspy.Module,
    reviewer: Reviewer,
    actor_name: str,
    actor_kwargs: dict,
    max_iters: int = 3,
    output_field: str = "reply",
    on_attempt: Optional[Callable[[Attempt], None]] = None,
) -> ActorReviewerResult:
    """Run actor, review output, retry with feedback on failure."""
    attempts: list[Attempt] = []
    feedback = ""

    for i in range(max_iters):
        prediction = actor(**actor_kwargs, feedback=feedback)
        actor_output = getattr(prediction, output_field)
        inputs_json = json.dumps(
            {k: v for k, v in actor_kwargs.items() if k != "feedback"},
            default=str,
        )

        review_pred = reviewer(
            actor_inputs=inputs_json, actor_output=str(actor_output)
        )
        review = ReviewResult(
            reasoning=review_pred.reasoning,
            passed=review_pred.passed,
            actor_inputs=actor_kwargs,
            actor_output=str(actor_output),
        )

        attempt = Attempt(iteration=i + 1, actor_output=prediction, review=review)
        attempts.append(attempt)
        if on_attempt:
            on_attempt(attempt)

        if review.passed:
            return ActorReviewerResult(
                actor_name=actor_name,
                attempts=attempts,
                final_output=prediction,
                passed=True,
            )
        feedback = review.reasoning

    return ActorReviewerResult(
        actor_name=actor_name,
        attempts=attempts,
        final_output=attempts[-1].actor_output,
        passed=False,
    )
