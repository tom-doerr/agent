from types import SimpleNamespace

import pytest

import cognition_typed_dspy as cognition


def test_parse_obj_like_supports_yaml_and_plan_lists() -> None:
    """parse_obj_like should handle YAML documents and list coercion."""

    yaml_payload = """
facts:
  - observed state
uncertainties:
  - ambiguous
""".strip()

    percept = cognition.parse_obj_like(yaml_payload, cognition.Percept)
    assert percept.facts == ["observed state"]
    assert percept.uncertainties == ["ambiguous"]

    plans_payload = """
- id: plan-1
  steps:
    - step one
- id: plan-2
  steps:
    - step two
""".strip()

    plans = cognition.parse_obj_like(plans_payload, cognition._plans_parser)  # noqa: SLF001 - module-level helper
    assert [plan.id for plan in plans] == ["plan-1", "plan-2"]


def test_cognition_agent_forward_uses_typed_predictions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CognitionAgent should parse each module output using TypedPredict wrappers."""

    calls: list[tuple[str, dict[str, object]]] = []

    responses = {
        "PerceiveFocus": {
            "percept": "facts:\n  - sensory\nuncertainties:\n  - noisy",
        },
        "UpdateBelief": {
            "belief": {
                "entities": ["entity"],
                "assumptions": ["assume"],
                "epistemic": 0.4,
                "aleatoric": 0.2,
            },
            "affect": {
                "confidence": 0.8,
                "surprise": 0.1,
                "risk": 0.3,
                "budget_spend": 1.0,
                "budget_cap": 5.0,
            },
        },
        "ProposePlans": {
            "plans": "- id: plan-1\n  steps:\n    - step",
        },
        "EvaluatePlans": {
            "scored": "- id: plan-1\n  EV: 1.2\n  risk: 0.1\n  confidence: 0.7\n  rationale: good",
        },
        "SelectAct": {
            "decision": "choice: execute\nplan_id: plan-1\naction_tool: tool",
        },
        "VerifyEffect": {
            "verification": {
                "checks": ["check"],
                "all_passed": True,
            },
            "outcome": "reward: 2.0\npolicy_violations: 0\nrisk_flag: false\nnotes: done",
        },
        "Learn": {
            "update": "note: remember",
        },
    }

    def fake_predict(signature):  # type: ignore[no-untyped-def]
        name = signature.__name__

        class Runner:
            def __call__(self, **kwargs):  # type: ignore[override]
                calls.append((name, kwargs))
                return SimpleNamespace(**responses[name])

        return Runner()

    monkeypatch.setattr(cognition.dspy, "Predict", fake_predict)

    agent = cognition.CognitionAgent()

    result = agent.forward(
        observation="obs",
        episodic_memory="memory",
        goals="goal",
        constraints="limit",
        utility_def="utility",
        prior_belief="prior",
        attention_results="attention",
        system_events="events",
    )

    sequence = [name for name, _ in calls]
    assert sequence == [
        "PerceiveFocus",
        "UpdateBelief",
        "ProposePlans",
        "EvaluatePlans",
        "SelectAct",
        "VerifyEffect",
        "Learn",
    ]

    first_call_name, first_call_kwargs = calls[0]
    assert first_call_name == "PerceiveFocus"
    assert first_call_kwargs["observation"] == "obs"
    assert first_call_kwargs["goals"] == "goal"

    assert isinstance(result["percept"], cognition.Percept)
    assert result["percept"].facts == ["sensory"]
    assert isinstance(result["belief"], cognition.Belief)
    assert result["affect"].confidence == pytest.approx(0.8)
    assert len(result["plans"]) == 1 and isinstance(result["plans"][0], cognition.Plan)
    assert result["scored"][0].EV == pytest.approx(1.2)
    assert result["decision"].choice == "execute"
    assert result["verification"].all_passed is True
    assert result["outcome"].reward == pytest.approx(2.0)
    assert result["update"].note == "remember"

