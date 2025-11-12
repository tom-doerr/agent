import types
import sys

import pytest

import timestamp_textual_app as mod


def test_main_catches_unicode_decode_and_exits(monkeypatch, capsys):
    # Pretend we are in a real UTF-8 TTY so preflight passes
    monkeypatch.setattr(sys, "stdin", types.SimpleNamespace(isatty=lambda: True))
    monkeypatch.setattr(sys, "stdout", types.SimpleNamespace(isatty=lambda: True))
    monkeypatch.setenv("LANG", "en_US.UTF-8")

    # Force the run to raise UnicodeDecodeError like Textual would
    class DummyApp:
        def run(self):
            raise UnicodeDecodeError("utf-8", b"\x97", 0, 1, "invalid start byte")

    monkeypatch.setattr(mod, "TimestampLogApp", lambda: DummyApp())

    with pytest.raises(SystemExit) as exc:
        mod.main()
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "non-utf-8 bytes" in err.lower()
