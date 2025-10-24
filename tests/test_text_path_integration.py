import asyncio
from tests.helpers import install_fake_dspy, fresh_pkg, import_pkg


def test_text_batch_path_includes_original_and_selects_third():
    install_fake_dspy(best_choice=3)
    with fresh_pkg():
        m = import_pkg()

        async def fake_batch(text, n, model, gen_params=None):
            return ["A", "B"]

        # patch internal async batcher
        m._batch = fake_batch  # type: ignore[attr-defined]
        assert m.batch_best("Q", n=2) == "B"
