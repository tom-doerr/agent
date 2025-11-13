import importlib
import os


def test_webconfig_defaults_use_shared_resolvers(monkeypatch, tmp_path):
    # Point private dir to a temp location and clear any explicit overrides
    monkeypatch.setenv("NLCO_PRIVATE_DIR", str(tmp_path / ".nlco" / "private"))
    monkeypatch.delenv("TIMESTAMP_MEMORY_PATH", raising=False)
    monkeypatch.delenv("TIMESTAMP_SHORT_TERM_PATH", raising=False)

    core = importlib.import_module("timestamp_app_core")
    importlib.reload(core)

    app_mod = importlib.import_module("webapp.nlco_htmx.app")
    importlib.reload(app_mod)

    cfg = app_mod.WebConfig()
    assert cfg.memory_path == core.resolve_memory_path()
    assert cfg.short_term_memory_path == core.resolve_short_term_path()

