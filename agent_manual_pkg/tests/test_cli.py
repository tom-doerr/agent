import os


def test_cli_configures_model_and_runs_tui(tmp_path, monkeypatch):
    from agent_manual_pkg import cli

    cfg = tmp_path / "cfg.json"
    os.environ["AGENT_MANUAL_CONFIG"] = str(cfg)

    called = {}

    def fake_configure(model, max_tokens=None, persist=True):
        called["args"] = (model, max_tokens, persist)

    class DummyTUI:
        def __init__(self, *a, **k):
            called["tui_init"] = True

        def run(self):
            called["tui_run"] = True

    monkeypatch.setattr("agent_manual_pkg.cli.configure_model", fake_configure)
    monkeypatch.setattr("agent_manual_pkg.cli.TUI", DummyTUI)

    cli.main(["--config", str(cfg), "--model", "chat", "--max-tokens", "123"])

    assert called.get("tui_init") and called.get("tui_run")
    assert called.get("args") == ("chat", 123, True)

