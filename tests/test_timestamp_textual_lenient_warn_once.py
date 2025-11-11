import os
import sys
import types

import timestamp_textual_app as mod


def _raising_decode(data: bytes, final: bool = False) -> str:  # pragma: no cover - helper used by test
    raise UnicodeDecodeError("utf-8", data or b"\x99", 0, 1, "invalid start byte")


def test_lenient_warns_once(monkeypatch, capsys):
    dummy_driver = types.SimpleNamespace(decode=_raising_decode)
    # Ensure import path and attribute resolution both point to our dummy
    dummy_pkg = types.SimpleNamespace(linux_driver=dummy_driver)
    monkeypatch.setitem(sys.modules, "textual.drivers", dummy_pkg)
    monkeypatch.setitem(sys.modules, "textual.drivers.linux_driver", dummy_driver)
    monkeypatch.setenv("TIMESTAMP_LENIENT_INPUT", "1")
    monkeypatch.setenv("TEXTUAL_FALLBACK_ENCODING", "cp1252")

    # Reset module-level flag if a prior test set it
    mod._lenient_warned = False
    mod._maybe_enable_lenient_input()

    dummy_driver.decode(b"\x99", True)
    dummy_driver.decode(b"\x8e", True)
    err = capsys.readouterr().err
    # Only one warning line expected
    assert err.count("lenient input enabled") == 1
