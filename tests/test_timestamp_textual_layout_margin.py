import timestamp_textual_app as mod


def test_log_css_has_right_padding():
    css = mod.TimestampLogApp.CSS
    assert "Log {" in css
    # Ensure we keep a 1-col right padding to dodge last-column clipping on some terminals
    assert "padding: 1 2;" in css

