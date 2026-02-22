"""Configuration management with JSON persistence."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

_config_path: Optional[Path] = None


def get_config_path() -> Path:
    import os
    env = os.environ.get("ACTOR_TUI_CONFIG")
    if env:
        return Path(env).expanduser()
    if _config_path:
        return _config_path
    return Path.home() / ".config" / "actor-tui" / "config.json"


def set_config_path(path: str) -> None:
    global _config_path
    _config_path = Path(path).expanduser()


@dataclass
class AppConfig:
    model: str = "spark2"
    max_tokens: Optional[int] = None
    max_review_iters: int = 3
    memory_path: str = str(Path.home() / ".config" / "actor-tui" / "memory.md")
    interaction_dataset_path: str = str(
        Path.home() / ".config" / "actor-tui" / "interaction_reviews.jsonl"
    )
    memory_dataset_path: str = str(
        Path.home() / ".config" / "actor-tui" / "memory_reviews.jsonl"
    )
    tool_dataset_path: str = str(
        Path.home() / ".config" / "actor-tui" / "tool_reviews.jsonl"
    )


_config: Optional[AppConfig] = None


def load_config() -> AppConfig:
    global _config
    path = get_config_path()
    if path.exists():
        data = json.loads(path.read_text())
        _config = AppConfig(**{
            k: v for k, v in data.items() if k in AppConfig.__dataclass_fields__
        })
    else:
        _config = AppConfig()
        save_config(_config)
    return _config


def get_config() -> AppConfig:
    if _config is None:
        return load_config()
    return _config


def save_config(config: AppConfig) -> None:
    path = get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(config), indent=2))


def update_config(**updates: object) -> AppConfig:
    cfg = get_config()
    for k, v in updates.items():
        if hasattr(cfg, k):
            setattr(cfg, k, v)
    save_config(cfg)
    return cfg
