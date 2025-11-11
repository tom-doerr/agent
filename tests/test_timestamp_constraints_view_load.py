from pathlib import Path
import types

import timestamp_textual_app as mod


def test_load_constraints_updates_markdown(tmp_path, monkeypatch):
    monkeypatch.delenv("TIMESTAMP_AUTO_SCROLL", raising=False)
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
    app._load_constraints()
    assert "1200 hello" in captured.get("text", "")
    assert str(c) in captured.get("title", "")
    assert captured.get("scrolled") is True
