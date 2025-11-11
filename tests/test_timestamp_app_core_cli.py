import os
import importlib


def test_parse_cli_sets_env(monkeypatch):
    mod = importlib.import_module('timestamp_app_core')
    # Clear possibly set vars first
    for k in [
        'TIMESTAMP_LENIENT_INPUT', 'TEXTUAL_FALLBACK_ENCODING', 'TIMESTAMP_RIGHT_MARGIN',
        'TIMESTAMP_AUTO_SCROLL', 'TIMESTAMP_CONSTRAINTS_TAIL', 'TIMESTAMP_PAD_EOL',
    ]:
        monkeypatch.delenv(k, raising=False)

    mod._parse_cli([
        '--lenient-input', '--fallback-encoding', 'latin1', '--right-margin', '3',
        '--no-auto-scroll', '--constraints-tail', '123', '--pad-eol',
    ])

    assert os.environ.get('TIMESTAMP_LENIENT_INPUT') == '1'
    assert os.environ.get('TEXTUAL_FALLBACK_ENCODING') == 'latin1'
    assert os.environ.get('TIMESTAMP_RIGHT_MARGIN') == '3'
    assert os.environ.get('TIMESTAMP_AUTO_SCROLL') == '0'
    assert os.environ.get('TIMESTAMP_CONSTRAINTS_TAIL') == '123'
    assert os.environ.get('TIMESTAMP_PAD_EOL') == '1'

