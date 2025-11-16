#!/usr/bin/env python
"""
Multi-step concept-learning world model with:

- Hidden numeric reactor env -> text observations only.
- Base STATE concepts tagged by an LLM (seed vocabulary).
- ACTION concepts in the same concept space, set by the env/policy.
- Discounted cumulative reward G_t (e.g. survival return).
- Single RewardModel: G_t ≈ f([STATE concepts_t, ACTION concepts_t]).
- Pairwise concept discovery using discounted reward ("fire together, wire together").
- ConceptCreator (LLM) that sees the full concept set and invents new STATE concepts.
- Re-tagging STATE concepts (base + learned) after schema update.
- Greedy actor that chooses actions by argmax predicted G_t (no LLM actor).

Requirements:
    pip install dspy-ai scikit-learn numpy pydantic

You must configure your OpenRouter key / base for DSPy separately, e.g.:

    export OPENROUTER_API_KEY=...
    # or via dspy.configure(lm=...)
"""

import random
from enum import Enum
from typing import List, Tuple, Optional

import numpy as np
from pydantic import BaseModel, Field
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

import dspy


# =========================
# 1. LM + CONCEPTS
# =========================

LM = dspy.LM(model="openrouter/deepseek/deepseek-v3.2-exp")
dspy.configure(lm=LM)


class ConceptSource(str, Enum):
    LLM = "llm"      # tagged from text by the LLM
    ENV = "env"      # set directly by environment/policy
    MODEL = "model"  # derived from a learned numeric model


class Concept(BaseModel):
    id: str = Field(..., description="Stable concept ID (e.g. 'STRAINED_CORE').")
    definition: str = Field(..., description="Short natural-language definition.")
    source: ConceptSource = Field(
        ConceptSource.LLM,
        description="Where this concept's activation comes from.",
    )


class ConceptUniverse:
    """Holds all concepts and provides indexing utilities."""
    def __init__(self, concepts: List[Concept]):
        self.concepts = concepts
        self.id_to_idx = {c.id: i for i, c in enumerate(concepts)}
        self.idx_to_id = {i: c.id for i, c in enumerate(concepts)}

    @property
    def ids(self) -> List[str]:
        return [c.id for c in self.concepts]

    @property
    def K(self) -> int:
        return len(self.concepts)

    @property
    def state_concepts(self) -> List[Concept]:
        """Concepts tagged by the LLM (STATE layer)."""
        return [c for c in self.concepts if c.source == ConceptSource.LLM]

    @property
    def state_ids(self) -> List[str]:
        return [c.id for c in self.state_concepts]

    def state_index_map(self) -> List[int]:
        """
        Map from 'state_concepts' indices to 'concepts' indices.
        Used if you want to embed STATE bits into the full concept space.
        """
        return [i for i, c in enumerate(self.concepts) if c.source == ConceptSource.LLM]


# --- Base STATE concepts (LLM-tagged) ---

BASE_STATE_CONCEPTS = [
    Concept(
        id="STRAINED_CORE",
        definition=(
            "The core is under unusually high internal stress, typically together with "
            "repeated small disturbances or glitches."
        ),
        source=ConceptSource.LLM,
    ),
    Concept(
        id="THIN_MARGIN",
        definition=(
            "Safety margins on the core are thin: the spare capacity or buffer is low, "
            "leaving little room for further stress."
        ),
        source=ConceptSource.LLM,
    ),
    Concept(
        id="STORMY_CHANNEL",
        definition=(
            "The energy channel is stormy: there have been several recent glitches or "
            "spikes in a short timespan."
        ),
        source=ConceptSource.LLM,
    ),
    Concept(
        id="AGITATED_OPERATOR",
        definition=(
            "The human operator is clearly agitated or upset, showing annoyance or anger "
            "about the system's behavior."
        ),
        source=ConceptSource.LLM,
    ),
    Concept(
        id="CRITICAL_MODE",
        definition=(
            "The overall situation is critical: the core is strained, safety margins are thin, "
            "and the operator is agitated, making a serious incident likely."
        ),
        source=ConceptSource.LLM,
    ),
]

# --- ACTION concepts (env/policy-sourced) ---

ACTION_CONCEPTS = [
    Concept(
        id="ACTION_STEADY",
        definition="The operator is holding controls steady, making no significant adjustment.",
        source=ConceptSource.ENV,
    ),
    Concept(
        id="ACTION_COOL",
        definition="The operator is nudging the controls toward cooling the core.",
        source=ConceptSource.ENV,
    ),
    Concept(
        id="ACTION_PUSH",
        definition="The operator is pushing the core harder to increase output.",
        source=ConceptSource.ENV,
    ),
]

# --- (Optional) MODEL-sourced reward concept definition (values derived later) ---

REWARD_CONCEPTS = [
    Concept(
        id="HIGH_VALUE",
        definition=(
            "The situation is expected to continue operating safely for many steps into the "
            "future under the chosen action."
        ),
        source=ConceptSource.MODEL,
    )
]

# Full initial universe: STATE + ACTION + (optional) MODEL-sourced reward concept.
BASE_UNIVERSE = ConceptUniverse(
    concepts=BASE_STATE_CONCEPTS + ACTION_CONCEPTS + REWARD_CONCEPTS
)


# =========================
# 2. ENVIRONMENT
# =========================

class ReactorEnv:
    """
    Multi-step reactor environment with hidden numeric state and a meltdown event.

    - Hidden variables: stress, margin, glitches, mood.
    - Actions: 0=steady, 1=cool, 2=push.
    - Meltdown if stress very high, margin very low, glitches high.
    - Emits ONLY text observations; numeric state and rules stay internal.
    """

    def __init__(self, max_steps: int = 10):
        self.max_steps = max_steps
        self.reset()

    def reset(self) -> str:
        self.stress = random.uniform(20, 60)
        self.margin = random.uniform(40, 80)
        self.glitches = 0
        self.mood = "calm"
        self.step_idx = 0
        self.meltdown = False
        return self._make_observation(last_action=None)

    def _update_mood(self):
        if self.stress < 60 and self.glitches < 2:
            self.mood = "calm"
        elif self.stress < 80 and self.glitches < 4:
            self.mood = "annoyed"
        else:
            self.mood = "furious"

    def _maybe_glitch(self):
        base_p = 0.05 + 0.003 * self.stress + 0.002 * max(0, 80 - self.margin)
        base_p = max(0.0, min(0.5, base_p / 100.0))
        if random.random() < base_p:
            self.glitches += 1
        else:
            if self.glitches > 0 and random.random() < 0.3:
                self.glitches -= 1

    def _check_meltdown(self):
        # Internal rule; never revealed externally.
        if self.stress > 92 and self.margin < 18 and self.glitches >= 3:
            self.meltdown = True

    def _make_observation(self, last_action: Optional[int]) -> str:
        if self.stress < 40:
            stress_phrase = "core stress index in a comfortable band"
        elif self.stress < 70:
            stress_phrase = "core stress index elevated but not alarming"
        else:
            stress_phrase = "core stress index pressing near the upper operating band"

        if self.margin < 20:
            margin_phrase = "flux margin is thin and shrinking"
        elif self.margin < 35:
            margin_phrase = "flux margin feels noticeably tight"
        else:
            margin_phrase = "flux margin appears healthy"

        if self.glitches == 0:
            glitch_phrase = "no shard glitches recorded in this cycle"
        elif self.glitches == 1:
            glitch_phrase = "a single minor shard glitch noted"
        elif self.glitches <= 3:
            glitch_phrase = f"{self.glitches} shard glitches in the last cycle"
        else:
            glitch_phrase = f"{self.glitches} shard glitches clustered in the last cycle"

        if self.mood == "calm":
            operator_msg = random.choice([
                "Readings look acceptable, just keeping an eye on the gauges.",
                "Everything feels stable enough for now.",
                "No major complaints, just monitoring the core.",
            ])
        elif self.mood == "annoyed":
            operator_msg = random.choice([
                "These spikes are getting annoying; this shouldn't wobble like that.",
                "I keep seeing little jumps in the readings; it's starting to bother me.",
                "The core keeps twitching, it's irritating.",
            ])
        else:
            operator_msg = random.choice([
                "This reactor is a mess; I'm sick of chasing these surges.",
                "If this core jumps again I'm filing a serious incident report.",
                "This is out of control, I'm furious we haven't shut it down.",
            ])

        if last_action is None:
            action_phrase = "No control adjustment yet this run."
        elif last_action == 0:
            action_phrase = "Operator holds controls steady."
        elif last_action == 1:
            action_phrase = "Operator nudges the controls toward cooling."
        else:
            action_phrase = "Operator pushes the core harder for more output."

        obs_lines = [
            f"Reactor log step {self.step_idx}: {stress_phrase}, {margin_phrase}, {glitch_phrase}.",
            f"{action_phrase}",
            f"Operator note: \"{operator_msg}\"",
        ]
        return " ".join(obs_lines)

    def step(self, action: int) -> Tuple[str, bool, bool]:
        """
        Apply action, update state, and return:
          observation: str
          done: bool
          meltdown: bool (if meltdown happened this step)
        """
        assert action in (0, 1, 2)
        self.step_idx += 1

        if action == 0:  # steady
            self.stress += random.uniform(-5, 5)
            self.margin += random.uniform(-3, 3)
        elif action == 1:  # cool
            self.stress += random.uniform(-12, 0)
            self.margin += random.uniform(2, 8)
        else:  # push
            self.stress += random.uniform(5, 15)
            self.margin += random.uniform(-10, 0)
            self.glitches += random.randint(0, 2)

        self.stress = max(0.0, min(100.0, self.stress))
        self.margin = max(0.0, min(100.0, self.margin))

        self._maybe_glitch()
        self._update_mood()
        self._check_meltdown()

        done = self.meltdown or (self.step_idx >= self.max_steps)
        obs = self._make_observation(last_action=action)
        return obs, done, self.meltdown


# =========================
# 3. TAGGER (STATE concepts only)
# =========================

class ConceptActivation(BaseModel):
    concept_id: str
    value: bool


class ConceptActivations(BaseModel):
    activations: List[ConceptActivation]


class TagConcepts(dspy.Signature):
    """
    Tag each STATE concept as true/false for a given observation.

    We pass only LLM-sourced concepts here (STATE layer).
    ACTION and MODEL concepts are filled in by env/model, not by the LLM.

    The model must return ONLY a JSON object matching the ConceptActivations schema:
      {"activations": [{"concept_id": "...", "value": 0 or 1}, ...]}.
    """
    observation: str = dspy.InputField()
    concepts: List[Concept] = dspy.InputField()
    labels_json: str = dspy.OutputField()


class LLMConceptTagger(dspy.Module):
    """One LLM call per observation → STATE concept bits only."""
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(TagConcepts)

    def tag_state(self, observation: str, universe: ConceptUniverse) -> np.ndarray:
        state_concepts = universe.state_concepts
        out = self.predict(observation=observation, concepts=state_concepts)
        activations = ConceptActivations.model_validate_json(out.labels_json)
        K_state = len(state_concepts)
        vec = np.zeros(K_state, dtype=int)
        # Map id -> index in state_concepts
        id_to_idx = {c.id: i for i, c in enumerate(state_concepts)}
        for act in activations.activations:
            if act.concept_id in id_to_idx:
                idx = id_to_idx[act.concept_id]
                vec[idx] = int(bool(act.value))
        return vec


# =========================
# 4. EPISODE DATASET & DISCOUNTED REWARD
# =========================

class EpisodeDataset:
    """
    Multi-step data + discounted reward.

    Stores:
      - observations (text)
      - episode_ids and step_indices
      - actions taken
      - meltdown flags & steps
      - Z_state: STATE concept activations (from LLM)
    """

    def __init__(self, gamma: float = 0.9):
        self.gamma = gamma
        self.observations: List[str] = []
        self.episode_ids: List[int] = []
        self.step_indices: List[int] = []
        self.meltdown_flags: List[bool] = []
        self.meltdown_steps: List[Optional[int]] = []
        self.actions: List[int] = []
        self.Z_state: Optional[np.ndarray] = None

    def simulate_random(self, env: ReactorEnv, num_episodes: int):
        """Collect episodes under a RANDOM behavior policy."""
        self.observations.clear()
        self.episode_ids.clear()
        self.step_indices.clear()
        self.meltdown_flags.clear()
        self.meltdown_steps.clear()
        self.actions.clear()

        for ep in range(num_episodes):
            env.reset()
            done = False
            step_idx = 0
            meltdown_step = None

            while not done:
                action = random.choice([0, 1, 2])
                obs, done, meltdown = env.step(action)

                self.observations.append(obs)
                self.episode_ids.append(ep)
                self.step_indices.append(step_idx)
                self.actions.append(action)

                if meltdown and meltdown_step is None:
                    meltdown_step = step_idx

                step_idx += 1

            self.meltdown_flags.append(meltdown_step is not None)
            self.meltdown_steps.append(meltdown_step)

    def tag_all_state(self, tagger: LLMConceptTagger, universe: ConceptUniverse):
        """Tag all observations with STATE concepts (LLM)."""
        n = len(self.observations)
        K_state = len(universe.state_concepts)
        Z = np.zeros((n, K_state), dtype=int)
        print("\n[LLM TAGGING] STATE concepts (id, source):")
        for c in universe.state_concepts:
            print(f"  - {c.id} [{c.source}]")
        for i, obs in enumerate(self.observations):
            print(f"\n[LLM TAG INPUT] obs_idx={i}")
            print(f"Observation: {obs}")
            vec = tagger.tag_state(obs, universe)
            Z[i, :] = vec
            activations_dict = {
                c.id: int(vec[j]) for j, c in enumerate(universe.state_concepts)
            }
            print(f"[LLM TAG OUTPUT] activations: {activations_dict}")
        self.Z_state = Z

    def build_discounted_reward(self) -> np.ndarray:
        """
        Build discounted cumulative reward G_t per step.

        Reward shaping:
          r_t = 1 for each step where the episode is alive (including last safe step),
          r_t = 0 at meltdown step (optional) — but we don't have steps AFTER meltdown.

        We compute returns per episode via:
          G_T-1 = r_T-1
          G_t   = r_t + gamma * G_{t+1}
        """
        assert self.Z_state is not None, "Call tag_all_state() before building reward."
        n = len(self.observations)
        G = np.zeros(n, dtype=float)

        # Map episode -> list of global indices for that episode
        ep_to_indices = {}
        for idx, ep in enumerate(self.episode_ids):
            ep_to_indices.setdefault(ep, []).append(idx)

        for ep, indices in ep_to_indices.items():
            # Sort by step index just in case
            indices_sorted = sorted(indices, key=lambda i: self.step_indices[i])
            T = len(indices_sorted)
            # Compute per-step rewards
            r = np.ones(T, dtype=float)
            # Optionally penalize meltdown step with 0
            if self.meltdown_flags[ep]:
                tau = self.meltdown_steps[ep]
                if tau is not None:
                    # find local index of meltdown step
                    for local_idx, global_idx in enumerate(indices_sorted):
                        if self.step_indices[global_idx] == tau:
                            r[local_idx] = 0.0
                            break
            # Discounted returns backwards
            G_local = np.zeros(T, dtype=float)
            G_local[-1] = r[-1]
            for t in reversed(range(T - 1)):
                G_local[t] = r[t] + self.gamma * G_local[t + 1]
            # Copy back
            for local_idx, global_idx in enumerate(indices_sorted):
                G[global_idx] = G_local[local_idx]

        return G

    def build_action_features(self, universe: ConceptUniverse) -> np.ndarray:
        """
        Construct X for RewardModel:

          X[i] = [STATE concept bits..., ACTION_STEADY, ACTION_COOL, ACTION_PUSH]

        STATE bits come from Z_state.
        ACTION bits are derived from self.actions.
        MODEL-sourced concepts (like HIGH_VALUE) are NOT used as inputs here (first pass).
        """
        assert self.Z_state is not None, "Call tag_all_state() before building features."
        n = len(self.observations)
        K_state = len(universe.state_concepts)
        A = 3  # steady, cool, push

        X = np.zeros((n, K_state + A), dtype=float)
        X[:, :K_state] = self.Z_state

        for i, a in enumerate(self.actions):
            if a in (0, 1, 2):
                X[i, K_state + a] = 1.0
        return X

    def train_test_split_by_episode(self, test_frac: float = 0.2):
        """Split indices into train/test sets by episode."""
        num_eps = len(self.meltdown_flags)
        eps = list(range(num_eps))
        random.shuffle(eps)
        split = int((1 - test_frac) * num_eps)
        train_eps = set(eps[:split])
        test_eps = set(eps[split:])

        train_idx = [i for i, ep in enumerate(self.episode_ids) if ep in train_eps]
        test_idx = [i for i, ep in enumerate(self.episode_ids) if ep in test_eps]
        return train_idx, test_idx


# =========================
# 5. REWARD MODEL
# =========================

class RewardModel:
    """
    Single model:
      features = [STATE concept bits, ACTION one-hot]
      target   = discounted cumulative reward G_t.
    """

    def __init__(self):
        self.model = LinearRegression()

    def fit(self, X: np.ndarray, G: np.ndarray, idx: List[int]):
        X_train = X[idx]
        y_train = G[idx]
        self.model.fit(X_train, y_train)

    def evaluate(self, X: np.ndarray, G: np.ndarray, idx: List[int], split_name: str):
        X_split = X[idx]
        y_split = G[idx]
        y_pred = self.model.predict(X_split)
        mse = mean_squared_error(y_split, y_pred)
        r2 = r2_score(y_split, y_pred)
        print(f"{split_name} Reward-MSE: {mse:.4f} | Reward-R^2: {r2:.3f}")
        return y_pred

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)


# =========================
# 6. CONCEPT CREATION (PAIRWISE, WITH FULL CONTEXT)
# =========================

class NewConceptSpec(BaseModel):
    id: str = Field(..., description="New concept ID in UPPER_SNAKE_CASE.")
    definition: str = Field(..., description="One-sentence abstract definition.")


class ProposeNewConcept(dspy.Signature):
    """
    Create a new, more abstract STATE concept from a pattern over existing concepts.

    Inputs:
      - all_concepts: the full current concept set (IDs + defs) for context.
      - pattern_concepts: the specific STATE concepts directly involved in the pattern.
      - pattern_description: text describing the pattern.
      - positive_examples: logs where pattern holds.
      - negative_examples: logs where it does not.

    Task:
      - Invent a new concept that captures the underlying situation in the positive
        examples and excludes the negative ones.
      - Concept should be more abstract than "A AND B"; don't just list IDs.
      - Output:
          * ID in UPPER_SNAKE_CASE, no spaces.
          * One-sentence definition (~<=25 tokens).
      - Do NOT mention hidden numeric rules or reward formulas.
    """
    all_concepts: List[Concept] = dspy.InputField()
    pattern_concepts: List[Concept] = dspy.InputField()
    pattern_description: str = dspy.InputField()
    positive_examples: List[str] = dspy.InputField()
    negative_examples: List[str] = dspy.InputField()
    new_concept: NewConceptSpec = dspy.OutputField()


class ConceptCreator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(ProposeNewConcept)

    def create(
        self,
        universe: ConceptUniverse,
        pattern_concepts: List[Concept],
        pattern_description: str,
        positive_examples: List[str],
        negative_examples: List[str],
    ) -> Concept:
        print("\n[LLM NEW-CONCEPT INPUT]")
        print("Pattern concepts:", [c.id for c in pattern_concepts])
        print("Pattern description:", pattern_description)
        if positive_examples:
            print("Positive examples (first 2):")
            for ex in positive_examples[:2]:
                print(f"  + {ex}")
        if negative_examples:
            print("Negative examples (first 2):")
            for ex in negative_examples[:2]:
                print(f"  - {ex}")
        out = self.predict(
            all_concepts=universe.concepts,
            pattern_concepts=pattern_concepts,
            pattern_description=pattern_description,
            positive_examples=positive_examples,
            negative_examples=negative_examples,
        )
        spec: NewConceptSpec = out.new_concept
        print("[LLM NEW-CONCEPT OUTPUT]", {"id": spec.id, "definition": spec.definition})
        return Concept(
            id=spec.id,
            definition=spec.definition,
            source=ConceptSource.LLM,  # new STATE concept, tagged by LLM in future
        )


class PairwiseConceptDiscovery:
    """
    Pairwise concept discovery from high-reward co-occurrences.

    Uses ONLY STATE concept activations (LLM layer) for the pattern,
    but passes the full universe to the LLM for context in naming.
    """

    def __init__(self, max_new: int = 2, min_support: float = 0.05):
        self.max_new = max_new
        self.min_support = min_support
        self.creator = ConceptCreator()

    def _score_pairs(
        self,
        state_concepts: List[Concept],
        Z_state: np.ndarray,
        G: np.ndarray,
    ) -> List[Tuple[float, float, int, int]]:
        """
        Score STATE concept pairs (i,j) by:

          support = P(C_i=1 & C_j=1)
          reward_pair = mean G over those steps

        Keep pairs with support >= min_support and reward_pair > global mean.
        """
        K_state = len(state_concepts)
        global_reward = float(G.mean()) if len(G) > 0 else 0.0
        candidates: List[Tuple[float, float, int, int]] = []

        for i in range(K_state):
            for j in range(i + 1, K_state):
                mask = (Z_state[:, i] == 1) & (Z_state[:, j] == 1)
                support = mask.mean()
                if support < self.min_support or mask.sum() == 0:
                    continue
                reward_pair = float(G[mask].mean()) if mask.sum() > 0 else 0.0
                if reward_pair <= global_reward:
                    continue
                candidates.append((reward_pair, support, i, j))

        candidates.sort(key=lambda x: -x[0])
        return candidates

    def discover(
        self,
        universe: ConceptUniverse,
        dataset: EpisodeDataset,
        G: np.ndarray,
    ) -> List[Tuple[Concept, Tuple[str, str]]]:
        assert dataset.Z_state is not None, "Need dataset.Z_state first."
        Z_state = dataset.Z_state
        state_concepts = universe.state_concepts

        candidates = self._score_pairs(state_concepts, Z_state, G)
        if not candidates:
            print("\nNo strong STATE concept pairs found for concept creation.")
            return []

        print("\n=== Concept creation: candidate STATE pairs (top few) ===")
        for reward_pair, support, i, j in candidates[:5]:
            print(
                f"Pair {state_concepts[i].id} & {state_concepts[j].id} | "
                f"support={support:.3f} | mean_discounted_reward={reward_pair:.3f}"
            )

        new_concepts_with_parents: List[Tuple[Concept, Tuple[str, str]]] = []
        used_ids = set(universe.ids)

        for reward_pair, support, i, j in candidates[: self.max_new]:
            cid_i = state_concepts[i].id
            cid_j = state_concepts[j].id

            print(
                f"\nCreating new STATE concept from pair {cid_i} & {cid_j} | "
                f"support={support:.3f} | mean_discounted_reward={reward_pair:.3f}"
            )

            mask_pos = (Z_state[:, i] == 1) & (Z_state[:, j] == 1)
            pos_idx = np.where(mask_pos)[0].tolist()

            mask_neg = ((Z_state[:, i] == 1) & (Z_state[:, j] == 0)) | (
                (Z_state[:, i] == 0) & (Z_state[:, j] == 1)
            )
            neg_idx = np.where(mask_neg)[0].tolist()
            if not neg_idx:
                mask_neg = (Z_state[:, i] == 0) & (Z_state[:, j] == 0)
                neg_idx = np.where(mask_neg)[0].tolist()

            if len(pos_idx) < 2 or len(neg_idx) < 2:
                print("  -> Too few positive/negative examples; skipping.")
                continue

            pos_examples = [dataset.observations[k] for k in pos_idx[:5]]
            neg_examples = [dataset.observations[k] for k in neg_idx[:5]]

            pattern_desc = (
                f"Situations where both {cid_i} and {cid_j} are true in the same log; "
                f"these co-occurrences tend to reflect especially important conditions."
            )
            pattern_concepts = [state_concepts[i], state_concepts[j]]

            new_c = self.creator.create(
                universe=universe,
                pattern_concepts=pattern_concepts,
                pattern_description=pattern_desc,
                positive_examples=pos_examples,
                negative_examples=neg_examples,
            )

            if new_c.id in used_ids:
                print(f"  -> Generated ID {new_c.id} already exists; skipping.")
                continue

            used_ids.add(new_c.id)
            new_concepts_with_parents.append((new_c, (cid_i, cid_j)))

            print("  -> New STATE concept created:")
            print(f"     id        : {new_c.id}")
            print(f"     definition: {new_c.definition}")

        if not new_concepts_with_parents:
            print("\nNo valid new concepts created from candidate pairs.")
        return new_concepts_with_parents


# =========================
# 7. EXPERIMENT + GREEDY ACTOR
# =========================

class Experiment:
    def __init__(
        self,
        num_episodes: int = 40,
        max_steps: int = 10,
        gamma: float = 0.9,
        max_new_concepts: int = 2,
    ):
        self.num_episodes = num_episodes
        self.env = ReactorEnv(max_steps=max_steps)
        self.universe = BASE_UNIVERSE  # includes STATE + ACTION + MODEL defs
        self.tagger = LLMConceptTagger()
        self.dataset = EpisodeDataset(gamma=gamma)
        self.reward_model = RewardModel()
        self.discovery = PairwiseConceptDiscovery(
            max_new=max_new_concepts,
            min_support=0.05,
        )

    def run(self):
        random.seed(42)
        np.random.seed(42)

        print(
            f"Simulating {self.num_episodes} episodes with up to "
            f"{self.env.max_steps} steps each (RANDOM actions)..."
        )
        self.dataset.simulate_random(self.env, num_episodes=self.num_episodes)
        n_steps_total = len(self.dataset.observations)
        print(f"Total steps collected: {n_steps_total}")

        # Tag with current STATE universe (initially base STATE concepts).
        print("\n[Pass 1] Tagging STATE concepts (one LLM call per step)...")
        self.dataset.tag_all_state(self.tagger, self.universe)

        print("\nBuilding discounted cumulative reward labels...")
        G = self.dataset.build_discounted_reward()

        train_idx, test_idx = self.dataset.train_test_split_by_episode(test_frac=0.2)
        print(f"Train steps: {len(train_idx)} | Test steps: {len(test_idx)}")

        # Pairwise concept discovery using discounted reward
        new_concepts_with_parents = self.discovery.discover(
            self.universe,
            self.dataset,
            G,
        )

        if new_concepts_with_parents:
            new_state_concepts = [nc for (nc, parents) in new_concepts_with_parents]

            # Extend universe with new STATE concepts while keeping ACTION/MODEL defs.
            extended_concepts = (
                self.universe.state_concepts
                + new_state_concepts
                + [c for c in self.universe.concepts if c.source != ConceptSource.LLM]
            )
            self.universe = ConceptUniverse(extended_concepts)

            print(
                f"\nExtended STATE space: {len(BASE_STATE_CONCEPTS)} base "
                f"+ {len(new_state_concepts)} learned = "
                f"{len(self.universe.state_concepts)} STATE concepts total"
            )

            # Re-tag STATE concepts with expanded schema
            print("\n[Pass 2] Re-tagging STATE concepts (one LLM call per step)...")
            self.dataset.tag_all_state(self.tagger, self.universe)
        else:
            print("\nNo new STATE concepts created; staying with base STATE concepts.")

        # Train RewardModel from STATE + ACTION concepts
        print("\n=== Reward model (STATE concepts + ACTION concepts -> discounted reward) ===")
        X_all = self.dataset.build_action_features(self.universe)
        self.reward_model.fit(X_all, G, train_idx)
        self.reward_model.evaluate(X_all, G, train_idx, "Train")
        self.reward_model.evaluate(X_all, G, test_idx, "Test")

        print("\nDone. Concept-learning + reward modeling complete.")
        print("Now running a greedy-actor demo using predicted cumulative reward per action...")
        self.run_greedy_actor_demo(num_episodes=3)

    def _greedy_action(self, state_vec: np.ndarray) -> Tuple[int, np.ndarray]:
        """
        Given current STATE concept bits c_t, evaluate RewardModel for each action
        and choose the action with highest predicted cumulative reward (argmax).
        """
        K_state = len(self.universe.state_concepts)
        A = 3
        X = np.zeros((A, K_state + A), dtype=float)
        for a in range(A):
            X[a, :K_state] = state_vec
            X[a, K_state + a] = 1.0  # ACTION concept bits
        preds = self.reward_model.predict(X)
        best_a = int(np.argmax(preds))  # maximize survival value
        return best_a, preds

    def run_greedy_actor_demo(self, num_episodes: int = 3):
        action_names = {0: "steady", 1: "cool", 2: "push"}

        print("\n=== Greedy Actor Demo (using RewardModel, actions & reward as concepts) ===")
        for ep in range(num_episodes):
            obs = self.env.reset()
            done = False
            step = 0
            meltdown_happened = False
            print(f"\nEpisode {ep}:")
            while not done:
                state_vec = self.tagger.tag_state(obs, self.universe)
                a, preds = self._greedy_action(state_vec)
                a_name = action_names.get(a, f"unknown({a})")
                print(
                    f"  step {step}: action={a_name} (raw={a}) | "
                    f"predicted_return_per_action={np.round(preds, 3)}"
                )

                obs, done, meltdown = self.env.step(a)
                if meltdown and not meltdown_happened:
                    meltdown_happened = True
                    print(f"    -> MELTDOWN at step {step}")
                step += 1

            if not meltdown_happened:
                print("    -> no meltdown in this episode (greedy actor run)")


# =========================
# 8. ENTRYPOINT
# =========================

def main():
    exp = Experiment(
        num_episodes=5,
        max_steps=10,
        gamma=0.9,
        max_new_concepts=2,
    )
    exp.run()


if __name__ == "__main__":
    main()
