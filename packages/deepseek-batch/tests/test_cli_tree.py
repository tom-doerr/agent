import sys
from .helpers import import_pkg, fresh_pkg, install_fake_dspy


def test_tree_cli_colors_and_calls(capsys):
    install_fake_dspy()
    with fresh_pkg():
        import importlib
        sys.modules.pop("deepseek_batch", None)
        sys.modules.pop("deepseek_batch.cli_tree", None)
        mod = import_pkg()

        class StubTree:
            def __init__(self, **kw):
                self.kw = kw
            def __call__(self, text):
                return f"TREE:{text}:{self.kw['init_n']}:{self.kw['expand_k']}:{self.kw['iters']}:{self.kw.get('model')}:{self.kw.get('gen_params',{}).get('temperature')}"

        mod.TryTree = StubTree  # type: ignore[attr-defined]
        cli = importlib.import_module("deepseek_batch.cli_tree")
        argv = sys.argv[:]
        try:
            sys.argv = [
                "deepseek-tree","Hi","--init-n","3","--expand-k","1","--iters","2","--model","M","--temperature","0.4",
            ]
            cli.main()
        finally:
            sys.argv = argv

        out = capsys.readouterr().out
        assert "\x1b[36mBEST\x1b[0m" in out
        assert "\x1b[1;32mTREE:Hi:3:1:2:M:0.4\x1b[0m" in out

