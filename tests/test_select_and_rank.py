from tests.helpers import install_fake_dspy, fresh_pkg, import_pkg


def test_select_best_module_picks_index():
    install_fake_dspy(best_choice=2)
    with fresh_pkg():
        m = import_pkg()
        sel = m.SelectBest()
        out = sel("Q", ["A", "B", "C"])  # type: ignore[arg-type]
        assert out == "B"


def test_binary_ranker_orders_desc_lex():
    install_fake_dspy()
    with fresh_pkg():
        m = import_pkg()
        r = m.BinaryRanker()
        r("B")
        r("A")
        r("C")
        assert r.items == ["C", "B", "A"]

