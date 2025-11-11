import timestamp_textual_app as mod


def test_constraints_missing_updates_view(tmp_path):
    c = tmp_path / "constraints.md"
    c.write_text("# 2025-11-11\n1200 hello\n")
    app = mod.TimestampLogApp(constraints_path=c)
    captured = {}

    class DummyMd:
        def update(self, text: str):
            captured["text"] = text

    class DummyTitle:
        def update(self, text: str):
            captured["title"] = text

    app._constraints_view = DummyMd()
    app._constraints_title = DummyTitle()
    app._load_constraints()
    assert "hello" in captured.get("text", "")

    # Remove file; refresh should show not found
    c.unlink()
    app._maybe_refresh_constraints()
    assert "not found" in captured.get("text", "")

