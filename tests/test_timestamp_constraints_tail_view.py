
import timestamp_textual_app as mod


def test_constraints_tail_shows_bottom(monkeypatch, tmp_path):
    c = tmp_path / "constraints.md"
    lines = "\n".join(f"L{i:03d}" for i in range(1, 301))
    c.write_text(lines)

    app = mod.TimestampLogApp(constraints_path=c)
    captured = {}

    class DummySize:
        def __init__(self, h: int) -> None:
            self.height = h

    class DummyMd:
        def __init__(self) -> None:
            # Simulate a 10-row pane -> tail = 8
            self.size = DummySize(10)
        def update(self, text: str):
            captured["text"] = text

    class DummyTitle:
        def update(self, text: str):
            captured["title"] = text

    app._constraints_view = DummyMd()
    app._constraints_title = DummyTitle()

    # Tail derives from pane height (10 -> 8). Expect last 8 lines L293..L300.
    app._load_constraints()
    txt = captured.get("text", "")
    assert "L293" in txt and "L292" not in txt
    assert txt.splitlines()[0].startswith("L293")
    assert txt.splitlines()[-1].startswith("L300") or "L300" in txt
