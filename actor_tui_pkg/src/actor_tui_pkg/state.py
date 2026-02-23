"""Shared system state passed to all modules."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class SystemState(BaseModel):
    """Central state object for the actor pipeline."""

    user_message: str
    memory: str = ""
    chat_history: str = ""
    assistant_reply: Optional[str] = None
    feedback: str = ""
