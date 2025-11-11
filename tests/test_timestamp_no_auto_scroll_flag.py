import os
import types

import timestamp_textual_app as mod


def test_no_auto_scroll_env_disables_scrolling(tmp_path, monkeypatch):
    c = tmp_path / "constraints.md"
    c.write_text("# 2025-11-11\n1200 hello\n")
    monkeypatch.setenv("TIMESTAMP_AUTO_SCROLL", "0")
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
    assert captured.get("scrolled") is None


def test_no_auto_scroll_cli_flag_sets_env(monkeypatch):
    monkeypatch.delenv("TIMESTAMP_AUTO_SCROLL", raising=False)
    mod._parse_cli(["--no-auto-scroll"])  # type: ignore[arg-type]
    assert os.environ.get("TIMESTAMP_AUTO_SCROLL") == "0"

