

class StubNode:
    def __init__(self) -> None:
        self.classes = set()

    def add_class(self, name: str) -> None:
        self.classes.add(name)

    def remove_class(self, name: str) -> None:
        self.classes.discard(name)


def test_layout_toggle(monkeypatch):
    from agent_manual_pkg.tui import TUI

    app = TUI()
    content = StubNode()
    log = StubNode()

    def fake_query_one(selector, widget_type=None):
        if selector == "#content":
            return content
        if selector == "#log":
            return log
        raise AssertionError(selector)

    monkeypatch.setattr(app, "query_one", fake_query_one)

    app._set_layout("stacked")
    assert "stacked" in content.classes
    assert "stacked" in log.classes

    app._set_layout("wide")
    assert "stacked" not in content.classes
    assert "stacked" not in log.classes

