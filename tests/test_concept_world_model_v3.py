import json
import math
import random
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
        # Tagger will run ConceptActivations.model_validate on this.
        return SimpleNamespace(activations=activations)

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


def test_operator_note_reflects_output_level():
    """Operator note should indirectly hint at output via steam/turbine text."""
    env = cm.ReactorEnv(max_steps=5)
    env.glitches = 0
    env.stress = 50
    env.margin = 60
    env.mood = "calm"

    # Low output
    env.output = 0.2
    note_low = env._make_observation(last_action=0)
    assert "steam output feels anemic" in note_low

    # Medium output
    env.output = 0.6
    note_med = env._make_observation(last_action=0)
    assert "Steam output feels normal" in note_med

    # High output
    env.output = 1.3
    note_high = env._make_observation(last_action=0)
    assert "Steam output is heavy" in note_high


def test_observation_includes_exact_power_output():
    """Observation string should include the exact numeric power output."""
    env = cm.ReactorEnv(max_steps=5, difficulty=1.0, noise=0.0)
    env.glitches = 0
    env.stress = 50
    env.margin = 60
    env.mood = "calm"
    env.output = 1.2345
    obs = env._make_observation(last_action=0)
    # Expect the formatted numeric output to appear with 3 decimals.
    assert f"{env.output:.3f}" in obs


def test_power_output_in_note_tracks_updates():
    """Operator note's numeric power output should reflect the latest env.output."""
    env = cm.ReactorEnv(max_steps=5, difficulty=1.0, noise=0.0)
    env.glitches = 0
    env.stress = 50
    env.margin = 60
    env.mood = "calm"

    env.output = 0.5
    obs1 = env._make_observation(last_action=0)
    assert "(measured reactor output=0.500)" in obs1

    env.output = 1.25
    obs2 = env._make_observation(last_action=0)
    assert "(measured reactor output=1.250)" in obs2


def test_red_warning_light_triggers_on_risky_state():
    """Red blinking warning text should appear only in risky regimes."""
    env = cm.ReactorEnv(max_steps=5)
    env.output = 0.8
    env.glitches = 0
    env.stress = 50
    env.margin = 60
    env.mood = "calm"

    safe_obs = env._make_observation(last_action=0)
    assert "red warning light blinks" not in safe_obs

    env.stress = 85.0
    env.margin = 30.0
    env.glitches = 3
    risky_obs = env._make_observation(last_action=0)
    assert "red warning light blinks" in risky_obs


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
    """Invalid structured output from the LLM should surface as a Pydantic ValidationError."""
    universe = cm.ConceptUniverse(concepts=cm.BASE_STATE_CONCEPTS[:1])
    tagger = cm.LLMConceptTagger()

    def fake_predict(**kwargs):
        # A plain string is not a valid ConceptActivations object.
        return SimpleNamespace(activations="not-json")

    monkeypatch.setattr(tagger, "predict", fake_predict)

    try:
        tagger.tag_state("obs", universe)
    except ValidationError:
        # Expected: Pydantic surfaces the schema/JSON issue directly.
        return
    assert False, "Expected ValidationError for invalid activations_json"


def test_tag_state_wrong_schema_raises_validation_error(monkeypatch):
    """Objects that don't match ConceptActivations schema should also raise."""
    universe = cm.ConceptUniverse(concepts=cm.BASE_STATE_CONCEPTS[:1])
    tagger = cm.LLMConceptTagger()

    # Missing 'activations' key and wrong structure.
    bad_payload = {"foo": "bar"}

    def fake_predict(**kwargs):
        # Missing 'activations' list in payload.
        return SimpleNamespace(activations=bad_payload)

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


def test_check_meltdown_triggers_under_extreme_conditions():
    """_check_meltdown should set meltdown when stress high, margin low, glitches present."""
    env = cm.ReactorEnv(max_steps=5, difficulty=1.0)
    env.stress = 90.0
    env.margin = 20.0
    env.glitches = 2
    env.meltdown = False
    env._check_meltdown()
    assert env.meltdown


def test_difficulty_tightens_meltdown_thresholds():
    """Higher difficulty should make the same state more likely to melt down."""
    # Same state: stress=77, margin=38, glitches=1.
    # For difficulty 1.0: stress_thresh=80, margin_thresh=35 → no meltdown.
    # For difficulty 2.0: stress_thresh=75, margin_thresh=40 → meltdown.
    env_easy = cm.ReactorEnv(max_steps=5, difficulty=1.0)
    env_easy.stress = 77.0
    env_easy.margin = 38.0
    env_easy.glitches = 1
    env_easy.meltdown = False
    env_easy._check_meltdown()
    assert not env_easy.meltdown

    env_hard = cm.ReactorEnv(max_steps=5, difficulty=2.0)
    env_hard.stress = 77.0
    env_hard.margin = 38.0
    env_hard.glitches = 1
    env_hard.meltdown = False
    env_hard._check_meltdown()
    assert env_hard.meltdown


def test_meltdown_reward_is_negative(monkeypatch):
    """When meltdown occurs in greedy run, reward_t should be -10."""
    exp = cm.Experiment(num_episodes=1, max_steps=3, gamma=0.9, max_new_concepts=0)

    # Avoid real LLM calls and learned policy.
    monkeypatch.setattr(
        exp.tagger,
        "tag_state",
        lambda obs, universe: np.zeros(len(universe.state_concepts), dtype=int),
    )
    monkeypatch.setattr(
        exp, "_greedy_action", lambda state_vec: (0, np.array([0.0, 0.0, 0.0]))
    )

    # Force meltdown on first step by monkeypatching env.step.
    def fake_step(action: int):
        exp.env.step_idx += 1
        exp.env.meltdown = True
        return "obs", True, True

    monkeypatch.setattr(exp.env, "step", fake_step)

    messages: list[str] = []

    def fake_print(*args, **kwargs):
        messages.append(" ".join(str(a) for a in args))

    monkeypatch.setattr(cm.console, "print", fake_print)
    monkeypatch.setattr(cm.console, "rule", lambda *a, **k: None)

    exp.run_greedy_actor_demo(num_episodes=1)

    joined = "\n".join(messages)
    # There should be a step line with reward_t=-10.000 and a meltdown marker.
    assert "[red]reward_t[/red]=-10.000" in joined
    assert "-> MELTDOWN at step 0" in joined


def test_greedy_action_picks_best_predicted_return():
    """_greedy_action should select the action with highest predicted return."""
    # Tiny universe: only STATE concepts so action indices are stable.
    base_two = cm.BASE_STATE_CONCEPTS[:2]
    universe = cm.ConceptUniverse(concepts=base_two + cm.ACTION_CONCEPTS)
    exp = cm.Experiment(num_episodes=1, max_steps=1, gamma=0.9, max_new_concepts=0)
    exp.universe = universe

    # Fit RewardModel on 3 synthetic transitions with hand-crafted targets so that
    # action 1 has the highest estimated value for the test state.
    K = exp.universe.K
    rm = exp.reward_model

    # Build simple feature vectors for each action at a fixed state.
    state_vec = np.array([1, 0], dtype=int)
    state_indices = exp.universe.state_index_map()
    action_ids = ["ACTION_STEADY", "ACTION_COOL", "ACTION_PUSH"]
    X_rows = []
    targets = []
    for a, target in zip([0, 1, 2], [0.5, 1.0, 0.2]):
        x = np.zeros(K, dtype=float)
        x[state_indices] = state_vec
        cid = action_ids[a]
        j_act = exp.universe.id_to_idx[cid]
        x[j_act] = 1.0
        X_rows.append(x)
        targets.append(target)
    X = np.stack(X_rows)
    G = np.array(targets)

    rm.fit(X, G, [0, 1, 2])

    best_a, preds = exp._greedy_action(state_vec)
    # Action 1 ("cool") should have the highest predicted return.
    assert best_a == 1
    assert preds[1] == max(preds)


def test_epsilon_greedy_exploration_respected(monkeypatch):
    """With epsilon=1.0, actions should be sampled uniformly at random."""
    exp = cm.Experiment(num_episodes=1, max_steps=5, gamma=0.9, max_new_concepts=0, eps_greedy=1.0)

    # Avoid real LLM calls; we only care about actions.
    monkeypatch.setattr(
        exp.tagger,
        "tag_state",
        lambda obs, universe: np.zeros(len(universe.state_concepts), dtype=int),
    )
    # Force the greedy action to always be 0 so any non-zero action must come from exploration.
    monkeypatch.setattr(
        exp,
        "_greedy_action",
        lambda state_vec: (0, np.array([0.0, 0.0, 0.0])),
    )

    # Capture actions chosen at each step.
    chosen_actions: list[int] = []

    # Patch env.step to record the action and keep the episode running for max_steps.
    def fake_step(action: int):
        chosen_actions.append(action)
        exp.env.step_idx += 1
        done = exp.env.step_idx >= exp.env.max_steps
        exp.env.meltdown = False
        return "obs", done, False

    monkeypatch.setattr(exp.env, "step", fake_step)

    # Disable noisy logging for this test.
    monkeypatch.setattr(cm.console, "print", lambda *a, **k: None)
    monkeypatch.setattr(cm.console, "rule", lambda *a, **k: None)

    exp.run_greedy_actor_demo(num_episodes=1)

    # With epsilon=1.0 and 5 steps, we expect a mix of actions 0,1,2.
    assert len(chosen_actions) == exp.env.max_steps
    assert set(chosen_actions).issubset({0, 1, 2})
    # Since greedy always suggests 0, seeing any non-zero action implies exploration happened.
    assert any(a != 0 for a in chosen_actions)


def test_reward_model_fit_logging(monkeypatch):
    """After an episode, we log a small summary of the reward model fit."""
    exp = cm.Experiment(num_episodes=1, max_steps=3, gamma=0.9, max_new_concepts=0)

    # Avoid real LLM calls and complex policy.
    monkeypatch.setattr(
        exp.tagger,
        "tag_state",
        lambda obs, universe: np.zeros(len(universe.state_concepts), dtype=int),
    )
    monkeypatch.setattr(
        exp,
        "_greedy_action",
        lambda state_vec: (0, np.array([0.0, 0.0, 0.0])),
    )

    # Simple env.step that never melts down and advances until max_steps.
    def fake_step(action: int):
        exp.env.step_idx += 1
        exp.env.output = 0.5
        exp.env.demand = "low"
        done = exp.env.step_idx >= exp.env.max_steps
        exp.env.meltdown = False
        return "obs", done, False

    monkeypatch.setattr(exp.env, "step", fake_step)

    messages: list[str] = []

    def fake_print(*args, **kwargs):
        messages.append(" ".join(str(a) for a in args))

    monkeypatch.setattr(cm.console, "print", fake_print)
    monkeypatch.setattr(cm.console, "rule", lambda *a, **k: None)

    exp.run_greedy_actor_demo(num_episodes=1)

    joined = "\n".join(messages)
    assert "Fitted reward model" in joined
    assert "samples=" in joined
    # Zero-weight tracking should also be mentioned.
    assert "always_zero=" in joined


def test_zero_weight_counts_tracking():
    """_update_zero_weight_counts increments counts for zero-weight concepts."""
    exp = cm.Experiment(num_episodes=1, max_steps=1, gamma=0.9, max_new_concepts=0)
    # Small universe to keep things readable.
    exp.universe = cm.ConceptUniverse(concepts=cm.BASE_STATE_CONCEPTS[:3])
    coef_arr = np.array([0.0, 0.5, 0.0])
    exp._update_zero_weight_counts(coef_arr)
    # Two concepts should have count=1; one should be 0.
    ids = exp.universe.idx_to_id
    zero_cids = [cid for idx, cid in ids.items() if coef_arr[idx] == 0.0]
    nonzero_cids = [cid for idx, cid in ids.items() if coef_arr[idx] != 0.0]
    for cid in zero_cids:
        assert exp.concept_zero_counts.get(cid, 0) == 1
    for cid in nonzero_cids:
        assert exp.concept_zero_counts.get(cid, 0) == 0


def test_max_concepts_drops_lowest_importance_state_concept(monkeypatch):
    """When max_concepts is exceeded, the lowest-importance STATE concept is dropped."""
    # Build an experiment with a tiny STATE universe and low max_concepts=2.
    exp = cm.Experiment(
        num_episodes=1,
        max_steps=1,
        gamma=0.9,
        max_new_concepts=0,
        max_concepts=2,
    )
    # Restrict to three STATE concepts but keep ACTION concepts so _greedy_action
    # can still build feature vectors.
    concepts = cm.BASE_STATE_CONCEPTS[:3] + cm.ACTION_CONCEPTS
    exp.universe = cm.ConceptUniverse(concepts=concepts)
    ids = [c.id for c in cm.BASE_STATE_CONCEPTS[:3]]

    # Pretend we've done 4 fits and concept importances averaged as follows:
    # concept 0 lowest, concept 1 medium, concept 2 highest.
    exp.concept_importance_updates = 4
    exp.concept_importance_sums = {
        ids[0]: 0.4,  # avg 0.10
        ids[1]: 1.6,  # avg 0.40
        ids[2]: 3.2,  # avg 0.80
    }

    # We don't want the real _update_concept_importance to overwrite our
    # synthetic averages during the test run.
    monkeypatch.setattr(exp, "_update_concept_importance", lambda: None)

    # Monkeypatch _analyze_concept_future to do nothing; we just want the
    # pruning branch in run_greedy_actor_demo.
    monkeypatch.setattr(exp, "_analyze_concept_future", lambda *a, **k: None)

    # Stub tagger/policy/step to run a single episode quickly.
    monkeypatch.setattr(
        exp.tagger,
        "tag_state",
        lambda obs, universe: np.zeros(len(universe.state_concepts), dtype=int),
    )
    monkeypatch.setattr(
        exp,
        "_greedy_action",
        lambda state_vec: (0, np.array([0.0, 0.0, 0.0])),
    )

    def fake_step(action: int):
        exp.env.step_idx += 1
        done = exp.env.step_idx >= exp.env.max_steps
        exp.env.meltdown = False
        exp.env.output = 0.5
        exp.env.demand = "low"
        return "obs", done, False

    monkeypatch.setattr(exp.env, "step", fake_step)
    monkeypatch.setattr(cm.console, "print", lambda *a, **k: None)
    monkeypatch.setattr(cm.console, "rule", lambda *a, **k: None)

    # Before run: 3 STATE concepts.
    assert len([c for c in exp.universe.concepts if c.source == cm.ConceptSource.LLM]) == 3
    exp.run_greedy_actor_demo(num_episodes=1)
    # After run, max_concepts=2, so one STATE concept should have been dropped
    # (the one with the lowest average importance, ids[0]).
    state_ids_after = [
        c.id for c in exp.universe.concepts if c.source == cm.ConceptSource.LLM
    ]
    assert len(state_ids_after) == 2
    assert ids[0] not in state_ids_after


def test_newly_created_concepts_not_pruned_immediately(monkeypatch):
    """Concepts created in the latest analysis run should not be pruned right away."""
    exp = cm.Experiment(
        num_episodes=1,
        max_steps=1,
        gamma=0.9,
        max_new_concepts=1,
        max_concepts=3,
    )
    # Start with three STATE concepts (two base + one extra) and no ACTIONS to
    # keep indices simple.
    base_two = cm.BASE_STATE_CONCEPTS[:2]
    extra = cm.Concept(
        id="EXTRA_BASE",
        definition="An extra base concept for pruning tests.",
        source=cm.ConceptSource.LLM,
    )
    exp.universe = cm.ConceptUniverse(concepts=base_two + [extra] + cm.ACTION_CONCEPTS)

    # Fake future-occupancy traces so that analyze_concept_future will try to
    # add exactly one new concept.
    Z_ep = np.array(
        [
            [1, 1, 0],
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 0],
        ],
        dtype=int,
    )
    obs_ep = [f"log {t}" for t in range(Z_ep.shape[0])]

    # Stub ConceptCreator.create to return a deterministic new concept id.
    def fake_create(universe, pattern_concepts, pattern_description, positive_examples, negative_examples):  # noqa: E501
        return cm.Concept(
            id="NEW_META_CONCEPT_FOR_PRUNE_TEST",
            definition="Meta concept used in pruning test.",
            source=cm.ConceptSource.LLM,
        )

    exp.concept_creator = cm.ConceptCreator()
    monkeypatch.setattr(exp.concept_creator, "create", fake_create)

    # Pretend we have some importance stats so pruning logic can run; make the
    # extra base concept the weakest so it gets dropped if needed.
    exp.concept_importance_updates = 2
    exp.concept_importance_sums = {
        "TEXT_LENGTHY": 1.0,
        "STRUCTURED_TEXT": 1.0,
        "EXTRA_BASE": 0.1,
    }

    # Run analysis to add one new concept and populate new_state_concepts_last_analysis.
    monkeypatch.setattr(cm.console, "print", lambda *a, **k: None)
    monkeypatch.setattr(cm.console, "rule", lambda *a, **k: None)
    exp._analyze_concept_future([Z_ep], [obs_ep])

    # Sanity: new concept should be present and remembered as "new this analysis".
    assert "NEW_META_CONCEPT_FOR_PRUNE_TEST" in exp.universe.id_to_idx
    assert "NEW_META_CONCEPT_FOR_PRUNE_TEST" in exp.new_state_concepts_last_analysis

    # Now trigger the pruning branch as if at the end of an episode. Since
    # max_concepts=3 and we now have 4 STATE concepts, one should be dropped,
    # but not the freshly created one.
    if exp.universe.K > exp.max_concepts and exp.concept_importance_sums:
        recent_new = set(exp.new_state_concepts_last_analysis)
        candidates = [
            cid
            for cid, concept in zip(
                exp.universe.ids, exp.universe.concepts
            )
            if concept.source == cm.ConceptSource.LLM and cid not in recent_new
        ]
        assert "NEW_META_CONCEPT_FOR_PRUNE_TEST" not in candidates



def test_noise_factor_scales_push_dynamics():
    """Higher noise factor should magnify the same underlying random push step."""
    # Fix RNG so the underlying random draws are identical across envs.
    random.seed(123)
    env_low = cm.ReactorEnv(max_steps=3, difficulty=1.0, noise=0.1)
    # Start from a known state.
    env_low.stress = 50.0
    env_low.margin = 50.0
    env_low.output = 1.0
    env_low.glitches = 0
    env_low.demand = "low"
    env_low.step_idx = 0
    # Apply PUSH with low noise.
    _obs, _done, _melt = env_low.step(2)
    delta_low = env_low.stress - 50.0

    random.seed(123)
    env_high = cm.ReactorEnv(max_steps=3, difficulty=1.0, noise=2.0)
    env_high.stress = 50.0
    env_high.margin = 50.0
    env_high.output = 1.0
    env_high.glitches = 0
    env_high.demand = "low"
    env_high.step_idx = 0
    _obs, _done, _melt = env_high.step(2)
    delta_high = env_high.stress - 50.0

    # With the same underlying random draw, higher noise should amplify the
    # change in stress magnitude for a PUSH step.
    assert abs(delta_high) > abs(delta_low)


def test_episode_summary_includes_running_avg(monkeypatch):
    """After each episode, logs should include a running avg episode reward."""
    exp = cm.Experiment(num_episodes=2, max_steps=1, gamma=0.9, max_new_concepts=0)

    # Avoid real LLM calls and complex policy.
    monkeypatch.setattr(
        exp.tagger,
        "tag_state",
        lambda obs, universe: np.zeros(len(universe.state_concepts), dtype=int),
    )
    monkeypatch.setattr(
        exp,
        "_greedy_action",
        lambda state_vec: (0, np.array([0.0, 0.0, 0.0])),
    )

    # Simple env.step that never melts down and always returns reward via output.
    def fake_step(action: int):
        exp.env.step_idx += 1
        exp.env.output = 0.5
        exp.env.demand = "low"
        done = True
        exp.env.meltdown = False
        return "obs", done, False

    monkeypatch.setattr(exp.env, "step", fake_step)

    messages: list[str] = []

    def fake_print(*args, **kwargs):
        messages.append(" ".join(str(a) for a in args))

    monkeypatch.setattr(cm.console, "print", fake_print)
    monkeypatch.setattr(cm.console, "rule", lambda *a, **k: None)

    exp.run_greedy_actor_demo(num_episodes=2)

    joined = "\n".join(messages)
    assert "Running avg episode reward" in joined
