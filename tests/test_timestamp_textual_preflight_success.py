import types
import subprocess
import sys

import timestamp_textual_app as mod


def test_preflight_success(monkeypatch):
    monkeypatch.setattr(sys, "stdin", types.SimpleNamespace(isatty=lambda: True))
    monkeypatch.setattr(sys, "stdout", types.SimpleNamespace(isatty=lambda: True))
    monkeypatch.setenv("LANG", "en_US.UTF-8")

    class Dummy:
        def __init__(self):
            self.returncode = 0
            self.stdout = "speed 38400 baud; rows 50; columns 150; iutf8"
            self.stderr = ""

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: Dummy())
    # Should not raise
    mod._ensure_utf8_tty()

