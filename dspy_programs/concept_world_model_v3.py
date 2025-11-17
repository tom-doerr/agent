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
import math
import random
from enum import Enum
from typing import Dict, List, Optional, Tuple

import numpy as np
from pydantic import BaseModel, Field, ValidationError
from rich.console import Console
from rich.table import Table
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge, Lasso
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import mean_squared_error, r2_score

import dspy


# =========================
# 1. LM + CONCEPTS
# =========================

# Rich console for pretty output
console = Console()

# Default LM: Gemini 2.5 Flash via OpenRouter
DEFAULT_LM_MODEL = "openrouter/google/gemini-2.5-flash"
LM = dspy.LM(model=DEFAULT_LM_MODEL)
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
# Seed vocabulary is intentionally simple and text-centric so it can transfer
# to other worlds: length, structure, tone, symbols.
BASE_STATE_CONCEPTS = [
    Concept(
        id="TEXT_LENGTHY",
        definition="The log text is long (many words/clauses).",
        source=ConceptSource.LLM,
    ),
    Concept(
        id="STRUCTURED_TEXT",
        definition="The text looks structured (lists, sections, repeated patterns).",
        source=ConceptSource.LLM,
    ),
    Concept(
        id="TECHNICAL_TONE",
        definition="The text sounds technical or formal (numbers, units, jargon).",
        source=ConceptSource.LLM,
    ),
    Concept(
        id="SPECIAL_SYMBOLS",
        definition=(
            "The text contains special symbols beyond letters/digits "
            "(brackets, hashes, unusual punctuation)."
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

    def __init__(self, max_steps: int = 15, difficulty: float = 1.0, noise: float = 1.0):
        self.max_steps = max_steps
        # Base difficulty scales how unstable the reactor is. We derive a
        # current_difficulty from this and the step index so that difficulty
        # ramps up within an episode but resets when the episode resets.
        self.difficulty = max(0.1, difficulty)
        # Global noise factor that scales stochastic dynamics; 0.0 means
        # deterministic updates from the drift terms only, >1.0 amplifies
        # randomness.
        self.noise = max(0.0, noise)
        self.reset()

    def reset(self) -> str:
        # Start in a moderately safe-but-not-trivial regime
        self.stress = random.uniform(25, 60)
        self.margin = random.uniform(35, 80)
        self.glitches = 0
        self.mood = "calm"
        self.demand = random.choice(["low", "high"])
        # Continuous reactor output level (0≈off, 1≈nominal, >1≈overdrive).
        self.output = random.uniform(0.5, 1.0)
        self.step_idx = 0
        self.meltdown = False
        return self._make_observation(last_action=None)

    def current_difficulty(self) -> float:
        """Difficulty ramp that increases with step index and resets each episode."""
        progress = self.step_idx / max(self.max_steps, 1)
        return self.difficulty * (1.0 + progress)

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
        base_p *= self.current_difficulty() * max(self.noise, 0.0)
        base_p = max(0.0, min(0.7, base_p))  # clamp

        if random.random() < base_p:
            self.glitches += 1
        else:
            # Occasional relaxation of glitches
            if self.glitches > 0 and random.random() < 0.3:
                self.glitches -= 1

    def _check_meltdown(self):
        # Deterministic meltdown rule; tuned so meltdowns are not ultra-rare.
        # Make meltdown more likely by lowering the stress threshold,
        # relaxing the margin constraint, and requiring fewer glitches.
        # Higher current_difficulty tightens thresholds slightly; lower loosens them.
        cur = self.current_difficulty()
        stress_thresh = 80.0 - 5.0 * (cur - 1.0)
        margin_thresh = 35.0 + 5.0 * (cur - 1.0)
        if self.stress > stress_thresh and self.margin < margin_thresh and self.glitches >= 1:
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

        if self.demand == "low":
            demand_phrase = "grid demand is modest"
        else:
            demand_phrase = (
                "grid demand is elevated; operators are asked to keep output up"
            )

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

        # Indirectly hint at reactor power via steam/turbine behavior so the
        # operator note carries a soft signal about output without quoting
        # numbers.
        if self.output < 0.4:
            output_phrase = "The steam output feels anemic; turbines are barely loaded."
        elif self.output < 0.9:
            output_phrase = "Steam output feels normal; turbines hum steadily."
        else:
            output_phrase = "Steam output is heavy; turbines are straining a bit."

        operator_msg_full = (
            f"{operator_msg} {output_phrase} "
            f"(measured reactor output={self.output:.3f})."
        )

        if last_action is None:
            action_phrase = "No control adjustment yet this run."
        elif last_action == 0:
            action_phrase = "Operator holds controls steady."
        elif last_action == 1:
            action_phrase = "Operator nudges the controls toward cooling."
        else:
            action_phrase = "Operator pushes the core harder for more output."

        # Red blinking warning light when the reactor operates in a risky band.
        # Keep it simple: treat high stress/low margin or many glitches as the
        # trigger and describe it textually.
        if (self.stress > 80 and self.margin < 35) or self.glitches >= 3:
            light_phrase = "A red warning light blinks on the console."
        else:
            light_phrase = ""

        obs_lines = [
            f"Reactor log step {self.step_idx}: {stress_phrase}, {margin_phrase}, {glitch_phrase}.",
            demand_phrase,
            f"{action_phrase}",
            f"Operator note: \"{operator_msg_full}\"",
        ]
        if light_phrase:
            obs_lines.append(light_phrase)
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
            self.stress += random.uniform(-4, 6) * self.noise
            self.margin += random.uniform(-4, 4) * self.noise
            # Hold output roughly steady with a little noise.
            self.output += random.uniform(-0.05, 0.05) * self.noise
        elif action == 1:  # cool
            self.stress += random.uniform(-14, -1) * self.noise
            self.margin += random.uniform(2, 10) * self.noise
            # Cooling reduces output, with some randomness.
            self.output += random.uniform(-0.25, -0.05) * self.noise
        else:  # push
            self.stress += random.uniform(6, 18) * self.noise
            self.margin += random.uniform(-12, 1) * self.noise
            self.glitches += random.randint(0, 2)
            # Pushing increases output, with some randomness.
            self.output += random.uniform(0.05, 0.25) * self.noise

        # Time drift: later steps are intrinsically harder
        drift = self.step_idx / max(self.max_steps, 1)
        cur = self.current_difficulty()
        self.stress += 2.0 * drift * cur
        self.margin -= 2.0 * drift * cur

        self.stress = max(0.0, min(100.0, self.stress))
        self.margin = max(0.0, min(100.0, self.margin))
        # Clamp output to a reasonable band.
        self.output = max(0.0, min(2.0, self.output))

        # Occasionally flip demand to simulate changing grid needs.
        p_flip = min(1.0, max(0.0, 0.2 * self.noise))
        if random.random() < p_flip:
            self.demand = "high" if self.demand == "low" else "low"

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
      - activations: a structured object matching the ConceptActivations schema:
          {"activations": [{"concept_id": "...", "value": true/false}, ...]}.
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
    activations: ConceptActivations = dspy.OutputField(
        desc="Structured ConceptActivations object for the given concepts."
    )


class LLMConceptTagger(dspy.Module):
    """One LLM call per observation → STATE concept bits only."""

    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(TagConcepts)

    def tag_state(self, observation: str, universe: ConceptUniverse) -> np.ndarray:
        """
        Returns an array of shape (K_state,) with values in {-1, 0, 1} for each
        STATE concept in universe.state_concepts, in that order:

          - 1  → concept clearly present in the observation
          - -1 → concept clearly absent
          - 0  → missing / no information (e.g. concept added after this data)
        """
        state_concepts = universe.state_concepts
        out = self.predict(observation=observation, concepts=state_concepts)
        try:
            # Allow either a ConceptActivations instance, a dict-like object,
            # or a JSON string; Pydantic will validate/convert accordingly.
            activations = ConceptActivations.model_validate(out.activations)
        except ValidationError as exc:
            console.rule(
                "[bold red]Pydantic validation error in LLM TAG OUTPUT (ConceptActivations)[/bold red]"
            )
            console.print(
                "[red]Failed to parse ConceptActivations from 'activations' output.[/red]"
            )
            console.print(f"[red]Raw activations output:[/red] {getattr(out, 'activations', None)!r}")
            console.print(exc)
            raise
        K_state = len(state_concepts)
        vec = np.zeros(K_state, dtype=int)
        id_to_idx = {c.id: i for i, c in enumerate(state_concepts)}
        for act in activations.activations:
            if act.concept_id in id_to_idx:
                idx = id_to_idx[act.concept_id]
                vec[idx] = 1 if bool(act.value) else -1
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
        # Use a simple linear model with mild L2 regularization.
        self.model = Ridge(alpha=0.1)
        self.n_features: Optional[int] = None

    def fit(self, X: np.ndarray, G: np.ndarray, idx: List[int]):
        X_train = X[idx]
        y_train = G[idx]
        self.model.fit(X_train, y_train)
        self.n_features = X_train.shape[1]

    def evaluate(self, X: np.ndarray, G: np.ndarray, idx: List[int], split_name: str):
        X_split = X[idx]
        y_split = G[idx]
        y_pred = self.model.predict(X_split)
        mse = mean_squared_error(y_split, y_pred)
        r2 = r2_score(y_split, y_pred)
        print(f"{split_name} Reward-MSE: {mse:.4f} | Reward-R^2: {r2:.3f}")
        return y_pred

    def predict(self, X: np.ndarray) -> np.ndarray:
        # If the concept space has grown since the last fit, pad/truncate
        # inputs to the learned feature dimension rather than resetting the
        # model. New concepts effectively behave as zero-features until a
        # refit happens with the larger space.
        if self.n_features is not None:
            if X.shape[1] > self.n_features:
                X = X[:, : self.n_features]
            elif X.shape[1] < self.n_features:
                pad = np.zeros((X.shape[0], self.n_features - X.shape[1]), dtype=X.dtype)
                X = np.hstack([X, pad])
            return self.model.predict(X)
        # Not fitted yet: behave like a zero model.
        return np.zeros(X.shape[0], dtype=float)


# =========================
# 6. CONCEPT CREATION (PAIRWISE, WITH FULL CONTEXT)
# =========================


class NewConceptSpec(BaseModel):
    id: str = Field(..., description="New concept ID in UPPER_SNAKE_CASE.")
    definition: str = Field(..., description="One-sentence abstract definition.")


class ProposeNewConcept(dspy.Signature):
    """
    Create a new, more abstract STATE concept that explains a pattern over existing concepts.

    Inputs:
      - all_concepts: the full current concept set (IDs + defs) for context.
      - pattern_concepts: the specific STATE concepts directly involved in the pattern.
      - pattern_description: text describing the pattern.
      - positive_examples: logs where pattern holds.
      - negative_examples: logs where it does not.

    Task:
      - Invent a new concept that captures a plausible underlying situation or cause
        that makes the pattern_concepts tend to be true together in the positive
        examples and not in the negative ones.
      - Concept should be more abstract than just "A AND B"; do NOT simply restate
        or conjoin the input concept names. Describe a latent condition that could
        generate their correlation.
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
        desc=(
            "STATE concepts directly involved in the high-value, highly correlated "
            "pattern we want to explain."
        )
    )
    pattern_description: str = dspy.InputField(
        desc="Short description of the correlated pattern we want to explain."
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
                "Situations where both "
                f"{cid_i} and {cid_j} are true in the same log, and their "
                "discounted future-occupancy weights are strongly correlated. "
                "Explain a single underlying situation or cause that would make "
                "both of these concepts tend to be true together in those cases."
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
        corr_threshold: float = 0.0,
        difficulty: float = 1.0,
        max_concepts: int = 10,
        noise: float = 1.0,
    ):
        self.num_episodes = num_episodes
        self.env = ReactorEnv(max_steps=max_steps, difficulty=difficulty, noise=noise)
        self.universe = BASE_UNIVERSE  # includes STATE + ACTION + MODEL defs
        self.tagger = LLMConceptTagger()
        self.dataset = EpisodeDataset(gamma=gamma)
        self.reward_model = RewardModel()
        self.discovery = PairwiseConceptDiscovery(
            max_new=max_new_concepts,
            min_support=0.05,
        )
        self.eps_greedy = eps_greedy
        # Correlation threshold for meta-concept creation in future-occupancy
        # analysis. Default 0.0 → accept any positive cosine similarity.
        self.corr_threshold = corr_threshold
        self.concept_importance: Dict[str, float] = {}
        self.concept_creator = ConceptCreator()
        # Track how many new STATE concepts have been added over time.
        self.base_state_count = len(self.universe.state_concepts)
        self.total_new_concepts = 0
        # Map meta-concept id -> tuple of parent concept ids that generated it.
        # Used to avoid reusing the same parent pair over and over.
        self.concept_parents: Dict[str, Tuple[str, str]] = {}
        # Track how often each concept ends up with zero reward-model weight
        # across fits; used to identify concepts that might be droppable.
        self.concept_zero_counts: Dict[str, int] = {}
        self.concept_fit_updates: int = 0
        # Track cumulative importance scores per concept across fits so we can
        # compute a simple average importance for pruning.
        self.concept_importance_sums: Dict[str, float] = {}
        self.concept_importance_updates: int = 0
        # Global replay-style buffers for greedy episodes: we keep all
        # (state, action, return) samples and always train the RewardModel on
        # the full accumulated dataset, padding missing concepts with 0.
        self.memory_states: List[Dict[str, int]] = []
        self.memory_actions: List[int] = []
        self.memory_returns: List[float] = []
        # Track which STATE concepts were introduced in the most recent
        # future-occupancy analysis so we can avoid immediately pruning the
        # ones we just created.
        self.new_state_concepts_last_analysis: List[str] = []
        # Hard cap on total concepts; if exceeded, we drop the concept that
        # has been zero-weight most often in the reward model. Default 15.
        self.max_concepts = max_concepts

    def _update_concept_importance(self) -> None:
        """
        Compute a simple importance score per concept from the current RewardModel:
        normalized |coef| over the feature dimensions.
        """
        coef = getattr(self.reward_model.model, "coef_", None)
        if coef is None:
            self.concept_importance = {}
            return
        coef_arr = np.asarray(coef).ravel()
        abs_coef = np.abs(coef_arr)
        if abs_coef.max() == 0:
            scores = abs_coef
        else:
            scores = abs_coef / abs_coef.max()
        importance: Dict[str, float] = {}
        for idx, cid in self.universe.idx_to_id.items():
            importance[cid] = float(scores[idx])
        self.concept_importance = importance
        # Maintain running sums so we can estimate average importance per
        # concept across fits.
        self.concept_importance_updates += 1
        for cid, score in importance.items():
            self.concept_importance_sums[cid] = (
                self.concept_importance_sums.get(cid, 0.0) + score
            )

    def _update_zero_weight_counts(self, coef_arr: np.ndarray) -> None:
        """
        Increment a counter for any concept whose reward-model coefficient is
        effectively zero in this fit. Concepts that remain zero across many
        fits are natural candidates for pruning.
        """
        self.concept_fit_updates += 1
        for idx, cid in self.universe.idx_to_id.items():
            if idx >= coef_arr.size:
                continue
            if float(abs(coef_arr[idx])) < 1e-6:
                self.concept_zero_counts[cid] = self.concept_zero_counts.get(cid, 0) + 1

    def _build_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Build full training arrays X_all, G_all from all stored samples,
        embedding per-step state dicts and actions into the current concept
        universe. STATE concepts that did not exist when a sample was
        collected are treated as 0 (missing / no information).
        """
        n = len(self.memory_states)
        K = self.universe.K
        if n == 0:
            return np.zeros((0, K), dtype=float), np.zeros(0, dtype=float)

        X = np.zeros((n, K), dtype=float)
        G = np.asarray(self.memory_returns, dtype=float)

        action_ids = ["ACTION_STEADY", "ACTION_COOL", "ACTION_PUSH"]

        for i in range(n):
            state_dict = self.memory_states[i]
            action = self.memory_actions[i]
            # Embed STATE concepts by id.
            for idx, concept in enumerate(self.universe.concepts):
                if concept.source == ConceptSource.LLM:
                    X[i, idx] = float(state_dict.get(concept.id, 0))
            # Embed ACTION as one-hot.
            if action in (0, 1, 2):
                cid = action_ids[action]
                if cid in self.universe.id_to_idx:
                    j_act = self.universe.id_to_idx[cid]
                    X[i, j_act] = 1.0

        return X, G

    def _analyze_concept_future(
        self,
        state_traces: List[np.ndarray],
        obs_traces: List[List[str]],
    ) -> None:
        """
        For each concept j, compute a discounted future-occurrence signal S_j(t)
        over the collected STATE traces, then train a tiny linear predictor
        S_j(t) ≈ w_j^T Z_state(t). Use cosine similarity between w_j vectors
        to identify strongly correlated concept pairs.
        """
        if not state_traces:
            return

        # Reset record of newly added STATE concepts for this analysis run.
        self.new_state_concepts_last_analysis = []

        gamma_c = 0.9
        Z_list: List[np.ndarray] = []
        S_list: List[np.ndarray] = []

        for Z_ep in state_traces:
            if Z_ep.size == 0:
                continue
            Z_ep = Z_ep.astype(float)
            T, K_state = Z_ep.shape
            # For the future-occurrence signal, treat presence as (value > 0)
            # so that S_j(t) measures discounted occupancy, not +/- evidence.
            occ = (Z_ep > 0).astype(float)
            S_ep = np.zeros_like(Z_ep, dtype=float)
            S_ep[-1] = occ[-1]
            for t in range(T - 2, -1, -1):
                S_ep[t] = occ[t] + gamma_c * S_ep[t + 1]
            Z_list.append(Z_ep)
            S_list.append(S_ep)

        if not Z_list:
            return

        Z_all = np.vstack(Z_list)
        S_all = np.vstack(S_list)
        _, K_state = Z_all.shape

        # Use a tiny linear model to predict the discounted future-occupancy
        # sum S_j(t) directly (regression) instead of a binary "ever occurs"
        # label. This keeps the signal closer to what we actually care about.
        W = np.zeros((K_state, K_state), dtype=float)
        s_stats: List[Tuple[str, float, bool]] = []
        for j in range(K_state):
            S_j = S_all[:, j]
            cid_j = self.universe.state_ids[j]
            s_mean = float(S_j.mean())
            is_const = bool(np.allclose(S_j, S_j[0]))
            s_stats.append((cid_j, s_mean, is_const))
            if is_const:
                continue
            reg = Ridge(alpha=1.0)
            reg.fit(Z_all, S_j)
            W[j] = reg.coef_.ravel()
            # Log a tiny summary of this regressor: mean target and a few
            # largest-magnitude weights.
            coef_j = reg.coef_.ravel()
            abs_coef = np.abs(coef_j)
            top_idx = np.argsort(-abs_coef)[:3]
            top_terms = []
            for idx in top_idx:
                if abs_coef[idx] == 0.0:
                    continue
                cid_feat = self.universe.idx_to_id.get(idx, f"idx{idx}")
                top_terms.append(f"{cid_feat}:{coef_j[idx]:.3f}")
            top_str = ", ".join(top_terms) if top_terms else "all ~0"
            console.print(
                f"[blue]Fitted occupancy regressor[/blue] for {cid_j}: "
                f"mean_S={s_mean:.3f}, top_weights=[{top_str}]"
            )

        console.rule("[bold blue]Concept Future-Occupancy Structure[/bold blue]")
        # If all-zero, nothing to report; include discounted occupancy stats.
        if not np.any(W):
            console.print(
                "[blue]Future-occupancy predictors are all zero/constant; "
                "no structure to report.[/blue]"
            )
            for cid, m, is_const in s_stats:
                if is_const and m == 0.0:
                    label = "constant 0"
                elif is_const:
                    label = "constant >0"
                else:
                    label = "varying"
                console.print(
                    f"[blue]- {cid}: discounted occupancy mean S={m:.3f} ({label})"
                )
            return

        sim = cosine_similarity(W)
        state_ids = self.universe.state_ids

        printed = 0
        max_pairs = 5
        max_new = 1
        new_added = 0

        # Build a set of parent pairs we've already used for meta-concept creation
        # so we don't keep reusing the same combinations.
        parent_map: Dict[str, Tuple[str, str]] = getattr(
            self, "concept_parents", {}
        )
        used_pairs = {frozenset(p) for p in parent_map.values()}

        for j in range(K_state):
            for k in range(j + 1, K_state):
                if np.allclose(W[j], 0) or np.allclose(W[k], 0):
                    continue
                # Use Experiment.corr_threshold if present, otherwise default 0.0.
                thresh = getattr(self, "corr_threshold", 0.0)
                if sim[j, k] <= thresh:
                    continue

                cid_j = state_ids[j]
                cid_k = state_ids[k]
                pair_key = frozenset({cid_j, cid_k})
                if pair_key in used_pairs:
                    continue
                console.print(
                    f"[blue]Pair[/blue] {cid_j} & {cid_k} | "
                    f"cosine_sim={sim[j, k]:.3f}"
                )
                printed += 1

                # Try to create a new meta-concept from this pair.
                # Collect positive (both on) and negative (only one on) examples.
                pos_obs: List[str] = []
                neg_obs: List[str] = []
                for Z_ep, obs_ep in zip(state_traces, obs_traces):
                    T_ep = Z_ep.shape[0]
                    for t in range(T_ep):
                        z_t = Z_ep[t]
                        if z_t[j] == 1 and z_t[k] == 1:
                            pos_obs.append(obs_ep[t])
                        elif (z_t[j] == 1) ^ (z_t[k] == 1):
                            neg_obs.append(obs_ep[t])
                        if len(pos_obs) >= 5 and len(neg_obs) >= 5:
                            break
                    if len(pos_obs) >= 5 and len(neg_obs) >= 5:
                        break

                if pos_obs and neg_obs and new_added < max_new:
                    pattern_concepts = [
                        self.universe.state_concepts[j],
                        self.universe.state_concepts[k],
                    ]
                    pattern_desc = (
                        f"Situations where both {cid_j} and {cid_k} tend to be "
                        "true together in the same log and in the near future."
                    )
                    try:
                        new_c = self.concept_creator.create(
                            universe=self.universe,
                            pattern_concepts=pattern_concepts,
                            pattern_description=pattern_desc,
                            positive_examples=pos_obs[:5],
                            negative_examples=neg_obs[:5],
                        )
                    except Exception as exc:  # keep creation failures local
                        console.print(
                            f"[red]Concept creation failed for pair "
                            f"{cid_j}/{cid_k}: {exc}[/red]"
                        )
                    else:
                        if new_c.id in self.universe.id_to_idx:
                            console.print(
                                f"[yellow]Generated concept id {new_c.id} already "
                                f"exists; skipping add.[/yellow]"
                            )
                        else:
                            # Append new concept to the universe.
                            self.universe = ConceptUniverse(
                                self.universe.concepts + [new_c]
                            )
                            console.print(
                                f"[bold blue]New concept added[/bold blue]: "
                                f"{new_c.id} from {cid_j} & {cid_k}"
                            )
                            new_added += 1
                            # Remember which parents produced this meta-concept.
                            parent_map = dict(parent_map)
                            parent_map[new_c.id] = (cid_j, cid_k)
                            self.concept_parents = parent_map
                            used_pairs.add(pair_key)
                            if hasattr(self, "total_new_concepts"):
                                self.total_new_concepts += 1
                            if hasattr(self, "new_state_concepts_last_analysis"):
                                self.new_state_concepts_last_analysis.append(new_c.id)

                if printed >= max_pairs:
                    break
            if printed >= max_pairs:
                break

        if printed == 0:
            console.print(
                "[blue]No strong concept-weight correlations found "
                "in future-occupancy predictors.[/blue]"
            )
        else:
            console.print(
                f"[blue]New concepts in this analysis:[/blue] {new_added} "
                f"(total added so far: {getattr(self, 'total_new_concepts', 0)})"
            )

    def run(self):
        random.seed(42)
        np.random.seed(42)

        console.rule("[bold cyan]No Warmup: ε-greedy Learning Episodes[/bold cyan]")
        console.print(
            f"[cyan]Episodes:[/cyan] {self.num_episodes}  |  "
            f"[cyan]Max steps per episode:[/cyan] {self.env.max_steps}  |  "
            f"[cyan]epsilon:[/cyan] {self.eps_greedy}"
        )

        # No separate random warmup: start directly with ε-greedy episodes.
        # RewardModel is updated after each episode from that episode's returns.
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
        total_reward = 0.0
        total_steps = 0
        episode_summaries: List[Tuple[int, float, int, bool]] = []

        for ep in range(num_episodes):
            obs = self.env.reset()
            done = False
            step = 0
            meltdown_happened = False
            ep_reward = 0.0
            ep_steps = 0
            episode_rewards: List[float] = []
            episode_states: List[np.ndarray] = []
            episode_obs: List[str] = []
            episode_state_dicts: List[Dict[str, int]] = []
            episode_actions: List[int] = []
            console.print(
                f"\n[bold green]Episode {ep + 1}/{num_episodes}[/bold green]:"
            )
            while not done:
                state_vec = self.tagger.tag_state(obs, self.universe)
                a, preds = self._greedy_action(state_vec)
                # Epsilon-greedy exploration: with probability eps_greedy, override
                # the greedy choice with a random action.
                explore = random.random() < getattr(self, "eps_greedy", 0.0)
                if explore:
                    a = random.choice([0, 1, 2])
                a_name = action_names.get(a, f"unknown({a})")

                # Snapshot state dict with current STATE concept ids so we can
                # safely embed later even if the universe grows.
                state_dict = {
                    c.id: int(state_vec[j])
                    for j, c in enumerate(self.universe.state_concepts)
                }

                # Build full feature vector for (state_vec, a)
                K_state = len(self.universe.state_concepts)
                K = self.universe.K
                full_state = np.zeros(K, dtype=float)
                state_indices = self.universe.state_index_map()
                full_state[state_indices] = state_vec
                action_ids = ["ACTION_STEADY", "ACTION_COOL", "ACTION_PUSH"]
                cid = action_ids[a]
                j_act = self.universe.id_to_idx[cid]
                full_state[j_act] = 1.0

                episode_obs.append(obs)
                episode_state_dicts.append(state_dict)
                episode_actions.append(a)
                obs, done, meltdown = self.env.step(a)
                # Continuous reward based on reactor output with a strong
                # penalty on meltdown. Higher output is better, especially
                # later in the episode and under high demand.
                if meltdown:
                    reward = -10.0
                else:
                    output = self.env.output
                    t_norm = self.env.step_idx / max(self.env.max_steps, 1)
                    demand_factor = 1.2 if self.env.demand == "high" else 0.8
                    exponent = 0.5 * output * (1.0 + t_norm) * demand_factor
                    reward = math.exp(exponent) - 1.0
                ep_reward += reward
                ep_steps += 1
                total_reward += reward
                total_steps += 1
                episode_rewards.append(reward)
                episode_states.append(state_vec.copy())

                # Current dataset sample count: number of transitions seen so far
                # across all episodes in this greedy run.
                samples_so_far = total_steps

                avg_reward_global = total_reward / total_steps if total_steps else 0.0
                avg_reward_ep = ep_reward / ep_steps if ep_steps else 0.0

                # Compact per-concept importance string (ID:score sorted by importance)
                if self.concept_importance:
                    sorted_ids = sorted(
                        self.concept_importance.keys(),
                        key=lambda cid: -self.concept_importance[cid],
                    )
                    imp_str = ", ".join(
                        f"{cid}:{self.concept_importance[cid]:.2f}" for cid in sorted_ids
                    )
                else:
                    imp_str = "n/a"

                added_total = getattr(self, "total_new_concepts", 0)
                console.print(
                    f"  [white]step {step}[/white]: "
                    f"[bold]action[/bold]={a_name} (raw={a}) | "
                    f"[cyan]predicted_return_per_action[/cyan]={np.round(preds, 3)} | "
                    f"[red]reward_t[/red]={reward:.3f} | "
                    f"[yellow]avg_reward_global[/yellow]={avg_reward_global:.3f} | "
                    f"[yellow]avg_reward_episode[/yellow]={avg_reward_ep:.3f} | "
                    f"[green]concept_importance[/green]=[{imp_str}] | "
                    f"[green]concepts_added_total[/green]={added_total} | "
                    f"[green]samples_total[/green]={samples_so_far} | "
                    f"[green]difficulty[/green]={self.env.current_difficulty():.2f}"
                )
                console.print(f"    [white]observation[/white]: {obs}")

                if meltdown and not meltdown_happened:
                    meltdown_happened = True
                    console.print(f"    [bold red]-> MELTDOWN at step {step}[/bold red]")
                step += 1

            # After each episode, recompute Monte-Carlo returns for this
            # episode and add them to the global replay buffers. We then
            # refit the RewardModel on all accumulated samples so far.
            if episode_rewards:
                gamma = self.dataset.gamma
                T = len(episode_rewards)
                G_ep = np.zeros(T, dtype=float)
                G_ep[-1] = episode_rewards[-1]
                for t in range(T - 2, -1, -1):
                    G_ep[t] = episode_rewards[t] + gamma * G_ep[t + 1]
                for t in range(T):
                    self.memory_states.append(episode_state_dicts[t])
                    self.memory_actions.append(episode_actions[t])
                    self.memory_returns.append(G_ep[t])

                X_all, G_all = self._build_training_data()
                idx_all = list(range(len(self.memory_returns)))
                if idx_all:
                    self.reward_model.fit(X_all, G_all, idx_all)
                    # Update concept importance after each greedy episode fit
                    self._update_concept_importance()
                    # Tiny summary of the reward predictor fit using all data.
                    coef = getattr(self.reward_model.model, "coef_", None)
                    if coef is not None:
                        coef_arr = np.asarray(coef).ravel()
                        abs_coef = np.abs(coef_arr)
                        # Track which concepts are effectively unused in this fit.
                        self._update_zero_weight_counts(coef_arr)
                        top_idx = np.argsort(-abs_coef)[:3]
                        top_terms = []
                        for j in top_idx:
                            if abs_coef[j] == 0.0:
                                continue
                            cid_feat = self.universe.idx_to_id.get(j, f"idx{j}")
                            top_terms.append(f"{cid_feat}:{coef_arr[j]:.3f}")
                        top_str = ", ".join(top_terms) if top_terms else "all ~0"
                        always_zero = [
                            cid
                            for cid in self.universe.idx_to_id.values()
                            if self.concept_zero_counts.get(cid, 0)
                            == self.concept_fit_updates
                        ]
                        console.print(
                            f"[magenta]Fitted reward model[/magenta]: "
                            f"samples={len(idx_all)}, mean_G={G_all.mean():.3f}, "
                            f"top_weights=[{top_str}], "
                            f"always_zero={always_zero}"
                        )

            if episode_states:
                # After this episode, analyze its future concept-occupancy
                # structure and create at most one new meta-concept from the
                # strongest correlated pair.
                self._analyze_concept_future(
                    [np.stack(episode_states)],
                    [episode_obs],
                )
                # If we've exceeded the max concept budget, drop the STATE
                # concept with the lowest average importance under the
                # RewardModel so far (ties broken arbitrarily). Do not drop
                # concepts that were just created in this analysis run.
                if self.universe.K > self.max_concepts and self.concept_importance_sums:
                    # Do not drop ACTION or MODEL concepts; only STATE.
                    recent_new = set(
                        getattr(self, "new_state_concepts_last_analysis", [])
                    )
                    candidates = [
                        cid
                        for cid, concept in zip(
                            self.universe.ids, self.universe.concepts
                        )
                        if concept.source == ConceptSource.LLM and cid not in recent_new
                    ]
                    if candidates:
                        # Compute simple average importance per candidate.
                        denom = max(self.concept_importance_updates, 1)
                        def avg_importance(cid: str) -> float:
                            return self.concept_importance_sums.get(cid, 0.0) / denom

                        drop_cid = min(candidates, key=avg_importance)
                        drop_idx = self.universe.id_to_idx.get(drop_cid)
                        if drop_idx is not None:
                            avg_imp = avg_importance(drop_cid)
                            console.print(
                                f"[magenta]Dropping concept[/magenta]: {drop_cid} "
                                f"(avg_importance={avg_imp:.3f} over "
                                f"{self.concept_importance_updates} fits)"
                            )
                            new_concepts = [
                                c
                                for i, c in enumerate(self.universe.concepts)
                                if i != drop_idx
                            ]
                            self.universe = ConceptUniverse(new_concepts)

                # Episode summary: average reward and meltdown flag.
                if ep_steps:
                    avg_ep = ep_reward / ep_steps
                    console.print(
                        f"    [cyan]Episode {ep + 1} avg reward[/cyan]: {avg_ep:.3f}"
                    )
                    episode_summaries.append(
                        (ep + 1, ep_reward, ep_steps, meltdown_happened)
                    )
                    # Print running per-episode totals so far.
                    cumulative = 0.0
                    console.print("    [cyan]Episode totals so far:[/cyan]")
                    for idx, total, steps, melted in episode_summaries:
                        cumulative += total
                        avg_so_far = total / steps if steps else 0.0
                        status = "MELTDOWN" if melted else "no-meltdown"
                        console.print(
                            f"      [cyan]Episode {idx}[/cyan]: "
                            f"total={total:.3f}, avg={avg_so_far:.3f}, status={status}"
                        )
                    # Running average reward per episode across all completed
                    # episodes so far (based on total rewards).
                    if episode_summaries:
                        running_avg = cumulative / len(episode_summaries)
                    else:
                        running_avg = 0.0
                    console.print(
                        f"    [cyan]Cumulative total reward[/cyan]: {cumulative:.3f}"
                    )
                    console.print(
                        f"    [cyan]Running avg episode reward[/cyan]: {running_avg:.3f}"
                    )
                if not meltdown_happened:
                    console.print(
                        "    [green]-> no meltdown in this episode (greedy actor run)[/green]"
                    )

        if episode_summaries:
            console.rule("[bold cyan]Episode Reward Summary[/bold cyan]")
            for idx, total, steps, melted in episode_summaries:
                avg_ep = total / steps if steps else 0.0
                status = "MELTDOWN" if melted else "no-meltdown"
                console.print(
                    f"[cyan]Episode {idx}[/cyan]: "
                    f"total_reward={total:.3f}, avg_reward={avg_ep:.3f}, steps={steps}, "
                    f"status={status}"
                )

        # After all episodes, analyze future concept-occupancy structure and
        # create any new meta-concepts from strongly correlated pairs.


# =========================
# 8. ENTRYPOINT
# =========================


def main(argv: Optional[List[str]] = None):
    parser = argparse.ArgumentParser(
        description="Concept-world RL experiment with DSPy-tagged concepts."
    )
    parser.add_argument(
        "--lm",
        type=str,
        default=DEFAULT_LM_MODEL,
        help=(
            "DSPy LM model string (default: "
            "openrouter/google/gemini-2.5-flash)."
        ),
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
    parser.add_argument(
        "--corr-threshold",
        type=float,
        default=0.0,
        help=(
            "Cosine similarity threshold for future-occupancy meta-concept "
            "creation (default: 0.0 = any positive correlation)."
        ),
    )
    parser.add_argument(
        "--difficulty",
        type=float,
        default=1.0,
        help=(
            "Reactor difficulty multiplier (>=0.1). Values >1 make the "
            "reactor more unstable (more glitches, faster stress drift, "
            "tighter meltdown thresholds). Default: 1.0."
        ),
    )
    parser.add_argument(
        "--noise",
        type=float,
        default=1.0,
        help=(
            "Global noise factor for stochastic dynamics (0 = no random "
            "perturbations in stress/margin/output; 1 = default levels; "
            ">1 amplifies noise). Default: 1.0."
        ),
    )
    parser.add_argument(
        "--max-concepts",
        type=int,
        default=15,
        help=(
            "Maximum total concepts in the universe before we drop the "
            "STATE concept with the highest zero-weight count in the reward "
            "model. Default: 15."
        ),
    )

    args = parser.parse_args(argv)

    lm = dspy.LM(model=args.lm)
    dspy.configure(lm=lm)

    exp = Experiment(
        num_episodes=args.episodes,
        max_steps=args.max_steps,
        gamma=args.gamma,
        max_new_concepts=args.max_new_concepts,
        eps_greedy=args.epsilon,
        corr_threshold=args.corr_threshold,
        difficulty=args.difficulty,
        max_concepts=args.max_concepts,
        noise=args.noise,
    )
    exp.run()


if __name__ == "__main__":
    main()
