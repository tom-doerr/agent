import timestamp_app_core as core


def test_core_constraints_height():
    css = core.TimestampLogApp.CSS
    assert "#constraints-container" in css and "height: 8;" in css

