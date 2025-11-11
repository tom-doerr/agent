import timestamp_textual_app as mod


def test_constraints_css_has_right_padding():
    css = mod.TimestampLogApp.CSS
    assert "#constraints-view" in css
    # Ensure we keep a 1-col right padding to dodge last-column clipping on some terminals
    assert "padding: 1 2;" in css
