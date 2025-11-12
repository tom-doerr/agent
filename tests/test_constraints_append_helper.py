from constraints_io import build_append_block


def test_build_append_block_first_entry_needs_heading():
    out = build_append_block(existing="", needs_heading=True, date_str="2025-11-12", line="1200 hello")
    assert out == "# 2025-11-12\n1200 hello\n"


def test_build_append_block_same_day_no_duplicate_heading():
    existing = "# 2025-11-12\n1200 first\n"
    out = build_append_block(existing, needs_heading=False, date_str="2025-11-12", line="1215 second")
    assert out == "1215 second\n"


def test_build_append_block_next_day_adds_blank_line_and_heading_when_no_trailing_newline():
    existing = "# 2025-11-11\n1234 existing line"  # note: no trailing newline
    out = build_append_block(existing, True, "2025-11-12", "0801 new day")
    assert out == "\n\n# 2025-11-12\n0801 new day\n"

