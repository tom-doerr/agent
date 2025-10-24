import tomllib


def test_scripts_declared_in_pyproject():
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    scripts = data["project"]["scripts"]
    assert scripts["deepseek-batch"] == "deepseek_batch.cli:main"
    assert scripts["deepseek-batch-tui"] == "deepseek_batch.tui:main"
    assert scripts["deepseek-tree"] == "deepseek_batch.cli_tree:main"
