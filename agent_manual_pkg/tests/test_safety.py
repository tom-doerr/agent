import types


def test_safety_allows_when_model_says_allow(monkeypatch):
    from agent_manual_pkg.runtime.safety import SafetyCheck
    import dspy

    class DummyPredict:
        def __init__(self, *a, **k):
            pass

        def __call__(self, *, command):
            return types.SimpleNamespace(decision="allow", reason="ok")

    monkeypatch.setattr(dspy, "Predict", DummyPredict)
    ok, reason = SafetyCheck().assess("echo hi")
    assert ok is True
    assert reason


def test_safety_blocks_when_model_says_block(monkeypatch):
    from agent_manual_pkg.runtime.safety import SafetyCheck
    import dspy

    class DummyPredict:
        def __init__(self, *a, **k):
            pass

        def __call__(self, *, command):
            return types.SimpleNamespace(decision="block", reason="nope")

    monkeypatch.setattr(dspy, "Predict", DummyPredict)
    ok, reason = SafetyCheck().assess("cat /etc/shadow")
    assert ok is False
    assert "nope" in reason

