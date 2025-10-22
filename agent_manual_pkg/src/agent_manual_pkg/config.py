from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

CONFIG_ENV = "AGENT_MANUAL_CONFIG"


@dataclass
class AppConfig:
    model: str = "chat"
    max_tokens: int | None = None
    module_models: dict[str, str] = field(default_factory=dict)


_config_path: Path | None = None
_config: AppConfig | None = None


def _default_path() -> Path:
    base = Path.home() / ".config" / "agent-manual"
    return base / "config.json"


def get_config_path() -> Path:
    global _config_path
    if _config_path is None:
        env = os.environ.get(CONFIG_ENV)
        _config_path = Path(env).expanduser() if env else _default_path()
    return _config_path


def set_config_path(path: str | os.PathLike[str]) -> None:
    global _config_path, _config
    _config_path = Path(path).expanduser()
    _config = None


def load_config() -> AppConfig:
    global _config
    path = get_config_path()
    defaults = asdict(AppConfig())
    data: dict[str, Any] = {}
    if path.exists():
        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            data = {}
    merged = defaults | {k: v for k, v in data.items() if k in defaults}
    _config = AppConfig(**merged)
    if not path.exists() or merged != data:
        save_config(_config)
    return _config


def get_config() -> AppConfig:
    global _config
    if _config is None:
        return load_config()
    return _config


def save_config(config: AppConfig | None = None) -> Path:
    cfg = config or get_config()
    path = get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(cfg), indent=2, sort_keys=True))
    return path


def update_config(*, persist: bool = True, **updates: Any) -> AppConfig:
    cfg = get_config()
    for key, value in updates.items():
        if not hasattr(cfg, key):
            raise AttributeError(f"unknown config option '{key}'")
        if key == "model":
            if not isinstance(value, str):
                raise ValueError("model must be a string")
        if key == "max_tokens":
            if value is not None and (not isinstance(value, int) or value <= 0):
                raise ValueError("max_tokens must be a positive integer")
        if key == "module_models":
            if value is None:
                value = {}
            if not isinstance(value, dict):
                raise ValueError("module_models must be a dict")
            value = {str(k): str(v) for k, v in value.items()}
            setattr(cfg, key, value)
            continue
        setattr(cfg, key, value)
    if persist:
        save_config(cfg)
    return cfg
