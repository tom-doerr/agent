from datetime import datetime
from pathlib import Path

from webapp.nlco_htmx import utils


def test_write_constraints_entry_uses_shared_append_block(tmp_path: Path) -> None:
    c = tmp_path / "constraints.md"
    # Start with a line that lacks trailing newline to exercise blank-line insertion
    c.write_text("# 2025-11-11\n1234 existing", encoding="utf-8")
    # Next day entry
    formatted, day = utils.write_constraints_entry(
        c, "new day", now=datetime(2025, 11, 12, 8, 1, 0)
    )
    out = c.read_text(encoding="utf-8")
    assert formatted == "08:01:00 new day"
    # Expect a separating blank line, a new heading, then the line
    assert "existing\n\n# 2025-11-12\n08:01:00 new day\n" in out
