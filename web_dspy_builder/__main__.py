"""Entry-point for launching the DSPy visual builder server."""

from __future__ import annotations

import argparse
import os

import uvicorn


DEFAULT_HOST = os.getenv("DSPY_BUILDER_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.getenv("DSPY_BUILDER_PORT", "8800"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the DSPy Visual Builder server")
    parser.add_argument("--host", default=DEFAULT_HOST, help="interface to bind (default: %(default)s)")
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help="port number to bind (default: %(default)s)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="enable auto-reload (development use only)",
    )
    args = parser.parse_args()

    uvicorn.run(
        "web_dspy_builder.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
