import types

import timestamp_textual_app as mod


class DummyEvent:
    def __init__(self, key: str):
        self.key = key
        self._stopped = False

    def stop(self):
        self._stopped = True


def test_ga_focuses_artifact_view(monkeypatch):
    app = mod.TimestampLogApp()
    # Install dummies
    artifact = types.SimpleNamespace(id="artifact-view")
    app._artifact_view = artifact
    app._input = types.SimpleNamespace(id="input")
    # Make app.focused return a dummy so app.on_key doesn't crash when not running
    import types as _types
    mod.TimestampLogApp.focused = property(lambda self: _types.SimpleNamespace(id="log"))  # type: ignore[attr-defined]
    called = {}

    def record_focus(widget):
        called["widget"] = widget

    app.set_focus = record_focus  # type: ignore[assignment]

    # Press 'g' then 'a'
    app.on_key(DummyEvent("g"))
    app.on_key(DummyEvent("a"))

    assert called.get("widget") is artifact
