import types
import subprocess

import pytest

import timestamp_textual_app as mod
import sys as _sys


def _isatty_true():
    return True


def _isatty_false():
    return False


def test_preflight_exits_when_not_tty(monkeypatch, capsys):
    monkeypatch.setattr(_sys, "stdin", types.SimpleNamespace(isatty=_isatty_false))
    monkeypatch.setattr(_sys, "stdout", types.SimpleNamespace(isatty=_isatty_false))
    with pytest.raises(SystemExit) as exc:
        mod._ensure_utf8_tty()
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "requires an interactive UTF-8 terminal" in err


def test_preflight_exits_when_locale_not_utf8(monkeypatch, capsys):
    monkeypatch.setattr(_sys, "stdin", types.SimpleNamespace(isatty=_isatty_true))
    monkeypatch.setattr(_sys, "stdout", types.SimpleNamespace(isatty=_isatty_true))
    monkeypatch.setenv("LANG", "C")
    monkeypatch.delenv("LC_ALL", raising=False)
    monkeypatch.delenv("LC_CTYPE", raising=False)
    with pytest.raises(SystemExit) as exc:
        mod._ensure_utf8_tty()
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "Non-UTF-8 locale" in err


def test_preflight_exits_when_iutf8_missing(monkeypatch, capsys):
    monkeypatch.setattr(_sys, "stdin", types.SimpleNamespace(isatty=_isatty_true))
    monkeypatch.setattr(_sys, "stdout", types.SimpleNamespace(isatty=_isatty_true))
    monkeypatch.setenv("LANG", "en_US.UTF-8")

    class DummyCompleted:
        def __init__(self):
            self.returncode = 0
            self.stdout = "speed 38400 baud; rows 50; columns 150; -iutf8"
            self.stderr = ""

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: DummyCompleted())

    with pytest.raises(SystemExit) as exc:
        mod._ensure_utf8_tty()
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "TTY UTF-8 input not enabled" in err
