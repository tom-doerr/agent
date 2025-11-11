import os
import timestamp_textual_app as mod


def test_parse_cli_pad_eol_sets_env(monkeypatch):
    monkeypatch.delenv("TIMESTAMP_PAD_EOL", raising=False)
    mod._parse_cli(["--pad-eol"])  # type: ignore[arg-type]
    assert os.environ.get("TIMESTAMP_PAD_EOL") == "1"

