from tests.helpers import install_fake_dspy, fresh_pkg, import_pkg


def test_blueberries_reverse():
    install_fake_dspy()
    with fresh_pkg():
        m = import_pkg()
        assert m.batch_best("blueberries") == "seirrebeulb"
