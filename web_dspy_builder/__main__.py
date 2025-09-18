"""Entry-point for launching the DSPy visual builder server."""

from __future__ import annotations

import uvicorn


def main() -> None:
    uvicorn.run("web_dspy_builder.server:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()

