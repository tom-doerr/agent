#!/usr/bin/env python
"""
Multi-step concept-learning world model with:

- Hidden numeric reactor env -> text observations only.
- STATE concepts tagged by an LLM (seed vocabulary, later extended).
- ACTION concepts in the same concept space, set by the env/policy.
- Discounted cumulative reward G_t (e.g. survival return).
- Single RewardModel: G_t ≈ f(full_concept_vector_t), where the vector contains:
    [STATE concept bits, ACTION concept bits, (optionally) MODEL concepts].
- Pairwise concept discovery using discounted reward ("fire together, wire together" on value).
- ConceptCreator (LLM) that sees the the full concept set and invents new STATE concepts.
- Re-tagging STATE concepts (base + learned) after schema update.
- Greedy actor that chooses actions by argmax predicted G_t (no LLM actor).

RL-wise this is:

- Monte-Carlo evaluation of a random behavior policy to get G_t targets.
- Supervised learning of a Q-like value model in concept space.
- Off-policy greedy control using that value model.

Requirements:
    pip install dspy-ai scikit-learn numpy pydantic

You must configure your OpenRouter key / base for DSPy separately, e.g.:

    export OPENROUTER_API_KEY=...
    # or via dspy.configure(lm=...)

File is self-contained: run it as

    python dspy_programs/concept_world_model_v3.py

to simulate, learn, and then run a greedy-actor demo.
"""

import argparse
import random
from enum import Enum
from typing import Dict, List, Optional, Tuple

import numpy as np
from pydantic import BaseModel, Field
from rich.console import Console
from rich.table import Table
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

import dspy


# =========================
# 1. LM + CONCEPTS
# =========================

# Rich console for pretty output
console = Console()

# Configure DSPy LM. Adjust the model string to whatever you actually use.
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
    """
    Holds all concepts and provides indexing utilities.

    The feature space is literally R^K where K = len(concepts).
    STATE concepts are tagged by the LLM; ACTION/MODEL concepts are filled
    deterministically by the environment or models.
    """

    def __init__(self, concepts: List[Concept]):
        self.concepts = concepts
        self.id_to_idx: Dict[str, int] = {c.id: i for i, c in enumerate(concepts)}
        self.idx_to_id: Dict[int, str] = {i: c.id for i, c in enumerate(concepts)}

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
        Used to embed STATE bits into the full concept space.
        """
        return [i for i, c in enumerate(self.concepts) if c.source == ConceptSource.LLM]


# --- Base STATE concepts (LLM-tagged) ---
# You *can* remove/replace these; they are just a seed vocabulary.
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

# --- MODEL-sourced reward concept definition (values derived later) ---

REWARD_CONCEPTS = [
    Concept(
        id="HIGH_VALUE",
        definition=(
            "The situation is expected to continue operating safely for many steps into the "
            "future under the chosen action (high predicted discounted return)."
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
    - Meltdown if stress very high, margin low, glitches high.
    - Emits ONLY text observations; numeric state and rules stay internal.

    This version is tuned so meltdowns are not ultra-rare, so the reward model
    actually sees interesting variation.
    """

    def __init__(self, max_steps: int = 15):
        self.max_steps = max_steps
        self.reset()

    def reset(self) -> str:
        # Start in a moderately safe-but-not-trivial regime
        self.stress = random.uniform(25, 60)
        self.margin = random.uniform(35, 80)
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
        """
        Increase glitch rate as stress rises and margin shrinks.
        Tuned to make meltdowns reasonably frequent in 10-20 step episodes.
        """
        stress_term = max(0.0, (self.stress - 40.0) / 50.0)  # 0..>1 above 40
        margin_term = max(0.0, (60.0 - self.margin) / 60.0)  # 0..>1 below 60
        base_p = 0.10 + 0.25 * stress_term + 0.25 * margin_term
        base_p = max(0.0, min(0.7, base_p))  # clamp

        if random.random() < base_p:
            self.glitches += 1
        else:
            # Occasional relaxation of glitches
            if self.glitches > 0 and random.random() < 0.3:
                self.glitches -= 1

    def _check_meltdown(self):
        # Deterministic meltdown rule; thresholds are deliberately moderate.
        if self.stress > 85 and self.margin < 25 and self.glitches >= 2:
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
            operator_msg = random.choice(
                [
                    "Readings look acceptable, just keeping an eye on the gauges.",
                    "Everything feels stable enough for now.",
                    "No major complaints, just monitoring the core.",
                ]
            )
        elif self.mood == "annoyed":
            operator_msg = random.choice(
                [
                    "These spikes are getting annoying; this shouldn't wobble like that.",
                    "I keep seeing little jumps in the readings; it's starting to bother me.",
                    "The core keeps twitching, it's irritating.",
                ]
            )
        else:
            operator_msg = random.choice(
                [
                    "This reactor is a mess; I'm sick of chasing these surges.",
                    "If this core jumps again I'm filing a serious incident report.",
                    "This is out of control, I'm furious we haven't shut it down.",
                ]
            )

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
          observation: str  (AFTER applying action)
          done: bool
          meltdown: bool (if meltdown happened this step)
        """
        assert action in (0, 1, 2)
        self.step_idx += 1

        # Dynamics tuned so PUSH tends to drive toward meltdown,
        # COOL tends to move away, STEADY dithers.
        if action == 0:  # steady
            self.stress += random.uniform(-4, 6)
            self.margin += random.uniform(-4, 4)
        elif action == 1:  # cool
            self.stress += random.uniform(-14, -1)
            self.margin += random.uniform(2, 10)
        else:  # push
            self.stress += random.uniform(6, 18)
            self.margin += random.uniform(-12, 1)
            self.glitches += random.randint(0, 2)

        # Time drift: later steps are intrinsically harder
        drift = self.step_idx / max(self.max_steps, 1)
        self.stress += 2.0 * drift
        self.margin -= 2.0 * drift

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

    Inputs:
      - observation: a single reactor text log.
      - concepts: the list of STATE concepts to tag, each with id + definition.

    Output:
      - activations_json: a JSON object matching the ConceptActivations schema:
          {"activations": [{"concept_id": "...", "value": 0 or 1}, ...]}.
        For each input concept, you MUST output exactly one activation, with:
          - concept_id: EXACTLY one of the given concept ids.
          - value: true if the concept is clearly present in the observation,
                   false otherwise.

    Do NOT invent new concept ids. If unsure, default to false.
    """

    observation: str = dspy.InputField(
        desc="A single reactor log observation (state + last action + operator note)."
    )
    concepts: List[Concept] = dspy.InputField(
        desc="List of STATE concept objects with 'id' and 'definition'."
    )
    activations_json: str = dspy.OutputField(
        desc=(
            "JSON string matching ConceptActivations: "
            '{"activations": [{"concept_id": "...", "value": 0 or 1}, ...]}.'
        )
    )


class LLMConceptTagger(dspy.Module):
    """One LLM call per observation → STATE concept bits only."""

    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(TagConcepts)

    def tag_state(self, observation: str, universe: ConceptUniverse) -> np.ndarray:
        """
        Returns an array of shape (K_state,) with 0/1 bits for each STATE concept
        in universe.state_concepts, in that order.
        """
        state_concepts = universe.state_concepts
        out = self.predict(observation=observation, concepts=state_concepts)
        activations = ConceptActivations.model_validate_json(out.activations_json)
        K_state = len(state_concepts)
        vec = np.zeros(K_state, dtype=int)
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
      - observations (text) at decision time (PRE-action).
      - episode_ids and step_indices.
      - actions taken.
      - meltdown flags & steps per episode.
      - Z_state: STATE concept activations (from LLM).

    Reward is Monte-Carlo survival-based:

      r_t = 1  while the system is alive,
      r_t = 0  at the meltdown-causing decision step (optional penalty).

    G_t is discounted return:

      G_T-1 = r_T-1
      G_t   = r_t + gamma * G_{t+1}
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
        """
        Collect episodes under a RANDOM behavior policy.

        IMPORTANT: we store observation BEFORE taking the action, so that
        (obs_t, action_t) pairs line up with G_t and can be used as Q(s_t, a_t)
        training data.
        """
        self.observations.clear()
        self.episode_ids.clear()
        self.step_indices.clear()
        self.meltdown_flags.clear()
        self.meltdown_steps.clear()
        self.actions.clear()
        self.Z_state = None

        for ep in range(num_episodes):
            obs = env.reset()
            done = False
            step_idx = 0
            meltdown_step: Optional[int] = None

            while not done:
                # Store PRE-action observation
                self.observations.append(obs)
                self.episode_ids.append(ep)
                self.step_indices.append(step_idx)

                action = random.choice([0, 1, 2])
                self.actions.append(action)

                obs, done, meltdown = env.step(action)

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
        print("\n[LLM TAGGING v3] STATE concepts (id, source):")
        for c in universe.state_concepts:
            print(f"  - {c.id} [{c.source}]")
        for i, obs in enumerate(self.observations):
            print(f"\n[LLM TAG INPUT v3] obs_idx={i}")
            print(f"Observation: {obs}")
            vec = tagger.tag_state(obs, universe)
            Z[i, :] = vec
            activations_dict = {
                c.id: int(vec[j]) for j, c in enumerate(universe.state_concepts)
            }
            print(f"[LLM TAG OUTPUT v3] activations: {activations_dict}")
        self.Z_state = Z

    def build_discounted_reward(self) -> np.ndarray:
        """
        Build discounted cumulative reward G_t per step.

        Reward shaping:
          r_t = 1 for each decision step where the episode is still alive,
          r_t = 0 at the meltdown-causing decision step (no future terms anyway).

        We compute returns per episode via:
          G_T-1 = r_T-1
          G_t   = r_t + gamma * G_{t+1}
        """
        assert self.Z_state is not None, "Call tag_all_state() before building reward."
        n = len(self.observations)
        G = np.zeros(n, dtype=float)

        # Map episode -> list of global indices for that episode
        ep_to_indices: Dict[int, List[int]] = {}
        for idx, ep in enumerate(self.episode_ids):
            ep_to_indices.setdefault(ep, []).append(idx)

        for ep, indices in ep_to_indices.items():
            indices_sorted = sorted(indices, key=lambda i: self.step_indices[i])
            T = len(indices_sorted)
            r = np.ones(T, dtype=float)
            if self.meltdown_flags[ep]:
                tau = self.meltdown_steps[ep]
                if tau is not None:
                    for local_idx, global_idx in enumerate(indices_sorted):
                        if self.step_indices[global_idx] == tau:
                            r[local_idx] = 0.0
                            break
            G_local = np.zeros(T, dtype=float)
            G_local[-1] = r[-1]
            for t in reversed(range(T - 1)):
                G_local[t] = r[t] + self.gamma * G_local[t + 1]
            for local_idx, global_idx in enumerate(indices_sorted):
                G[global_idx] = G_local[local_idx]

        return G

    def build_action_features(self, universe: ConceptUniverse) -> np.ndarray:
        """
        Construct full concept vector X for RewardModel.

          X[i] lives in R^K where K = universe.K.

        We:
          - Insert STATE concept bits at the indices corresponding to LLM concepts.
          - Set exactly one ACTION concept bit (STEADY/COOL/PUSH) per step.
          - MODEL-sourced concepts (like HIGH_VALUE) are NOT used as inputs
            in training; they could be filled later from the reward model if desired.
        """
        assert self.Z_state is not None, "Call tag_all_state() before building features."
        n = len(self.observations)
        K = universe.K
        X = np.zeros((n, K), dtype=float)

        state_indices = universe.state_index_map()
        if len(state_indices) != self.Z_state.shape[1]:
            raise ValueError(
                "Mismatch between number of STATE concepts in universe "
                "and columns of Z_state."
            )
        X[:, state_indices] = self.Z_state

        action_ids = ["ACTION_STEADY", "ACTION_COOL", "ACTION_PUSH"]
        for i, a in enumerate(self.actions):
            if a not in (0, 1, 2):
                continue
            cid = action_ids[a]
            if cid not in universe.id_to_idx:
                raise KeyError(f"Universe missing action concept {cid}")
            j = universe.id_to_idx[cid]
            X[i, j] = 1.0

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
    Single model on full concept vectors:

      X_t = full_concept_vector(s_t, a_t)
      target = discounted cumulative reward G_t.

    With our construction, this is effectively a Q^{pi_random}(s, a) approximator
    in the concept space (Monte-Carlo evaluation).
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
      - Concept should be more abstract than just "A AND B"; don't just list IDs.
      - Output:
          * ID in UPPER_SNAKE_CASE, no spaces.
          * One-sentence definition (~<=25 tokens).
      - Do NOT mention hidden numeric rules or reward formulas.
      - Do NOT reuse any existing concept id.
    """

    all_concepts: List[Concept] = dspy.InputField(
        desc="Full current concept set (STATE, ACTION, MODEL)."
    )
    pattern_concepts: List[Concept] = dspy.InputField(
        desc="STATE concepts directly involved in the high-reward pattern."
    )
    pattern_description: str = dspy.InputField(
        desc="Short description of the pattern we want to abstract."
    )
    positive_examples: List[str] = dspy.InputField(
        desc="Example logs where the pattern holds."
    )
    negative_examples: List[str] = dspy.InputField(
        desc="Example logs where the pattern does NOT hold."
    )
    new_concept: NewConceptSpec = dspy.OutputField(
        desc="New concept spec with id + definition."
    )


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
        print("\n[LLM NEW-CONCEPT INPUT v3]")
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
        print("[LLM NEW-CONCEPT OUTPUT v3]", {"id": spec.id, "definition": spec.definition})
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
        num_episodes: int = 15,
        max_steps: int = 15,
        gamma: float = 0.9,
        max_new_concepts: int = 2,
        eps_greedy: float = 0.0,
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
        self.eps_greedy = eps_greedy

    def run(self):
        random.seed(42)
        np.random.seed(42)

        console.rule("[bold cyan]Warmup: Random Policy (1 episode)[/bold cyan]")

        # Hard-coded warmup: collect exactly one random-policy episode for training.
        console.print(
            f"[cyan]Simulating 1 warmup episode with up to[/cyan] "
            f"{self.env.max_steps} [cyan]steps each (RANDOM actions)...[/cyan]"
        )
        self.dataset.simulate_random(self.env, num_episodes=1)
        n_steps_total = len(self.dataset.observations)
        console.print(f"[cyan]Total decision steps collected:[/cyan] {n_steps_total}")

        console.rule("[bold cyan]Pass 1: Tag STATE Concepts[/bold cyan]")
        console.print("[cyan]Tagging STATE concepts (one LLM call per step)...[/cyan]")
        self.dataset.tag_all_state(self.tagger, self.universe)

        console.rule("[bold cyan]Monte-Carlo Returns[/bold cyan]")
        console.print("[cyan]Building discounted cumulative reward labels (G_t)...[/cyan]")
        G = self.dataset.build_discounted_reward()

        # Baseline: random policy discounted return stats
        num_eps = len(self.dataset.meltdown_flags)
        num_meltdowns = sum(1 for f in self.dataset.meltdown_flags if f)
        meltdown_rate = num_meltdowns / num_eps if num_eps > 0 else 0.0
        console.rule("[bold magenta]Baseline: Random Policy (Behavior)[/bold magenta]")
        console.print(
            f"[magenta]Episodes:[/magenta] {num_eps}  |  "
            f"[magenta]Meltdowns:[/magenta] {num_meltdowns}  |  "
            f"[magenta]Meltdown rate:[/magenta] {meltdown_rate:.3f}"
        )

        self.baseline_overall_mean = float(G.mean()) if len(G) > 0 else 0.0
        self.baseline_action_means: Dict[int, float] = {}
        action_names = {0: "steady", 1: "cool", 2: "push"}
        table = Table(title="Baseline action returns (random policy)")
        table.add_column("Action", justify="left")
        table.add_column("Mean G_t", justify="right")
        table.add_column("# Steps", justify="right")
        for a in (0, 1, 2):
            idxs = [i for i, act in enumerate(self.dataset.actions) if act == a]
            if not idxs:
                table.add_row(action_names[a], "—", "0")
                continue
            mean_g = float(G[idxs].mean())
            self.baseline_action_means[a] = mean_g
            table.add_row(action_names[a], f"{mean_g:.3f}", str(len(idxs)))
        console.print(table)

        train_idx, test_idx = self.dataset.train_test_split_by_episode(test_frac=0.2)
        console.rule("[bold cyan]Train / Test Split[/bold cyan]")
        console.print(
            f"[cyan]Train steps:[/cyan] {len(train_idx)}  |  "
            f"[cyan]Test steps:[/cyan] {len(test_idx)}"
        )

        new_concepts_with_parents = self.discovery.discover(
            self.universe,
            self.dataset,
            G,
        )

        if new_concepts_with_parents:
            new_state_concepts = [nc for (nc, _) in new_concepts_with_parents]
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

            print("\n[Pass 2] Re-tagging STATE concepts (one LLM call per step)...")
            self.dataset.tag_all_state(self.tagger, self.universe)
        else:
            print("\nNo new STATE concepts created; staying with base STATE concepts.")

        print("\n=== Reward model (concept vector -> discounted return) ===")
        X_all = self.dataset.build_action_features(self.universe)
        if not train_idx:
            console.print(
                "[bold red]No train steps available (warmup episode too small); "
                "skipping RewardModel training and greedy demo.[/bold red]"
            )
            return
        self.reward_model.fit(X_all, G, train_idx)
        self.reward_model.evaluate(X_all, G, train_idx, "Train")
        self.reward_model.evaluate(X_all, G, test_idx, "Test")

        print("\nDone. Concept-learning + reward modeling complete.")
        print("Now running a greedy-actor demo using predicted cumulative reward per action...")
        self.run_greedy_actor_demo(num_episodes=self.num_episodes)

    def _greedy_action(self, state_vec_state_only: np.ndarray) -> Tuple[int, np.ndarray]:
        """
        Given current STATE concept bits c_t (shape (K_state,)), embed into full concept
        vector, evaluate RewardModel for each ACTION concept, and choose the action
        with highest predicted cumulative reward (argmax).
        """
        K_state = len(self.universe.state_concepts)
        if state_vec_state_only.shape[0] != K_state:
            raise ValueError("STATE vector length does not match universe STATE count.")

        K = self.universe.K
        full_state = np.zeros(K, dtype=float)
        state_indices = self.universe.state_index_map()
        full_state[state_indices] = state_vec_state_only

        action_ids = ["ACTION_STEADY", "ACTION_COOL", "ACTION_PUSH"]
        A = len(action_ids)
        preds = np.zeros(A, dtype=float)

        for a in range(A):
            x = full_state.copy()
            for cid in action_ids:
                j = self.universe.id_to_idx[cid]
                x[j] = 0.0
            cid_a = action_ids[a]
            j_a = self.universe.id_to_idx[cid_a]
            x[j_a] = 1.0
            preds[a] = self.reward_model.predict(x[None, :])[0]

        best_a = int(np.argmax(preds))
        return best_a, preds

    def run_greedy_actor_demo(self, num_episodes: int = 3):
        action_names = {0: "steady", 1: "cool", 2: "push"}

        console.rule("[bold green]Greedy Actor Demo (using RewardModel)[/bold green]")
        baseline_overall = getattr(self, "baseline_overall_mean", 0.0)
        baseline_action_means = getattr(self, "baseline_action_means", {})
        total_reward = 0.0
        total_steps = 0

        for ep in range(num_episodes):
            obs = self.env.reset()
            done = False
            step = 0
            meltdown_happened = False
            ep_reward = 0.0
            ep_steps = 0
            console.print(f"\n[bold green]Episode {ep}[/bold green]:")
            while not done:
                state_vec = self.tagger.tag_state(obs, self.universe)
                a, preds = self._greedy_action(state_vec)
                # Epsilon-greedy exploration: with probability eps_greedy, override
                # the greedy choice with a random action.
                explore = random.random() < getattr(self, "eps_greedy", 0.0)
                if explore:
                    a = random.choice([0, 1, 2])
                a_name = action_names.get(a, f"unknown({a})")
                obs, done, meltdown = self.env.step(a)
                reward = 0.0 if meltdown else 1.0
                ep_reward += reward
                ep_steps += 1
                total_reward += reward
                total_steps += 1

                avg_reward_global = total_reward / total_steps if total_steps else 0.0
                avg_reward_ep = ep_reward / ep_steps if ep_steps else 0.0

                base_means = [
                    baseline_action_means.get(i, float("nan")) for i in (0, 1, 2)
                ]

                console.print(
                    f"  [white]step {step}[/white]: "
                    f"[bold]action[/bold]={a_name} (raw={a}) | "
                    f"[cyan]predicted_return_per_action[/cyan]={np.round(preds, 3)} | "
                    f"[magenta]baseline_mean_G[/magenta]={baseline_overall:.3f} | "
                    f"[magenta]baseline_action_means[/magenta]={np.round(base_means, 3)} | "
                    f"[yellow]avg_reward_global[/yellow]={avg_reward_global:.3f} | "
                    f"[yellow]avg_reward_episode[/yellow]={avg_reward_ep:.3f}"
                )

                if meltdown and not meltdown_happened:
                    meltdown_happened = True
                    console.print(f"    [bold red]-> MELTDOWN at step {step}[/bold red]")
                step += 1

            if not meltdown_happened:
                console.print("    [green]-> no meltdown in this episode (greedy actor run)[/green]")


# =========================
# 8. ENTRYPOINT
# =========================


def main(argv: Optional[List[str]] = None):
    parser = argparse.ArgumentParser(
        description="Concept-world RL experiment with DSPy-tagged concepts."
    )
    parser.add_argument(
        "--episodes",
        "--epochs",
        type=int,
        default=5,
        help="Number of episodes to simulate under the random behavior policy (default: 5).",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=12,
        help="Maximum steps per episode (default: 12).",
    )
    parser.add_argument(
        "--gamma",
        type=float,
        default=0.9,
        help="Discount factor for returns G_t (default: 0.9).",
    )
    parser.add_argument(
        "--max-new-concepts",
        type=int,
        default=2,
        help="Maximum number of new STATE concepts to create from high-value pairs (default: 2).",
    )
    parser.add_argument(
        "--epsilon",
        type=float,
        default=0.0,
        help="Epsilon for epsilon-greedy exploration during greedy actor runs (default: 0.0).",
    )

    args = parser.parse_args(argv)

    exp = Experiment(
        num_episodes=args.episodes,
        max_steps=args.max_steps,
        gamma=args.gamma,
        max_new_concepts=args.max_new_concepts,
        eps_greedy=args.epsilon,
    )
    exp.run()


if __name__ == "__main__":
    main()
