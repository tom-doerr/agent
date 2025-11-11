import types

import timestamp_textual_app as mod


def test_help_bindings_include_f1():
    assert any(b[0] == "f1" and b[1] == "toggle_help" for b in mod.TimestampLogApp.BINDINGS)


def test_toggle_help_action_toggles_panel(monkeypatch):
    app = mod.TimestampLogApp()

    class DummyPanel:
        def __init__(self):
            self.visible = False
            self.text = ""

        def update(self, s: str):
            self.text = s

    app._help_panel = DummyPanel()
    app._help_visible = False
    # First toggle shows help
    app.action_toggle_help()
    assert app._help_panel.visible is True
    assert isinstance(app._help_message, str) and app._help_message
    # Second toggle hides help
    app.action_toggle_help()
    assert app._help_panel.visible is False
    assert app._help_message == ""

