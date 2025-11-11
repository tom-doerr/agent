import textwrap

import timestamp_textual_app as mod


def test_constraints_tail_shows_bottom(monkeypatch, tmp_path):
    c = tmp_path / "constraints.md"
    lines = "\n".join(f"L{i:03d}" for i in range(1, 301))
    c.write_text(lines)

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

    # Default tail is 200; we expect to see L101..L300
    app._load_constraints()
    txt = captured.get("text", "")
    assert "L101" in txt and "L100" not in txt
    assert txt.splitlines()[0].startswith("L101")
    assert txt.splitlines()[-1].startswith("L300") or "L300" in txt
