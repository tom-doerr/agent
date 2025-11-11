import timestamp_textual_app as appmod


def test_constraints_container_height_is_8():
    css = appmod.TimestampLogApp.CSS
    assert "#constraints-container" in css and "height: 8;" in css

