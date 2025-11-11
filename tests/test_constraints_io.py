from pathlib import Path
from constraints_io import tail_lines, append_line


def test_tail_and_append(tmp_path: Path):
    p = tmp_path / "c.md"
    p.write_text("A\nB\n")
    append_line(p, "C")
    assert p.read_text().endswith("C\n")
    assert tail_lines(p, 2) == ["B", "C"]

