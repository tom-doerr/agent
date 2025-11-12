from datetime import date
from pathlib import Path

import timestamp_textual_app as mod


def _app(tmp_path: Path) -> mod.TimestampLogApp:
    return mod.TimestampLogApp(artifact_path=tmp_path / "artifact.md", constraints_path=tmp_path / "constraints.md")


def test_append_first_entry_creates_heading_and_line(tmp_path):
    app = _app(tmp_path)
    app._prepare_constraints()
    d = date(2025, 11, 11)
    app._append_to_constraints(d, "12:00:00 hello")
    text = (tmp_path / "constraints.md").read_text()
    assert text.endswith("12:00:00 hello\n")
    assert "# 2025-11-11" in text


def test_append_same_day_does_not_duplicate_heading(tmp_path):
    app = _app(tmp_path)
    app._prepare_constraints()
    d = date(2025, 11, 11)
    app._append_to_constraints(d, "12:00:00 first")
    app._append_to_constraints(d, "12:15:00 second")
    text = (tmp_path / "constraints.md").read_text()
    assert text.count("# 2025-11-11") == 1
    assert "12:00:00 first\n" in text and "12:15:00 second\n" in text


def test_append_next_day_adds_new_heading_even_without_trailing_newline(tmp_path):
    cpath = tmp_path / "constraints.md"
    cpath.write_text("# 2025-11-11\n12:34:00 existing line")  # no trailing newline
    app = _app(tmp_path)
    app._prepare_constraints()
    app._last_constraints_date = date(2025, 11, 11)
    app._append_to_constraints(date(2025, 11, 12), "08:01:00 new day")
    text = cpath.read_text()
    assert "# 2025-11-12\n08:01:00 new day\n" in text
    # Ensure a newline was inserted before the new heading
    assert "existing line\n\n# 2025-11-12" in text
