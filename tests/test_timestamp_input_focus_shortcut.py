import types

import timestamp_textual_app as mod


class DummyEvent:
    def __init__(self, key: str):
        self.key = key
        self._stopped = False

    def stop(self):
        self._stopped = True


def test_gi_focuses_input():
    app = mod.TimestampLogApp()
    app._input = types.SimpleNamespace(id="input")
    app._artifact_view = types.SimpleNamespace(id="artifact-view")

    called = {}

    def record_focus(widget):
        called["widget"] = widget

    app.set_focus = record_focus  # type: ignore[assignment]
    # Simulate not currently focusing input
    import types as _types
    mod.TimestampLogApp.focused = property(lambda self: _types.SimpleNamespace(id="constraints-view"))  # type: ignore[attr-defined]

    app.on_key(DummyEvent("g"))
    app.on_key(DummyEvent("i"))
    assert called.get("widget") is app._input

