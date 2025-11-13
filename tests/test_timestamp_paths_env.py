import os
from pathlib import Path

import importlib


def test_resolve_defaults_use_private_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("NLCO_PRIVATE_DIR", str(tmp_path / ".nlco" / "private"))
    monkeypatch.delenv("TIMESTAMP_CONSTRAINTS_PATH", raising=False)
    monkeypatch.delenv("TIMESTAMP_ARTIFACT_PATH", raising=False)
    monkeypatch.delenv("TIMESTAMP_MEMORY_PATH", raising=False)
    monkeypatch.delenv("TIMESTAMP_SHORT_TERM_PATH", raising=False)
    core = importlib.import_module("timestamp_app_core")
    importlib.reload(core)
    assert core.resolve_constraints_path() == Path(os.path.expanduser(str(tmp_path / ".nlco" / "private"))) / "constraints.md"
    assert core.resolve_artifact_path() == Path(os.path.expanduser(str(tmp_path / ".nlco" / "private"))) / "artifact.md"
    assert core.resolve_memory_path() == Path(os.path.expanduser(str(tmp_path / ".nlco" / "private"))) / "memory.md"
    assert core.resolve_short_term_path() == Path(os.path.expanduser(str(tmp_path / ".nlco" / "private"))) / "short_term_memory.md"


def test_resolve_env_overrides(monkeypatch, tmp_path):
    c = tmp_path / "custom_constraints.md"
    a = tmp_path / "custom_artifact.md"
    m = tmp_path / "custom_memory.md"
    s = tmp_path / "custom_short_term.md"
    monkeypatch.setenv("TIMESTAMP_CONSTRAINTS_PATH", str(c))
    monkeypatch.setenv("TIMESTAMP_ARTIFACT_PATH", str(a))
    monkeypatch.setenv("TIMESTAMP_MEMORY_PATH", str(m))
    monkeypatch.setenv("TIMESTAMP_SHORT_TERM_PATH", str(s))
    core = importlib.import_module("timestamp_app_core")
    importlib.reload(core)
    assert core.resolve_constraints_path() == c
    assert core.resolve_artifact_path() == a
    assert core.resolve_memory_path() == m
    assert core.resolve_short_term_path() == s


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
