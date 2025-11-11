from datetime import datetime

import timestamp_textual_app as mod


def test_format_line():
    app = mod.TimestampLogApp()
    t = datetime(2025, 11, 11, 7, 5, 33)
    assert app._format_line("hello", t) == "0705 hello"

