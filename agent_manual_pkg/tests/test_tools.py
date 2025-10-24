def test_run_shell_blocked(monkeypatch):
    from agent_manual_pkg.runtime.tools import run_shell
    from agent_manual_pkg.runtime import safety as safety_mod

    monkeypatch.setattr(safety_mod.SAFETY, "assess", lambda cmd: (False, "blocked"))
    out = run_shell("echo hi")
    assert out["status"] == "blocked"
    assert out["safety"]["passed"] is False


def test_run_shell_allowed(monkeypatch):
    from agent_manual_pkg.runtime.tools import run_shell
    from agent_manual_pkg.runtime import safety as safety_mod

    monkeypatch.setattr(safety_mod.SAFETY, "assess", lambda cmd: (True, "ok"))
    out = run_shell("echo hi")
    assert out["status"] == "ok"
    assert out["output"].strip() in {"hi", "hi\n".strip()}
    assert out["safety"]["passed"] is True

