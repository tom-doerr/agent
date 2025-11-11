import nootropics_log as nl


def test_append_nootropics_section_appends():
    def fake_load(**kwargs):
        return ['{"ts":"2025-11-06 10:00:00","note":"alpha"}', '{"ts":"2025-11-06 11:00:00","note":"beta"}']

    orig = nl.load_recent_nootropics_lines
    nl.load_recent_nootropics_lines = fake_load  # monkeypatch manually to avoid fixture dependency
    try:
        out = nl.append_nootropics_section("CTX")
        assert "Nootropics (last 72h)" in out
        assert "alpha" in out and "beta" in out
    finally:
        nl.load_recent_nootropics_lines = orig


def test_append_nootropics_section_noop_when_empty():
    def fake_empty(**kwargs):
        return []

    orig = nl.load_recent_nootropics_lines
    nl.load_recent_nootropics_lines = fake_empty
    try:
        out = nl.append_nootropics_section("CTX")
        assert out == "CTX"
    finally:
        nl.load_recent_nootropics_lines = orig

