"""Web DSPy Builder package with lazy server import."""

from __future__ import annotations

from typing import Any


def create_app(*args: Any, **kwargs: Any):
    """Import the FastAPI server lazily to avoid hard dependencies."""

    from .server import create_app as _create_app

    return _create_app(*args, **kwargs)


__all__ = ["create_app"]

