"""Command line entry point for the DSPy Textual application."""

from __future__ import annotations

from .app import DSpyProgramApp


def main() -> None:
    """Launch the Textual DSPy program app."""

    app = DSpyProgramApp()
    app.run()


if __name__ == "__main__":  # pragma: no cover - manual launch helper
    main()
