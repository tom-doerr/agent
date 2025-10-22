from __future__ import annotations

import argparse
from typing import List, Optional

from .config import load_config, set_config_path
from .runtime import MODEL_PRESETS, configure_model
from .tui import TUI


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Run the agent-manual Textual TUI.")
    parser.add_argument("--config", type=str, help="Path to the agent-manual config file.")
    parser.add_argument("--model", choices=list(MODEL_PRESETS.keys()), help="Set default model before launch.")
    parser.add_argument("--max-tokens", type=int, help="Override max output tokens before launch.")
    args = parser.parse_args(argv)

    if args.config:
        set_config_path(args.config)
    cfg = load_config()

    if args.max_tokens is not None and args.max_tokens <= 0:
        parser.error("--max-tokens must be a positive integer")

    target_model = args.model or cfg.model
    persist = args.model is not None or args.max_tokens is not None
    configure_model(target_model, max_tokens=args.max_tokens, persist=persist)

    TUI(concurrency=1).run()


if __name__ == "__main__":
    main()

