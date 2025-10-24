from tests.helpers import install_fake_dspy, fresh_pkg, import_pkg


def test_bestofbatch_include_original_flag_affects_pool():
    install_fake_dspy(best_choice=2)  # pick index 2
    with fresh_pkg():
        m = import_pkg()

        async def fake_batch(text, n, model, gen_params=None):
            return ["A", "B"]

        m._batch = fake_batch  # type: ignore[attr-defined]

        # include_original=True => pool=[Q,A,B] -> best_choice=2 => 'A'
        assert m.batch_best("Q", n=2, include_original=True) == "A"
        # include_original=False => pool=[A,B] -> best_choice=2 => 'B'
        assert m.batch_best("Q", n=2, include_original=False) == "B"


def test_bestofbatch_passes_gen_params():
    install_fake_dspy()
    seen = {}
    with fresh_pkg():
        m = import_pkg()

        async def fake_batch(text, n, model, gen_params=None):
            seen.update(text=text, n=n, model=model, gen_params=gen_params)
            return ["X", "Y"]

        m._batch = fake_batch  # type: ignore[attr-defined]
        m.batch_best("Q", n=2, model="M", gen_params={"temperature": 0.1})
        assert seen["model"] == "M"
        assert seen["n"] == 2
        assert seen["gen_params"] == {"temperature": 0.1}

