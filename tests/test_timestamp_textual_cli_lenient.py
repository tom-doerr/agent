import runpy
import sys
import types
import subprocess



def test_cli_lenient_enables_decode_fallback(monkeypatch):
    # Make TTY + locale checks pass
    monkeypatch.setattr(sys, "stdin", types.SimpleNamespace(isatty=lambda: True))
    monkeypatch.setattr(sys, "stdout", types.SimpleNamespace(isatty=lambda: True))
    monkeypatch.setenv("LANG", "en_US.UTF-8")

    class Dummy:
        def __init__(self):
            self.returncode = 0
            self.stdout = "speed 38400 baud; rows 50; columns 150; iutf8"
            self.stderr = ""

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: Dummy())

    # Provide a dummy Textual driver and App.run
    def raising_decode(data: bytes, final: bool = False) -> str:
        raise UnicodeDecodeError("utf-8", data or b"\x99", 0, 1, "invalid start byte")

    dummy_driver = types.SimpleNamespace(
        decode=raising_decode,
        LinuxDriver=type("LinuxDriver", (), {}),
    )
    dummy_pkg = types.SimpleNamespace(linux_driver=dummy_driver)
    monkeypatch.setitem(sys.modules, "textual.drivers", dummy_pkg)
    monkeypatch.setitem(sys.modules, "textual.drivers.linux_driver", dummy_driver)

    import textual.app

    def fake_run(self):
        return None

    monkeypatch.setattr(textual.app.App, "run", fake_run)

    # Simulate CLI flags
    monkeypatch.setenv("PYTHONPATH", ".")
    argv_backup = sys.argv[:]
    sys.argv = ["timestamp_textual_app.py", "--lenient-input", "--fallback-encoding", "cp1252"]

    try:
        runpy.run_path("timestamp_textual_app.py", run_name="__main__")
    finally:
        sys.argv = argv_backup

    # After script ran, the driver.decode should have been patched to a safe decoder
    out = dummy_driver.decode(b"Hello \x99", True)
    assert "Hello" in out and ("\u2122" in out or "™" in out)
