import timestamp_textual_app as mod


def test_constraints_newlines_respected(monkeypatch, tmp_path):
    c = tmp_path / "constraints.md"
    c.write_text("A\n\nB\nC")
    app = mod.TimestampLogApp(constraints_path=c)
    captured = {}

    class DummySize:
        def __init__(self, h: int) -> None:
            self.height = h

    class DummyMd:
        def __init__(self) -> None:
            self.size = DummySize(10)
        def update(self, text: str):
            captured["text"] = text

    class DummyTitle:
        def update(self, text: str):
            pass

    app._constraints_view = DummyMd()
    app._constraints_title = DummyTitle()
    app._load_constraints()
    txt = captured.get("text", "")
    # Each newline becomes an explicit markdown line break; double newline becomes two breaks
    assert "A  \n  \nB  \nC" in txt
