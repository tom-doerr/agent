import os
import timestamp_textual_app as mod


def test_parse_cli_constraints_rows_sets_env(monkeypatch):
    monkeypatch.delenv("TIMESTAMP_CONSTRAINTS_ROWS", raising=False)
    mod._parse_cli(["--constraints-rows", "15"])  # type: ignore[arg-type]
    assert os.environ.get("TIMESTAMP_CONSTRAINTS_ROWS") == "15"

