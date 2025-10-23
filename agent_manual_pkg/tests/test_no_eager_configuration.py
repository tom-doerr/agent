import importlib


def test_runtime_does_not_eagerly_configure_agent():
    mod = importlib.import_module("agent_manual_pkg.runtime.configuration")
    assert getattr(mod, "_AGENT", None) is None

