import nlco_textual


def test_layout_heights_are_adjusted():
    css = nlco_textual.NLCOTextualApp.CSS
    assert "#constraints-pane" in css and "height: 8;" in css
    assert "#editor-row" in css and "height: 30;" in css
