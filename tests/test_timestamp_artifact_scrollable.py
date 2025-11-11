import timestamp_textual_app as mod


def test_css_makes_artifact_scrollable():
    css = mod.TimestampLogApp.CSS
    # Ensure the artifact view enables overflow auto
    assert "#artifact-view" in css
    assert "overflow: auto" in css

