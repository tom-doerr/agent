import sys
import types

import timestamp_textual_app as mod


def _raising_decode(data: bytes, final: bool = False) -> str:  # mimics Textual's decode signature
    raise UnicodeDecodeError("utf-8", data or b"\x99", 0, 1, "invalid start byte")


def test_lenient_input_opt_in(monkeypatch):
    dummy_driver = types.SimpleNamespace(decode=_raising_decode)
    dummy_pkg = types.SimpleNamespace(linux_driver=dummy_driver)
    monkeypatch.setitem(sys.modules, "textual.drivers", dummy_pkg)
    monkeypatch.setitem(sys.modules, "textual.drivers.linux_driver", dummy_driver)
    monkeypatch.setenv("TIMESTAMP_LENIENT_INPUT", "1")
    monkeypatch.setenv("TEXTUAL_FALLBACK_ENCODING", "cp1252")

    mod._maybe_enable_lenient_input()

    out = dummy_driver.decode(b"Hello \x99", True)
    assert "Hello" in out and ("\u2122" in out or "™" in out)


def test_lenient_input_default_off(monkeypatch):
    dummy_driver = types.SimpleNamespace(decode=_raising_decode)
    monkeypatch.setitem(sys.modules, "textual.drivers.linux_driver", dummy_driver)
    monkeypatch.delenv("TIMESTAMP_LENIENT_INPUT", raising=False)

    # Should not patch when not enabled
    mod._maybe_enable_lenient_input()
    try:
        dummy_driver.decode(b"\x99", True)
        assert False, "expected UnicodeDecodeError"
    except UnicodeDecodeError:
        pass
