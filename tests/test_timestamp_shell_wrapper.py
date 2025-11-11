from pathlib import Path


def test_shell_wrapper_contents():
    path = Path("timestamp_tui.sh")
    text = path.read_text()
    assert "stty iutf8" in text
    assert "LANG=en_US.UTF-8" in text
    assert "LC_ALL=en_US.UTF-8" in text
    assert "timestamp_textual_app.py --lenient-input" in text

