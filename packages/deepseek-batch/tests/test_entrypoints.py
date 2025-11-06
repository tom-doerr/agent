import tomllib


def test_scripts_declared_in_pyproject():
    import os
    here = os.path.dirname(__file__)
    pyproj = os.path.join(os.path.dirname(here), "pyproject.toml")
    with open(pyproj, "rb") as f:
        data = tomllib.load(f)
    scripts = data["tool"]["poetry"]["scripts"]
    assert scripts["deepseek-batch"] == "deepseek_batch.cli:main"
    assert scripts["deepseek-batch-tui"] == "deepseek_batch.tui:main"
    assert scripts["deepseek-tree"] == "deepseek_batch.cli_tree:main"

