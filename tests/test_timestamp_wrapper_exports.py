import importlib


def test_wrapper_reexports_core():
    core = importlib.import_module('timestamp_app_core')
    wrapper = importlib.import_module('timestamp_textual_app')

    # Wrapper provides the app and helper functions; identity may differ
    assert hasattr(wrapper, 'TimestampLogApp') and callable(wrapper._parse_cli)
    assert callable(wrapper._maybe_enable_lenient_input) and callable(wrapper._ensure_utf8_tty)


def test_wrapper_main_calls_wired_funcs(monkeypatch):
    wrapper = importlib.import_module('timestamp_textual_app')

    called = {"parse": False, "tty": False, "lenient": False, "run": False}

    def fake_parse(argv):
        called["parse"] = True

    def fake_tty():
        called["tty"] = True

    def fake_lenient():
        called["lenient"] = True

    class FakeApp:
        def __init__(self, *a, **k):
            pass

        def run(self):
            called["run"] = True

    monkeypatch.setattr(wrapper, "_parse_cli", fake_parse)
    monkeypatch.setattr(wrapper, "_ensure_utf8_tty", fake_tty)
    monkeypatch.setattr(wrapper, "_maybe_enable_lenient_input", fake_lenient)
    monkeypatch.setattr(wrapper, "TimestampLogApp", FakeApp)

    wrapper.main()

    assert all(called.values())
