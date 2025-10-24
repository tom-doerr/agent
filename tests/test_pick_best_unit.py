from tests.helpers import install_fake_dspy, fresh_pkg, import_pkg


def test__pick_best_chooses_index_2():
    fake = install_fake_dspy(best_choice=2)
    with fresh_pkg():
        m = import_pkg()
        out = m._pick_best("Q", ["AA", "BB", "CC"])  # type: ignore[attr-defined]
        assert out == "BB"
