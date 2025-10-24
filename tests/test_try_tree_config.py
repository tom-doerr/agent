from tests.helpers import install_fake_dspy, fresh_pkg, import_pkg


def test_trytree_uses_refine_signature_and_comparator_and_gen_params():
    install_fake_dspy()
    with fresh_pkg():
        m = import_pkg()
        dspy = __import__("dspy")

        class RefSig(dspy.Signature):
            """Custom refine sig"""
            previous: str
            draft: str

        # Seeds from _batch; verify gen_params plumbed
        seen = {}

        async def fake_batch(text, n, model, gen_params=None):
            seen.update(gen_params=gen_params)
            return ["B", "A"]

        m._batch = fake_batch  # type: ignore[attr-defined]

        tt = m.TryTree(init_n=2, expand_k=1, iters=1, comparator=m.PairwiseBetter, gen_params={"temperature": 0.2}, refine_sig=RefSig)
        best = tt("Q")
        assert best.startswith("B")  # refined still ranks above A
        assert seen["gen_params"] == {"temperature": 0.2}

