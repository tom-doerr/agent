import sys
from .helpers import install_fake_dspy, fresh_pkg, import_pkg


def test_cli_colors_and_args(capsys):
    install_fake_dspy()
    with fresh_pkg():
        import importlib
        sys.modules.pop("deepseek_batch", None)
        sys.modules.pop("deepseek_batch.cli", None)
        pkg = import_pkg()

        def fake_batch_best(text, n=4, model=None, include_original=True, gen_params=None):
            temp = gen_params.get("temperature") if isinstance(gen_params, dict) else None
            return f"OK:{text}:{n}:{model}:{include_original}:{temp}"

        pkg.batch_best = fake_batch_best
        cli = importlib.import_module("deepseek_batch.cli")
        argv = sys.argv[:]
        try:
            sys.argv = [
                "deepseek-batch",
                "Hello",
                "-n","5",
                "--model","M",
                "--no-include-original",
                "--temperature","0.1",
            ]
            cli.main()
        finally:
            sys.argv = argv

        out = capsys.readouterr().out.strip()
        assert out.startswith("\x1b[36mBEST\x1b[0m: ")
        assert "OK:Hello:5:M:False:0.1" in out

