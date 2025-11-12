"""FastAPI application serving an HTMX-based frontend."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import os

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from . import utils
from .auth import AuthContext, UserRead
from refiner_signature import ScheduleBlock


class TextSnapshot(BaseModel):
    """Represents the current contents and recency of a text file."""

    text: str
    last_updated: datetime | None = Field(description="Filesystem modification time in ISO format")
    age_label: str = Field(description="Human-readable recency label, e.g., '2m 14s ago'")


class HistoryEntry(BaseModel):
    """A dated group of constraint entries."""

    date: str
    entries: list[str]


class ScheduleSnapshot(BaseModel):
    blocks: list[ScheduleBlock]
    last_updated: datetime | None = Field(description="Filesystem modification time in ISO format", default=None)
    age_label: str = Field(description="Human-readable recency label, e.g., '2m 14s ago'")
    error: str | None = Field(default=None, description="Optional parsing error message.")


class StatusResponse(BaseModel):
    """Aggregated view of information NLCO clients need."""

    artifact: TextSnapshot
    memory: TextSnapshot
    short_term_memory: TextSnapshot | None
    history: list[HistoryEntry]
    schedule: ScheduleSnapshot


class MessageRequest(BaseModel):
    message: str



class WebConfig(BaseModel):
    """Runtime configuration for the web frontend."""

    artifact_path: Path = Field(default=Path("artifact.md"))
    memory_path: Path = Field(default=Path("memory.md"))
    constraints_path: Path = Field(default=Path("constraints.md"))
    short_term_memory_path: Path | None = Field(default=Path("short_term_memory.md"))
    schedule_path: Path = Field(default=Path("structured_schedule.json"))
    history_limit: int = Field(default=200, ge=1, le=2000)
    auth_database_url: str = Field(
        default_factory=lambda: os.getenv("NLCO_AUTH_DB_URI", "sqlite+aiosqlite:///./nlco_auth.db")
    )
    auth_jwt_secret: str = Field(
        default_factory=lambda: os.getenv("NLCO_AUTH_SECRET", "CHANGE_ME")
    )
    auth_jwt_lifetime_seconds: int = Field(default=60 * 60 * 6)
    auth_cookie_name: str = Field(default="nlco_auth")
    auth_cookie_secure: bool = Field(
        default_factory=lambda: os.getenv("NLCO_AUTH_COOKIE_SECURE", "false").lower() == "true"
    )
    auth_cookie_max_age: int = Field(
        default_factory=lambda: int(os.getenv("NLCO_AUTH_COOKIE_MAX_AGE", str(60 * 60 * 24 * 7)))
    )
    github_client_id: str | None = Field(default_factory=lambda: os.getenv("NLCO_GITHUB_CLIENT_ID"))
    github_client_secret: str | None = Field(default_factory=lambda: os.getenv("NLCO_GITHUB_CLIENT_SECRET"))
    github_redirect_url: str | None = Field(default_factory=lambda: os.getenv("NLCO_GITHUB_REDIRECT_URL"))
    github_state_secret: str | None = Field(default_factory=lambda: os.getenv("NLCO_GITHUB_STATE_SECRET"))
    default_user_email: str | None = Field(default_factory=lambda: os.getenv("NLCO_DEFAULT_USER_EMAIL"))
    default_user_password: str | None = Field(default_factory=lambda: os.getenv("NLCO_DEFAULT_USER_PASSWORD"))

    class Config:
        arbitrary_types_allowed = True


def create_app(config: WebConfig | None = None) -> FastAPI:
    config = config or WebConfig()
    app = FastAPI(title="NLCO Web Frontend", version="0.1.0")
    auth_context = AuthContext(config)
    app.state.auth_context = auth_context

    templates_dir = Path(__file__).parent / "templates"
    static_dir = Path(__file__).parent / "static"
    templates = Jinja2Templates(directory=str(templates_dir))

    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    auth_context.include_routers(app)
    app.add_event_handler("startup", auth_context.startup)
    app.add_event_handler("shutdown", auth_context.shutdown)

    constraint_lock = None

    try:
        import anyio

        constraint_lock = anyio.Lock()
    except Exception:  # pragma: no cover - fallback if anyio unavailable
        import asyncio

        constraint_lock = asyncio.Lock()

    async def render_template(
        name: str,
        request: Request,
        context: dict[str, Any] | None = None,
        user: UserRead | None = None,
    ) -> HTMLResponse:
        data = {"config": config, "user": user, "login_url": auth_context.login_url()}
        if context:
            data.update(context)
        return templates.TemplateResponse(request, name, data)

    async def load_history() -> list[tuple[str, list[str]]]:
        return await run_in_threadpool(utils.load_constraints_history, config.constraints_path, config.history_limit)

    async def load_artifact() -> tuple[str, str]:
        text, mtime = await run_in_threadpool(utils.load_text_and_mtime, config.artifact_path)
        formatted = utils.format_timedelta(datetime.now(), mtime)
        return text, formatted

    async def load_memory(path: Path) -> tuple[str, str]:
        text, mtime = await run_in_threadpool(utils.load_text_and_mtime, path)
        formatted = utils.format_timedelta(datetime.now(), mtime)
        return text, formatted

    async def build_snapshot(path: Path) -> TextSnapshot:
        text, mtime = await run_in_threadpool(utils.load_text_and_mtime, path)
        return TextSnapshot(
            text=text,
            last_updated=mtime,
            age_label=utils.format_timedelta(datetime.now(), mtime),
        )

    async def build_optional_snapshot(path: Path | None) -> TextSnapshot | None:
        if path is None:
            return None
        return await build_snapshot(path)

    async def build_history(limit: int | None = None) -> list[HistoryEntry]:
        history = await load_history() if limit is None else await run_in_threadpool(
            utils.load_constraints_history,
            config.constraints_path,
            limit,
        )
        return [HistoryEntry(date=date_str, entries=entries) for date_str, entries in history]

    async def build_schedule_snapshot() -> ScheduleSnapshot:
        blocks, mtime, error = await run_in_threadpool(utils.load_schedule_snapshot, config.schedule_path)
        return ScheduleSnapshot(
            blocks=blocks,
            last_updated=mtime,
            age_label=utils.format_timedelta(datetime.now(), mtime),
            error=error,
        )

    @app.get("/", response_class=HTMLResponse)
    async def get_index(
        request: Request,
        user: UserRead | None = Depends(auth_context.current_user_optional),
    ) -> HTMLResponse:
        if user is None:
            return await render_template("login.html", request, {}, user=None)
        artifact_text, artifact_age = await load_artifact()
        memory_text, memory_age = await load_memory(config.memory_path)
        short_term_text = ""
        short_term_age = "never"
        if config.short_term_memory_path is not None:
            short_term_text, short_term_age = await load_memory(config.short_term_memory_path)
        history = await load_history()
        schedule_snapshot = await build_schedule_snapshot()
        return await render_template(
            "index.html",
            request,
            {
                "artifact_text": artifact_text,
                "artifact_age": artifact_age,
                "memory_text": memory_text,
                "memory_age": memory_age,
                "short_term_text": short_term_text,
                "short_term_age": short_term_age,
                "history": history,
                "schedule": schedule_snapshot,
            },
            user=user,
        )

    @app.get("/partials/artifact", response_class=HTMLResponse)
    async def get_artifact_partial(
        request: Request,
        user: UserRead = Depends(auth_context.current_user),
    ) -> HTMLResponse:
        artifact_text, artifact_age = await load_artifact()
        return await render_template(
            "partials/artifact.html",
            request,
            {
                "artifact_text": artifact_text,
                "artifact_age": artifact_age,
            },
            user=user,
        )

    @app.get("/partials/schedule", response_class=HTMLResponse)
    async def get_schedule_partial(
        request: Request,
        user: UserRead = Depends(auth_context.current_user),
    ) -> HTMLResponse:
        schedule_snapshot = await build_schedule_snapshot()
        return await render_template(
            "partials/schedule.html",
            request,
            {
                "schedule": schedule_snapshot,
            },
            user=user,
        )

    @app.get("/partials/memory", response_class=HTMLResponse)
    async def get_memory_partial(
        request: Request,
        user: UserRead = Depends(auth_context.current_user),
    ) -> HTMLResponse:
        memory_text, memory_age = await load_memory(config.memory_path)
        short_term_text = ""
        short_term_age = "never"
        if config.short_term_memory_path is not None:
            short_term_text, short_term_age = await load_memory(config.short_term_memory_path)
        return await render_template(
            "partials/memory.html",
            request,
            {
                "memory_text": memory_text,
                "memory_age": memory_age,
                "short_term_text": short_term_text,
                "short_term_age": short_term_age,
            },
            user=user,
        )

    @app.get("/partials/history", response_class=HTMLResponse)
    async def get_history_partial(
        request: Request,
        user: UserRead = Depends(auth_context.current_user),
    ) -> HTMLResponse:
        history = await load_history()
        return await render_template(
            "partials/history.html",
            request,
            {
                "history": history,
            },
            user=user,
        )

    @app.post("/messages", response_class=HTMLResponse)
    async def post_message(
        request: Request,
        message: str = Form(...),
        user: UserRead = Depends(auth_context.current_user),
    ) -> HTMLResponse:
        message = message.strip()
        if not message:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="message required")
        now = datetime.now()
        async with constraint_lock:
            await run_in_threadpool(utils.write_constraints_entry, config.constraints_path, message, now=now)
        history = await load_history()
        return await render_template(
            "partials/history.html",
            request,
            {
                "history": history,
            },
            user=user,
        )

    @app.get("/api/v1/status", response_model=StatusResponse)
    async def get_status(
        user: UserRead = Depends(auth_context.current_user),
    ) -> StatusResponse:
        artifact_snapshot = await build_snapshot(config.artifact_path)
        memory_snapshot = await build_snapshot(config.memory_path)
        short_term_snapshot = await build_optional_snapshot(config.short_term_memory_path)
        history_entries = await build_history()
        schedule_snapshot = await build_schedule_snapshot()
        return StatusResponse(
            artifact=artifact_snapshot,
            memory=memory_snapshot,
            short_term_memory=short_term_snapshot,
            history=history_entries,
            schedule=schedule_snapshot,
        )

    @app.post("/api/v1/messages", response_model=StatusResponse)
    async def post_message_json(
        payload: MessageRequest,
        user: UserRead = Depends(auth_context.current_user),
    ) -> StatusResponse:
        message = payload.message.strip()
        if not message:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="message required")
        now = datetime.now()
        async with constraint_lock:
            await run_in_threadpool(utils.write_constraints_entry, config.constraints_path, message, now=now)
        artifact_snapshot = await build_snapshot(config.artifact_path)
        memory_snapshot = await build_snapshot(config.memory_path)
        short_term_snapshot = await build_optional_snapshot(config.short_term_memory_path)
        history_entries = await build_history()
        schedule_snapshot = await build_schedule_snapshot()
        return StatusResponse(
            artifact=artifact_snapshot,
            memory=memory_snapshot,
            short_term_memory=short_term_snapshot,
            history=history_entries,
            schedule=schedule_snapshot,
        )

    return app


app = create_app()
