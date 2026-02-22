"""CLI entry point for actor-tui."""

from __future__ import annotations

import argparse
from typing import Optional

import dspy

from .config import load_config, set_config_path, update_config
from .models import MODEL_PRESETS, build_lm


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Actor-Reviewer TUI")
    parser.add_argument("--config", type=str, help="Config file path")
    parser.add_argument("--model", choices=list(MODEL_PRESETS), help="Model preset")
    parser.add_argument("--max-tokens", type=int, help="Max output tokens")
    parser.add_argument("--memory", type=str, help="Path to memory.md")
    args = parser.parse_args(argv)

    if args.config:
        set_config_path(args.config)
    cfg = load_config()

    model_key = args.model or cfg.model
    dspy.configure(lm=build_lm(model_key, args.max_tokens or cfg.max_tokens))

    if args.memory:
        update_config(memory_path=args.memory)

    from .tui import ActorTUI

    ActorTUI().run()


if __name__ == "__main__":
    main()
