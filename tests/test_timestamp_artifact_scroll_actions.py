import timestamp_textual_app as mod


def test_artifact_page_actions_invoke_scroll_methods():
    app = mod.TimestampLogApp()
    called = {"down": 0, "up": 0}

    class DummyView:
        def scroll_page_down(self):
            called["down"] += 1
        def scroll_page_up(self):
            called["up"] += 1

    app._artifact_view = DummyView()
    app.action_artifact_page_down()
    app.action_artifact_page_up()
    assert called["down"] == 1 and called["up"] == 1


def test_artifact_page_down_fallback_relative():
    app = mod.TimestampLogApp()
    called = {"rel": 0}

    class DummyView:
        # no scroll_page_down
        def scroll_relative(self, y: int = 0):
            if y > 0:
                called["rel"] += 1

    app._artifact_view = DummyView()
    app.action_artifact_page_down()
    assert called["rel"] == 1


def test_artifact_page_up_fallback_home():
    app = mod.TimestampLogApp()
    called = {"home": 0}

    class DummyView:
        # no scroll_page_up, no scroll_relative
        def scroll_home(self, animate: bool = False):
            called["home"] += 1

    app._artifact_view = DummyView()
    app.action_artifact_page_up()
    assert called["home"] == 1
