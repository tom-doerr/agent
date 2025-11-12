import timestamp_textual_app as mod

def test_tail_uses_view_height_and_ignores_env(monkeypatch, tmp_path):
    # Prepare constraints with 100 lines
    c = tmp_path / "constraints.md"
    c.write_text("\n".join(f"L{i:03d}" for i in range(1, 101)), encoding="utf-8")

    app = mod.TimestampLogApp(constraints_path=c)
    # Even if env is set, height-derived tail should be used
    monkeypatch.setenv("TIMESTAMP_CONSTRAINTS_TAIL", "999")
    captured = {}

    class DummySize:
        def __init__(self, h: int) -> None:
            self.height = h

    class DummyMd:
        def __init__(self) -> None:
            self.size = DummySize(6)  # tail = 4
        def update(self, text: str):
            captured["text"] = text

    class DummyTitle:
        def update(self, text: str):
            captured["title"] = text

    app._constraints_view = DummyMd()
    app._constraints_title = DummyTitle()
    app._load_constraints()
    txt = captured.get("text", "")
    assert "L097" in txt and "L096" not in txt


def test_md_preserve_lines():
    app = mod.TimestampLogApp()
    text = "a\nb\n"
    assert app._md_preserve_lines(text) == "a  \nb  \n"


def test_maybe_scroll_constraints_end_scrolls_when_not_focused(monkeypatch):
    app = mod.TimestampLogApp()
    calls = {"n": 0}

    class Dummy:
        def scroll_end(self, animate: bool = False):  # noqa: ARG002
            calls["n"] += 1

    app._constraints_view = Dummy()
    # Ensure auto-scroll is on
    app._auto_scroll = True  # type: ignore[attr-defined]
    app._maybe_scroll_constraints_end()
    assert calls["n"] == 1


def test_maybe_scroll_constraints_end_skips_when_focused(monkeypatch):
    app = mod.TimestampLogApp()
    calls = {"n": 0}

    class Dummy:
        def scroll_end(self, animate: bool = False):  # noqa: ARG002
            calls["n"] += 1

    app._constraints_view = Dummy()
    app._auto_scroll = True  # type: ignore[attr-defined]
    # Simulate focus on constraints view
    monkeypatch.setattr(mod.TimestampLogApp, "focused", property(lambda s: getattr(s, "_constraints_view", None)), raising=False)
    app._maybe_scroll_constraints_end()
    assert calls["n"] == 0
