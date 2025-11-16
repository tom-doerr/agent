import numpy as np

from dspy_programs.concept_worldmodel_experiment import (
    CONCEPTS,
    CONCEPT_IDS,
    ConceptActivation,
    ConceptActivations,
    ConceptTagger,
    evaluate_concept_structure,
    evaluate_concept_tagging,
    generate_synthetic_example,
    SAMPLES_LOG_PATH,
    log_samples_jsonl,
    print_concepts,
)


def test_generate_synthetic_example_labels_are_consistent():
    _, labels = generate_synthetic_example()
    assert set(labels.keys()) == set(CONCEPT_IDS)
    if labels["CRITICAL_MODE"]:
        assert labels["STRAINED_CORE"]
        assert labels["THIN_MARGIN"]
        assert labels["AGITATED_OPERATOR"]


def test_concept_tagger_uses_pydantic_activations(monkeypatch):
    tagger = ConceptTagger()

    acts = ConceptActivations(
        activations=[
            ConceptActivation(concept_id=c.id, value=i % 2) for i, c in enumerate(CONCEPTS)
        ]
    )

    class DummyOut:
        def __init__(self, labels):
            self.activations = labels

    monkeypatch.setattr(
        tagger, "predict", lambda observation, concepts: DummyOut(acts.model_dump_json())
    )

    result = tagger("dummy observation", CONCEPTS)
    assert set(result.keys()) == {c.id for c in CONCEPTS}
    for i, c in enumerate(CONCEPTS):
        assert result[c.id] == i % 2


def test_evaluate_helpers_run_and_print(capsys):
    # Small, non-degenerate labels for three concepts
    Z_true = np.array(
        [
            [0, 0, 1],
            [1, 0, 0],
            [1, 1, 1],
            [0, 1, 0],
        ],
        dtype=int,
    )
    Z_pred = Z_true.copy()

    evaluate_concept_tagging(Z_true, Z_pred, ["A", "B", "C"])
    out_tag, _ = capsys.readouterr()
    assert "Concept Tagging Quality" in out_tag
    assert "Concept A" in out_tag

    Z_train = Z_pred
    Z_val = Z_pred
    evaluate_concept_structure(Z_train, Z_val, ["A", "B", "C"])
    out_struct, _ = capsys.readouterr()
    assert "Concept Structure" in out_struct
    assert "Concept A" in out_struct
    assert "Concept Usefulness Summary" in out_struct


def test_print_concepts_lists_ids(capsys):
    print_concepts()
    out, _ = capsys.readouterr()
    assert "Concepts (id: definition):" in out
    for c in CONCEPTS:
        assert c.id in out


def test_log_samples_jsonl_writes_lines(tmp_path):
    path = tmp_path / "samples.jsonl"
    samples = [
        {"index": 0, "observation": "obs0", "labels": {"A": 1}, "predicted": {"A": 0}},
        {"index": 1, "observation": "obs1", "labels": {"A": 0}, "predicted": {"A": 1}},
    ]
    log_samples_jsonl(samples, path)
    assert path.exists()
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
