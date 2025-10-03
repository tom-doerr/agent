"""Editing helpers for artifact refinement flows."""

from __future__ import annotations

from typing import Tuple, TypeVar

from pydantic import BaseModel


EditType = TypeVar("EditType", bound=BaseModel)


def apply_edits(artifact: str, edits: list[EditType]) -> Tuple[str, list[EditType]]:
    """Apply structured search/replace edits to the artifact text."""
    error_message = ""
    search_replace_errors: list[EditType] = []
    for edit in edits:
        search_term = getattr(edit, "search", None)
        replacement = getattr(edit, "replace", None)
        if not search_term or search_term not in artifact:
            search_replace_errors.append(edit)
            error_message += f"Search term '{search_term}' not found in artifact.\n"
            print("error:", error_message)
            continue
        artifact = artifact.replace(search_term, replacement)
    return artifact, search_replace_errors
