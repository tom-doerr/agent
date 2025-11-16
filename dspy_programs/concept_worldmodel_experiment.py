#!/usr/bin/env python
"""
Minimal concept-worldmodel experiment with DSPy + DeepSeek V3.2 via OpenRouter.

Changes vs previous version:
- Concepts are Pydantic objects with id + definition.
- The DSPy Signature takes a List[Concept] as input (no hardcoded concept fields).
- The LLM returns a Pydantic ConceptActivations object (no raw JSON string).
- Ground truth is hidden numeric state -> non-obvious textual logs.
- Metrics:
  - Concept tagging quality (LLM vs ground truth).
  - For each concept: how well it can be predicted from the others (baseline CE vs model CE, acc, AUC).
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from pydantic import BaseModel, Field
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, log_loss, roc_auc_score

import dspy


# -----------------------------
# 1. CONFIG: LM + CONCEPTS
# -----------------------------

# Configure DSPy to use DeepSeek V3.2 Exp via OpenRouter.
# NOTE: We do NOT set api_base or api_key here.
# You are expected to configure dspy/your env appropriately.
LM = dspy.LM(model="openrouter/deepseek/deepseek-v3.2-exp")
dspy.configure(lm=LM)


class Concept(BaseModel):
    """Single concept definition."""

    id: str = Field(..., description="Stable concept ID (e.g. 'STRAINED_CORE').")
    definition: str = Field(..., description="Short textual definition of the concept.")


# Fictional "reactor" concepts.
# Ground truth is based on hidden numeric state, not trivially tied to explicit thresholds
# in the text, so the LLM must genuinely infer.
CONCEPTS: List[Concept] = [
    Concept(
        id="STRAINED_CORE",
        definition=(
            "The core is under unusually high internal stress, typically together with "
            "repeated small disturbances or glitches."
        ),
    ),
    Concept(
        id="THIN_MARGIN",
        definition=(
            "Safety margins on the core are thin: the spare capacity or buffer is low, "
            "leaving little room for further stress."
        ),
    ),
    Concept(
        id="STORMY_CHANNEL",
        definition=(
            "The energy channel is stormy: there have been several recent glitches or "
            "spikes in a short timespan."
        ),
    ),
    Concept(
        id="AGITATED_OPERATOR",
        definition=(
            "The human operator is clearly agitated or upset, showing annoyance or anger "
            "about the system's behavior."
        ),
    ),
    Concept(
        id="CRITICAL_MODE",
        definition=(
            "The overall situation is critical: the core is strained, safety margins are thin, "
            "and the operator is agitated, making a serious incident likely."
        ),
    ),
]

CONCEPT_IDS = [c.id for c in CONCEPTS]
K = len(CONCEPTS)

SAMPLES_LOG_PATH = Path(".nlco/meta/concept_worldmodel_samples.jsonl")


def print_concepts() -> None:
    print("Concepts (id: definition):")
    for c in CONCEPTS:
        print(f"- {c.id}: {c.definition}")


def log_samples_jsonl(samples: List[Dict], path: Path | None = None) -> None:
    target = path or SAMPLES_LOG_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as f:
        for row in samples:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


# -----------------------------
# 2. SYNTHETIC DATA GENERATION
# -----------------------------


def generate_synthetic_example() -> Tuple[str, Dict[str, int]]:
    """
    Generate one synthetic "reactor log" observation + ground-truth concept labels.

    Hidden variables:
      - stress: 0..100 (core stress index)
      - margin: 0..100 (flux safety margin, higher is safer)
      - glitches: 0..5 (recent disturbances)
      - tone: calm / annoyed / furious (operator tone)

    Ground-truth concept logic (not shown to the LLM):

      STRAINED_CORE:
        stress > 75 and glitches >= 2

      THIN_MARGIN:
        margin < 25

      STORMY_CHANNEL:
        glitches >= 3

      AGITATED_OPERATOR:
        tone in {annoyed, furious}

      CRITICAL_MODE:
        STRAINED_CORE and THIN_MARGIN and AGITATED_OPERATOR
    """

    # Sample hidden state
    stress = random.choices(
        [random.randint(15, 45), random.randint(45, 75), random.randint(76, 98)],
        weights=[0.4, 0.35, 0.25],
    )[0]
    margin = random.choices(
        [random.randint(40, 95), random.randint(5, 30)],
        weights=[0.65, 0.35],
    )[0]
    glitches = random.randint(0, 5)
    tone = random.choices(
        ["calm", "annoyed", "furious"],
        weights=[0.5, 0.3, 0.2],
    )[0]

    # Ground-truth concept labels
    labels: Dict[str, int] = {}
    labels["STRAINED_CORE"] = int(stress > 75 and glitches >= 2)
    labels["THIN_MARGIN"] = int(margin < 25)
    labels["STORMY_CHANNEL"] = int(glitches >= 3)
    labels["AGITATED_OPERATOR"] = int(tone in ("annoyed", "furious"))
    labels["CRITICAL_MODE"] = int(
        labels["STRAINED_CORE"] and labels["THIN_MARGIN"] and labels["AGITATED_OPERATOR"]
    )

    # Build synthetic observation text (non-obvious but consistent)
    if stress < 40:
        stress_phrase = "core stress index in a comfortable band"
    elif stress < 70:
        stress_phrase = "core stress index elevated but not alarming"
    else:
        stress_phrase = "core stress index pressing near the upper operating band"

    if margin < 20:
        margin_phrase = "flux margin is thin and shrinking"
    elif margin < 35:
        margin_phrase = "flux margin feels noticeably tight"
    else:
        margin_phrase = "flux margin appears healthy"

    if glitches == 0:
        glitch_phrase = "no shard glitches recorded in this cycle"
    elif glitches == 1:
        glitch_phrase = "a single minor shard glitch noted"
    elif glitches <= 3:
        glitch_phrase = f"{glitches} shard glitches in the last cycle"
    else:
        glitch_phrase = f"{glitches} shard glitches clustered in the last cycle"

    if tone == "calm":
        operator_msg = random.choice(
            [
                "Readings look acceptable, just keeping an eye on the gauges.",
                "Everything feels stable enough for now.",
                "No major complaints, just monitoring the core.",
            ]
        )
    elif tone == "annoyed":
        operator_msg = random.choice(
            [
                "These spikes are getting annoying; this shouldn't wobble like that.",
                "I keep seeing little jumps in the readings; it's starting to bother me.",
                "The core keeps twitching, it's irritating.",
            ]
        )
    else:  # furious
        operator_msg = random.choice(
            [
                "This reactor is a mess; I'm sick of chasing these surges.",
                "If this core jumps again I'm filing a serious incident report.",
                "This is out of control, I'm furious we haven't shut it down.",
            ]
        )

    obs_lines = [
        f"Reactor log: {stress_phrase}, {margin_phrase}, {glitch_phrase}.",
        f'Operator note: "{operator_msg}"',
    ]
    observation = " ".join(obs_lines)

    return observation, labels


# -----------------------------
# 3. Pydantic OUTPUT MODELS
# -----------------------------


class ConceptActivation(BaseModel):
    concept_id: str = Field(..., description="ID of the concept.")
    value: int = Field(..., description="0 or 1 indicating whether the concept applies.")


class ConceptActivations(BaseModel):
    activations: List[ConceptActivation] = Field(
        ...,
        description=(
            "List of activations, one per concept: "
            "{'concept_id': 'STRAINED_CORE', 'value': 0 or 1}, etc."
        ),
    )


# -----------------------------
# 4. DSPy SIGNATURE + MODULE
# -----------------------------


class TagConcepts(dspy.Signature):
    """
    You are a precise concept tagger for a fictional reactor system.

    Task:
      - You see one observation: a short log-like description of the reactor state
        and the human operator's note.
      - You also receive a list of concept definitions, each with a stable ID and a
        short natural-language description.
      - For each concept in the list, decide whether it applies (1) or not (0)
        in this observation.

    Output:
      - Return ONLY a JSON object that matches the ConceptActivations schema:
        {"activations": [{"concept_id": "...", "value": 0 or 1}, ...]}.
      - Each concept_id in the input list MUST appear exactly once in the activations
        list with value 0 or 1.
      - Do not include extra text outside the JSON.
    """

    observation: str = dspy.InputField(
        desc="A single reactor log observation: reactor state and operator note."
    )
    concepts: List[Concept] = dspy.InputField(
        desc=(
            "List of concept objects, each with 'id' and 'definition'. "
            "Decide 0/1 for each concept based on the observation."
        )
    )
    activations: str = dspy.OutputField(
        desc=(
            "JSON object matching ConceptActivations: "
            '{"activations": [{"concept_id": "...", "value": 0 or 1}, ...]}.'
        )
    )


class ConceptTagger(dspy.Module):
    """
    Wraps a DSPy Predict module that, given an observation and a list of Concept
    objects, returns a ConceptActivations Pydantic object.
    """

    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(TagConcepts)

    def __call__(self, observation: str, concepts: List[Concept]) -> Dict[str, int]:
        out = self.predict(observation=observation, concepts=concepts)
        activations = ConceptActivations.model_validate_json(out.activations)
        values: Dict[str, int] = {c.id: 0 for c in concepts}
        for act in activations.activations:
            cid = act.concept_id
            if cid in values:
                values[cid] = int(act.value)
        return values


# -----------------------------
# 5. METRICS HELPERS
# -----------------------------


def evaluate_concept_tagging(
    Z_true: np.ndarray, Z_pred: np.ndarray, concept_ids: List[str]
) -> None:
    """
    Compare LLM-predicted concept bits vs ground truth.
    Prints accuracy and F1 per concept and averages.
    """
    print("\n=== Concept Tagging Quality (LLM vs ground truth) ===")
    accs = []
    f1s = []
    for j, cid in enumerate(concept_ids):
        y_true = Z_true[:, j]
        y_pred = Z_pred[:, j]
        acc = accuracy_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        accs.append(acc)
        f1s.append(f1)
        pos_rate = float(y_true.mean())
        print(
            f"Concept {cid:18s} | pos_rate={pos_rate:.3f} | acc={acc:.3f} | f1={f1:.3f}"
        )
    print(
        f"\nAverage accuracy: {np.mean(accs):.3f} | Average F1: {np.mean(f1s):.3f}\n"
    )


def evaluate_concept_structure(
    Z_train: np.ndarray,
    Z_val: np.ndarray,
    concept_ids: List[str],
) -> None:
    """
    For each concept j, train logistic regression to predict it from all other concepts.
    Uses predicted bits (i.e., LLM's view of concepts) as input.

    Metrics per concept:
      - baseline cross-entropy (predicting constant pos_rate),
      - model cross-entropy,
      - ΔCE (information gain),
      - accuracy,
      - ROC AUC.
    """
    print("\n=== Concept Structure: Predict each concept from the others ===")
    _, K_local = Z_train.shape
    delta_self = np.zeros(K_local)
    ce_baselines = np.full(K_local, np.nan)
    concept_masks: List[np.ndarray] = []
    X_train_list: List[np.ndarray] = []
    X_val_list: List[np.ndarray] = []
    y_train_list: List[np.ndarray] = []
    y_val_list: List[np.ndarray] = []

    for j, cid in enumerate(concept_ids):
        # Exclude this concept from features
        mask = np.ones(K_local, dtype=bool)
        mask[j] = False

        X_train = Z_train[:, mask]
        y_train = Z_train[:, j]
        X_val = Z_val[:, mask]
        y_val = Z_val[:, j]

        # Skip degenerate cases (all 0 or all 1)
        if y_train.mean() == 0.0 or y_train.mean() == 1.0:
            print(
                f"Concept {cid:18s} | constant in train (pos_rate={y_train.mean():.3f}), skipping."
            )
            concept_masks.append(mask)
            X_train_list.append(X_train)
            X_val_list.append(X_val)
            y_train_list.append(y_train)
            y_val_list.append(y_val)
            continue

        baseline_p = np.full_like(y_val, fill_value=y_train.mean(), dtype=float)
        ce_baseline = log_loss(y_val, baseline_p, labels=[0, 1])
        ce_baselines[j] = ce_baseline

        concept_masks.append(mask)
        X_train_list.append(X_train)
        X_val_list.append(X_val)
        y_train_list.append(y_train)
        y_val_list.append(y_val)

    # Global hyperparameter search across concepts
    print("\nHyperparam search for structure models (shared across concepts):")
    print(" trial |      C | max_iter | avg_CE | avg_acc | avg_AUC | sum_ΔCE")
    best_global_delta = float("-inf")
    best_C = None
    best_max_iter = None

    for trial in range(3):
        C = 10 ** random.uniform(-2, 2)
        max_iter = random.randint(200, 800)

        total_ce = 0.0
        total_acc = 0.0
        total_auc = 0.0
        total_delta = 0.0
        n_valid = 0

        for j, cid in enumerate(concept_ids):
            if np.isnan(ce_baselines[j]):
                continue
            X_train = X_train_list[j]
            y_train = y_train_list[j]
            X_val = X_val_list[j]
            y_val = y_val_list[j]

            clf = LogisticRegression(
                C=C,
                penalty="l2",
                solver="lbfgs",
                max_iter=max_iter,
            )
            clf.fit(X_train, y_train)
            y_proba = clf.predict_proba(X_val)[:, 1]
            ce_model = log_loss(y_val, y_proba, labels=[0, 1])
            acc = accuracy_score(y_val, (y_proba >= 0.5).astype(int))
            try:
                auc = roc_auc_score(y_val, y_proba)
            except ValueError:
                auc = float("nan")

            total_ce += ce_model
            total_acc += acc
            if not np.isnan(auc):
                total_auc += auc
            delta = ce_baselines[j] - ce_model
            total_delta += delta
            n_valid += 1

        if n_valid == 0:
            avg_ce = float("nan")
            avg_acc = float("nan")
            avg_auc = float("nan")
        else:
            avg_ce = total_ce / n_valid
            avg_acc = total_acc / n_valid
            avg_auc = total_auc / max(n_valid, 1)

        print(
            f"   {trial:1d}   | {C:7.3f} | {max_iter:8d} | {avg_ce:6.3f} | {avg_acc:7.3f} | {avg_auc:7.3f} | {total_delta:7.3f}"
        )

        if total_delta > best_global_delta:
            best_global_delta = total_delta
            best_C = C
            best_max_iter = max_iter

    # Final per-concept metrics with best global hyperparams
    for j, cid in enumerate(concept_ids):
        if np.isnan(ce_baselines[j]):
            continue
        X_train = X_train_list[j]
        y_train = y_train_list[j]
        X_val = X_val_list[j]
        y_val = y_val_list[j]

        clf = LogisticRegression(
            C=best_C,
            penalty="l2",
            solver="lbfgs",
            max_iter=best_max_iter,
        )
        clf.fit(X_train, y_train)
        y_proba = clf.predict_proba(X_val)[:, 1]

        ce_model = log_loss(y_val, y_proba, labels=[0, 1])
        acc = accuracy_score(y_val, (y_proba >= 0.5).astype(int))
        try:
            auc = roc_auc_score(y_val, y_proba)
        except ValueError:
            auc = float("nan")

        delta = ce_baselines[j] - ce_model
        delta_self[j] = delta

        print(
            f"Concept {cid:18s} | base_CE={ce_baselines[j]:.3f} | best_CE={ce_model:.3f} "
            f"| ΔCE={delta:.3f} | acc={acc:.3f} | AUC={auc:.3f} "
            f"| best_C={best_C:.3f}, best_max_iter={best_max_iter}"
        )

    total_delta = float(delta_self.sum())
    print("\n=== Concept Usefulness Summary (internal, ΔCE_self) ===")
    print("ΔCE_self = baseline_CE − best_CE for predicting this concept from the others (higher = more structured).")
    print("Concept             | ΔCE_self (predictable from others) | frac_of_total")
    order = np.argsort(-delta_self)  # descending by ΔCE_self
    for idx in order:
        cid = concept_ids[idx]
        j = int(idx)
        share = delta_self[j] / total_delta if total_delta > 0 else 0.0
        print(f"{cid:20s} | {delta_self[j]:8.3f} | {share:8.3f}")


# -----------------------------
# 6. MAIN EXPERIMENT
# -----------------------------


def main() -> None:
    random.seed(42)
    np.random.seed(42)

    N_TRAIN = 120
    N_VAL = 40

    print_concepts()
    print(f"Generating {N_TRAIN + N_VAL} synthetic observations...")
    observations: List[str] = []
    labels_true_list: List[Dict[str, int]] = []

    for _ in range(N_TRAIN + N_VAL):
        obs, lab = generate_synthetic_example()
        observations.append(obs)
        labels_true_list.append(lab)

    print("\nSample synthetic observations + ground truth labels (first 3):")
    for i in range(min(3, N_TRAIN + N_VAL)):
        print(f"\n--- Example {i} ---")
        print(f"Observation: {observations[i]}")
        print(f"Labels: {labels_true_list[i]}")

    Z_true = np.zeros((N_TRAIN + N_VAL, K), dtype=int)
    for i, lab in enumerate(labels_true_list):
        for j, cid in enumerate(CONCEPT_IDS):
            Z_true[i, j] = lab[cid]

    tagger = ConceptTagger()
    Z_pred = np.zeros((N_TRAIN + N_VAL, K), dtype=int)
    samples_for_log: List[Dict] = []

    print(
        "\nTagging concepts with DeepSeek V3.2 (this will call the API once per observation)..."
    )
    for i, obs in enumerate(observations):
        result = tagger(observation=obs, concepts=CONCEPTS)
        for j, cid in enumerate(CONCEPT_IDS):
            Z_pred[i, j] = result[cid]
        if i < 3:
            print(f"\nLLM activations for example {i}:")
            print(f"Observation: {obs}")
            print(f"Predicted activations: {result}")
        elif i == 3:
            print("\n... (remaining activations suppressed; only first 3 shown) ...")
        if i < 5:
            samples_for_log.append(
                {
                    "index": i,
                    "observation": obs,
                    "labels": labels_true_list[i],
                    "predicted": result,
                }
            )

    Z_true_train = Z_true[:N_TRAIN]
    Z_true_val = Z_true[N_TRAIN:]
    Z_pred_train = Z_pred[:N_TRAIN]
    Z_pred_val = Z_pred[N_TRAIN:]

    evaluate_concept_tagging(Z_true, Z_pred, CONCEPT_IDS)
    evaluate_concept_structure(Z_pred_train, Z_pred_val, CONCEPT_IDS)

    if samples_for_log:
        log_samples_jsonl(samples_for_log)
        print(f"\nWrote {len(samples_for_log)} samples to {SAMPLES_LOG_PATH}")

    print("\nDone. This is a minimal concept-worldmodel baseline with dynamic Pydantic concepts.")


if __name__ == "__main__":
    main()
