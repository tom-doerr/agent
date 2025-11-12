import os

import timestamp_textual_app as mod


def test_constraints_refresh_on_mtime_change(tmp_path):
    c = tmp_path / "constraints.md"
    c.write_text("# 2025-11-11\n1200 old\n")
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
    old_mtime = app._constraints_mtime
    assert "old" in captured.get("text", "")

    # Modify file and bump mtime
    c.write_text("# 2025-11-11\n1215 new\n")
    if old_mtime is not None:
        os.utime(c, (old_mtime + 2, old_mtime + 2))

    app._maybe_refresh_constraints()
    assert "1215 new" in captured.get("text", "")

