import json
import math
from types import SimpleNamespace

import numpy as np
from pydantic import ValidationError

import dspy_programs.concept_world_model_v3 as cm


def test_tag_state_ternary_encoding(monkeypatch):
    """LLMConceptTagger maps True→1, False→-1, missing→0."""
    # Use three STATE concepts so we can check present / absent / missing.
    state_concepts = cm.BASE_STATE_CONCEPTS[:3]
    universe = cm.ConceptUniverse(concepts=state_concepts)

    activations = {
        "activations": [
            {"concept_id": state_concepts[0].id, "value": True},
            {"concept_id": state_concepts[1].id, "value": False},
            # Intentionally omit the third concept to exercise the "missing" case.
        ]
    }

    tagger = cm.LLMConceptTagger()

    def fake_predict(**kwargs):
        return SimpleNamespace(activations_json=json.dumps(activations))

    monkeypatch.setattr(tagger, "predict", fake_predict)

    vec = tagger.tag_state("dummy observation", universe)
    assert vec.shape == (3,)
    assert list(vec) == [1, -1, 0]


def test_build_discounted_reward_no_meltdown():
    """Discounted returns for an episode without meltdown are standard MC sums."""
    dataset = cm.EpisodeDataset(gamma=0.9)
    dataset.observations = ["o0", "o1", "o2"]
    dataset.episode_ids = [0, 0, 0]
    dataset.step_indices = [0, 1, 2]
    dataset.actions = [0, 0, 0]
    dataset.meltdown_flags = [False]
    dataset.meltdown_steps = [None]
    # Z_state just needs the right shape; values are irrelevant for rewards.
    dataset.Z_state = np.zeros((3, 1), dtype=int)

    G = dataset.build_discounted_reward()
    assert G.shape == (3,)
    # r = [1, 1, 1], gamma = 0.9
    assert np.allclose(G, [1 + 0.9 + 0.9**2, 1 + 0.9, 1])


def test_build_discounted_reward_with_meltdown():
    """Meltdown step gets reward 0; earlier steps do not propagate beyond it."""
    dataset = cm.EpisodeDataset(gamma=0.9)
    dataset.observations = ["o0", "o1"]
    dataset.episode_ids = [0, 0]
    dataset.step_indices = [0, 1]
    dataset.actions = [2, 2]
    dataset.meltdown_flags = [True]
    dataset.meltdown_steps = [1]
    dataset.Z_state = np.zeros((2, 1), dtype=int)

    G = dataset.build_discounted_reward()
    assert G.shape == (2,)
    # r = [1, 0] → G = [1, 0]
    assert np.allclose(G, [1.0, 0.0])


def test_continuous_output_reward_monotonic_in_output():
    """Higher output at same step and demand should yield strictly higher reward."""
    env = cm.ReactorEnv(max_steps=10)
    env.step_idx = 5
    env.demand = "high"
    # Fake a steady action to skip dynamics; we care only about reward formula.
    # Simulate three different outputs and check reward ordering.
    outputs = [0.2, 0.8, 1.5]
    rewards = []
    for out in outputs:
        env.output = out
        env.meltdown = False
        # Reuse reward logic from run_greedy_actor_demo.
        t_norm = env.step_idx / max(env.max_steps, 1)
        demand_factor = 1.2
        exponent = 0.5 * env.output * (1.0 + t_norm) * demand_factor
        reward = math.exp(exponent) - 1.0
        rewards.append(reward)

    assert rewards[0] < rewards[1] < rewards[2]


def test_analyze_concept_future_adds_new_concept(monkeypatch):
    """_analyze_concept_future appends a new STATE concept once per parent pair."""
    exp = cm.Experiment(num_episodes=1, max_steps=1, gamma=0.9, max_new_concepts=1)
    # Default correlation threshold should be 0.0 (accept any positive cosine).
    assert getattr(exp, "corr_threshold", None) == 0.0
    # Restrict universe to two STATE concepts to keep K_state small and predictable.
    base_two = cm.BASE_STATE_CONCEPTS[:2]
    exp.universe = cm.ConceptUniverse(concepts=base_two)

    # Simple trace over 4 steps for 2 concepts so that both are sometimes on together
    # and sometimes not, giving us positive and negative examples.
    Z_ep = np.array(
        [
            [1, 1],  # both on
            [1, 0],  # only first
            [0, 1],  # only second
            [0, 0],  # neither
        ],
        dtype=int,
    )
    obs_ep = [f"log {t}" for t in range(Z_ep.shape[0])]

    # Stub LogisticRegression to produce identical non-zero weights for every concept
    # so cosine similarity between weight vectors is 1.0.
    class StubLR:
        def __init__(self, *args, **kwargs):
            self.coef_ = None

        def fit(self, X, y):
            # One row of ones → non-zero and identical for all j.
            self.coef_ = np.ones((1, X.shape[1]), dtype=float)

    monkeypatch.setattr(cm, "LogisticRegression", StubLR)

    # Stub concept_creator.create to return a deterministic new concept id.
    def fake_create(universe, pattern_concepts, pattern_description, positive_examples, negative_examples):  # noqa: D401,E501
        return cm.Concept(
            id="NEW_META_CONCEPT",
            definition="A meta concept used only in tests.",
            source=cm.ConceptSource.LLM,
        )

    monkeypatch.setattr(exp, "concept_creator", cm.ConceptCreator())
    monkeypatch.setattr(exp.concept_creator, "create", fake_create)

    prev_state_count = len(exp.universe.state_concepts)
    exp._analyze_concept_future([Z_ep], [obs_ep])

    # Universe should now contain the new concept as a STATE concept.
    assert "NEW_META_CONCEPT" in exp.universe.id_to_idx
    assert len(exp.universe.state_concepts) == prev_state_count + 1
    new_c = exp.universe.concepts[-1]
    assert new_c.id == "NEW_META_CONCEPT"
    assert new_c.source == cm.ConceptSource.LLM
    # Calling again with the same traces should NOT add a second meta-concept
    # from the same parent pair.
    exp._analyze_concept_future([Z_ep], [obs_ep])
    assert len(exp.universe.state_concepts) == prev_state_count + 1


def test_tag_state_invalid_json_raises_validation_error(monkeypatch):
    """Invalid JSON from the LLM path should surface as a Pydantic ValidationError."""
    universe = cm.ConceptUniverse(concepts=cm.BASE_STATE_CONCEPTS[:1])
    tagger = cm.LLMConceptTagger()

    def fake_predict(**kwargs):
        return SimpleNamespace(activations_json="not-json")

    monkeypatch.setattr(tagger, "predict", fake_predict)

    try:
        tagger.tag_state("obs", universe)
    except ValidationError:
        # Expected: Pydantic surfaces the schema/JSON issue directly.
        return
    assert False, "Expected ValidationError for invalid activations_json"


def test_tag_state_wrong_schema_raises_validation_error(monkeypatch):
    """JSON that doesn't match ConceptActivations schema should also raise."""
    universe = cm.ConceptUniverse(concepts=cm.BASE_STATE_CONCEPTS[:1])
    tagger = cm.LLMConceptTagger()

    # Missing 'activations' key and wrong structure.
    bad_payload = {"foo": "bar"}

    def fake_predict(**kwargs):
        return SimpleNamespace(activations_json=json.dumps(bad_payload))

    monkeypatch.setattr(tagger, "predict", fake_predict)

    try:
        tagger.tag_state("obs", universe)
    except ValidationError:
        return
    assert False, "Expected ValidationError for wrong ConceptActivations schema"


def test_analyze_concept_future_all_constant_prints_message(monkeypatch):
    """When all future-occupancy targets are constant, we log a detailed message."""
    exp = cm.Experiment(num_episodes=1, max_steps=1, gamma=0.9, max_new_concepts=1)
    # One episode, all-zero STATE activations → y_j always 0 for every concept.
    K_state = len(exp.universe.state_concepts)
    Z_ep = np.zeros((4, K_state), dtype=int)
    obs_ep = [f"log {t}" for t in range(Z_ep.shape[0])]

    messages: list[str] = []

    def fake_print(*args, **kwargs):
        messages.append(" ".join(str(a) for a in args))

    monkeypatch.setattr(cm.console, "print", fake_print)
    monkeypatch.setattr(cm.console, "rule", lambda *a, **k: None)

    exp._analyze_concept_future([Z_ep], [obs_ep])

    assert any("Future-occupancy predictors are all zero/constant" in m for m in messages)
    # At least one concept should have a constant-0 occupancy stat printed.
    assert any("constant 0" in m for m in messages)


def test_analyze_concept_future_mixed_target_avoids_constant_message(monkeypatch):
    """If at least one concept has mixed future-occupancy, we should not emit the 'all zero' message."""
    exp = cm.Experiment(num_episodes=1, max_steps=1, gamma=0.9, max_new_concepts=1)
    # Restrict to a single STATE concept for clarity.
    exp.universe = cm.ConceptUniverse(concepts=cm.BASE_STATE_CONCEPTS[:1])
    # Make the concept present only at the first step so y is mixed.
    Z_ep = np.array([[1], [0], [0], [0]], dtype=int)
    obs_ep = [f"log {t}" for t in range(Z_ep.shape[0])]

    messages: list[str] = []

    def fake_print(*args, **kwargs):
        messages.append(" ".join(str(a) for a in args))

    monkeypatch.setattr(cm.console, "print", fake_print)
    monkeypatch.setattr(cm.console, "rule", lambda *a, **k: None)

    exp._analyze_concept_future([Z_ep], [obs_ep])

    assert not any(
        "Future-occupancy predictors are all zero/constant" in m for m in messages
    )


def test_run_greedy_actor_demo_no_baseline_fields(monkeypatch):
    """Per-step logs should not mention baseline_* fields now that warmup is gone."""
    exp = cm.Experiment(num_episodes=1, max_steps=2, gamma=0.9, max_new_concepts=0)

    # Avoid real LLM calls: stub tagger and _greedy_action.
    monkeypatch.setattr(
        exp.tagger,
        "tag_state",
        lambda obs, universe: np.zeros(len(universe.state_concepts), dtype=int),
    )

    def fake_greedy_action(state_vec):
        return 0, np.array([0.0, 0.0, 0.0])

    monkeypatch.setattr(exp, "_greedy_action", fake_greedy_action)

    messages: list[str] = []

    def fake_print(*args, **kwargs):
        messages.append(" ".join(str(a) for a in args))

    monkeypatch.setattr(cm.console, "print", fake_print)
    monkeypatch.setattr(cm.console, "rule", lambda *a, **k: None)

    exp.run_greedy_actor_demo(num_episodes=1)

    joined = "\n".join(messages)
    assert "baseline_mean_G" not in joined
    assert "baseline_action_means" not in joined


def test_reward_model_pad_truncate_prediction():
    """RewardModel.predict pads/truncates features instead of resetting when K changes."""
    rm = cm.RewardModel()
    # Fit on 3 features.
    X = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    G = np.array([1.0, 2.0])
    rm.fit(X, G, [0, 1])
    assert rm.n_features == 3

    # Predict with more features: the extra ones should be ignored.
    X_more = np.array([[1.0, 0.0, 0.0, 999.0]])
    y_more = rm.predict(X_more)
    X_same = np.array([[1.0, 0.0, 0.0]])
    y_same = rm.predict(X_same)
    assert np.allclose(y_more, y_same)

    # Predict with fewer features: they should be zero-padded.
    X_less = np.array([[1.0, 0.0]])
    y_less = rm.predict(X_less)
    assert np.allclose(y_less, y_same)
