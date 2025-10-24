from tests.helpers import install_fake_dspy, fresh_pkg, import_pkg


def test_try_tree_text_iterates_top_then_refines_child():
    install_fake_dspy()
    with fresh_pkg():
        m = import_pkg()

        async def fake_batch(text, n, model, gen_params=None):
            return ["B", "A"]  # B ranks above A (lex)

        m._batch = fake_batch  # type: ignore[attr-defined]
        tt = m.TryTree(init_n=2, expand_k=1, iters=1)
        # Monkeypatch refiner to append '!'
        tt.refine = lambda prev, x, kw: prev + "!"  # type: ignore[method-assign]
        best = tt("Q")
        assert best == "B!"
