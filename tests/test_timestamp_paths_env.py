import os
from pathlib import Path

import importlib


def test_resolve_defaults_use_private_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("NLCO_PRIVATE_DIR", str(tmp_path / ".nlco" / "private"))
    monkeypatch.delenv("TIMESTAMP_CONSTRAINTS_PATH", raising=False)
    monkeypatch.delenv("TIMESTAMP_ARTIFACT_PATH", raising=False)
    core = importlib.import_module("timestamp_app_core")
    importlib.reload(core)
    assert core.resolve_constraints_path() == Path(os.path.expanduser(str(tmp_path / ".nlco" / "private"))) / "constraints.md"
    assert core.resolve_artifact_path() == Path(os.path.expanduser(str(tmp_path / ".nlco" / "private"))) / "artifact.md"


def test_resolve_env_overrides(monkeypatch, tmp_path):
    c = tmp_path / "custom_constraints.md"
    a = tmp_path / "custom_artifact.md"
    monkeypatch.setenv("TIMESTAMP_CONSTRAINTS_PATH", str(c))
    monkeypatch.setenv("TIMESTAMP_ARTIFACT_PATH", str(a))
    core = importlib.import_module("timestamp_app_core")
    importlib.reload(core)
    assert core.resolve_constraints_path() == c
    assert core.resolve_artifact_path() == a


def test_core_app_uses_resolved_paths(monkeypatch, tmp_path):
    c = tmp_path / "C.md"
    a = tmp_path / "A.md"
    monkeypatch.setenv("TIMESTAMP_CONSTRAINTS_PATH", str(c))
    monkeypatch.setenv("TIMESTAMP_ARTIFACT_PATH", str(a))
    core = importlib.import_module("timestamp_app_core")
    importlib.reload(core)
    app = core.TimestampLogApp()
    assert app._constraints_path == c
    assert app._artifact_path == a

