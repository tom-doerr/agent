import os
import timestamp_textual_app as mod


def test_parse_right_margin_sets_env(monkeypatch):
    monkeypatch.delenv("TIMESTAMP_RIGHT_MARGIN", raising=False)
    mod._parse_cli(["--right-margin", "4"])  # type: ignore[arg-type]
    assert os.environ.get("TIMESTAMP_RIGHT_MARGIN") == "4"

