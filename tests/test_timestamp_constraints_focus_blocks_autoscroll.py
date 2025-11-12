
import timestamp_textual_app as mod


def test_focus_blocks_auto_scroll(tmp_path, monkeypatch):
    c = tmp_path / "constraints.md"
    c.write_text("# 2025-11-11\n1200 hello\n")
    app = mod.TimestampLogApp(constraints_path=c)

    captured = {}

    class DummyMd:
        def update(self, text: str):
            captured["text"] = text
        def scroll_end(self, animate: bool = False):  # noqa: ARG002
            captured["scrolled"] = True

    class DummyTitle:
        def update(self, text: str):
            captured["title"] = text

    app._constraints_view = DummyMd()
    app._constraints_title = DummyTitle()
    # Pretend constraints view is focused
    orig_focused = mod.TimestampLogApp.focused
    try:
        mod.TimestampLogApp.focused = property(lambda self: app._constraints_view)  # type: ignore[attr-defined]
        app._load_constraints()
        assert captured.get("scrolled") is None
    finally:
        mod.TimestampLogApp.focused = orig_focused
