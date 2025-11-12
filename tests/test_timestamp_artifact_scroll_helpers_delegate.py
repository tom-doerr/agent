import timestamp_textual_app as mod
import timestamp_app_core as core


def test_artifact_page_down_uses_core_helper(monkeypatch):
    app = mod.TimestampLogApp()
    called = {"n": 0, "arg": None}

    def spy(view):
        called["n"] += 1
        called["arg"] = view

    monkeypatch.setattr(mod, "_core_scroll_page_down", spy, raising=False)
    dummy = object()
    app._artifact_view = dummy  # type: ignore[assignment]
    app.action_artifact_page_down()
    assert called["n"] == 1 and called["arg"] is dummy


def test_artifact_page_up_uses_core_helper(monkeypatch):
    app = mod.TimestampLogApp()
    called = {"n": 0, "arg": None}

    def spy(view):
        called["n"] += 1
        called["arg"] = view

    monkeypatch.setattr(mod, "_core_scroll_page_up", spy, raising=False)
    dummy = object()
    app._artifact_view = dummy  # type: ignore[assignment]
    app.action_artifact_page_up()
    assert called["n"] == 1 and called["arg"] is dummy

