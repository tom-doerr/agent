import sys
import runpy
import types

import pytest


def test_script_entry_calls_lenient_hook(monkeypatch):
    # Make TTY + locale checks pass
    monkeypatch.setattr(sys, "stdin", types.SimpleNamespace(isatty=lambda: True))
    monkeypatch.setattr(sys, "stdout", types.SimpleNamespace(isatty=lambda: True))
    monkeypatch.setenv("LANG", "en_US.UTF-8")

    # Opt-in to lenient mode so the script references the hook
    monkeypatch.setenv("TIMESTAMP_LENIENT_INPUT", "1")

    # Prevent actually running a UI loop: force App.run to raise decode error which main catches
    import textual.app

    def fake_run(self):
        raise UnicodeDecodeError("utf-8", b"\x99", 0, 1, "invalid start byte")

    monkeypatch.setattr(textual.app.App, "run", fake_run)

    with pytest.raises(SystemExit) as exc:
        runpy.run_path("timestamp_textual_app.py", run_name="__main__")
    assert exc.value.code == 2

