import importlib


def test_env_overrides_max_iters(monkeypatch):
    monkeypatch.setenv("NLCO_MAX_ITERS", "7")
    # Reload module to pick up env
    mod = importlib.import_module("nlco_iter")
    importlib.reload(mod)
    assert mod.MAX_ITERATIONS == 7

