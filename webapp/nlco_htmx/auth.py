"""Authentication utilities for the HTMX FastAPI app using FastAPI Users."""

from __future__ import annotations

import logging
import os
from collections.abc import AsyncGenerator, Callable
from typing import Optional, TYPE_CHECKING

from fastapi import Depends, FastAPI
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    JWTStrategy,
)
from fastapi_users.models import UP
from httpx_oauth.clients.github import GitHubOAuth2
from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeMeta, declarative_base, mapped_column, Mapped
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from .app import WebConfig

logger = logging.getLogger(__name__)

Base: DeclarativeMeta = declarative_base()


class User(SQLAlchemyBaseUserTable[int], Base):
    """Database table for application users."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


class UserRead(BaseUser[int]):
    pass


class UserCreate(BaseUserCreate):
    pass


class UserUpdate(BaseUserUpdate):
    pass


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """Custom user manager to configure token secrets."""

    def __init__(self, user_db: SQLAlchemyUserDatabase[User, int], secret: str) -> None:
        super().__init__(user_db)
        self._secret = secret

    @property
    def reset_password_token_secret(self) -> str:
        return self._secret

    @property
    def verification_token_secret(self) -> str:
        return self._secret


class AuthContext:
    """Encapsulates FastAPI Users setup for a particular application config."""

    def __init__(self, config: "WebConfig") -> None:
        self.config = config
        self.engine = create_async_engine(
            config.auth_database_url,
            echo=False,
            future=True,
        )
        self.async_session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            self.engine, expire_on_commit=False
        )
        self.user_db_dependency = self._make_user_db_dependency()
        self.user_manager_dependency = self._make_user_manager_dependency()
        self.cookie_transport = CookieTransport(
            cookie_name=config.auth_cookie_name,
            cookie_max_age=config.auth_cookie_max_age,
            cookie_secure=config.auth_cookie_secure,
            cookie_samesite="lax",
        )
        self.auth_backend = AuthenticationBackend(
            name="jwt",
            transport=self.cookie_transport,
            get_strategy=self._get_jwt_strategy,
        )
        self.fastapi_users: FastAPIUsers[User, int] = FastAPIUsers(
            self.user_manager_dependency,
            [self.auth_backend],
        )
        self.current_user = self.fastapi_users.current_user(active=True)
        self.current_user_optional = self.fastapi_users.current_user(optional=True)
        self.github_redirect_url: str | None = None
        self.github_provider = self._build_github_provider()

    def _make_user_db_dependency(self) -> Callable[[], AsyncGenerator[SQLAlchemyUserDatabase[User, int], None]]:
        async def get_user_db() -> AsyncGenerator[SQLAlchemyUserDatabase[User, int], None]:
            async with self.async_session_maker() as session:
                yield SQLAlchemyUserDatabase(session, User)

        return get_user_db

    def _make_user_manager_dependency(self) -> Callable[[SQLAlchemyUserDatabase[User, int]], AsyncGenerator[UserManager, None]]:
        secret = self.config.auth_jwt_secret

        async def get_user_manager(
            user_db: SQLAlchemyUserDatabase[User, int] = Depends(self.user_db_dependency),
        ) -> AsyncGenerator[UserManager, None]:
            yield UserManager(user_db, secret)

        return get_user_manager

    def _get_jwt_strategy(self) -> JWTStrategy:
        return JWTStrategy(secret=self.config.auth_jwt_secret, lifetime_seconds=self.config.auth_jwt_lifetime_seconds)

    def _build_github_provider(self) -> Optional[GitHubOAuth2]:
        client_id = self.config.github_client_id
        client_secret = self.config.github_client_secret
        redirect_url = self.config.github_redirect_url
        if not client_id or not client_secret:
            logger.info("GitHub OAuth not configured; skipping provider setup")
            return None
        if not redirect_url:
            redirect_url = os.getenv("NLCO_GITHUB_REDIRECT_URL", "http://localhost:8000/auth/github/callback")
        self.github_redirect_url = redirect_url
        return GitHubOAuth2(
            client_id=client_id,
            client_secret=client_secret,
        )

    async def startup(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def shutdown(self) -> None:
        await self.engine.dispose()

    def include_routers(self, app: FastAPI) -> None:
        app.include_router(
            self.fastapi_users.get_auth_router(self.auth_backend),
            prefix="/auth/jwt",
            tags=["auth"],
        )
        app.include_router(
            self.fastapi_users.get_register_router(UserRead, UserCreate),
            prefix="/auth",
            tags=["auth"],
        )
        app.include_router(
            self.fastapi_users.get_users_router(UserRead, UserUpdate),
            prefix="/users",
            tags=["users"],
        )
        if self.github_provider:
            state_secret = self.config.github_state_secret or self.config.auth_jwt_secret
            app.include_router(
                self.fastapi_users.get_oauth_router(
                    self.github_provider,
                    self.auth_backend,
                    state_secret,
                    redirect_url=self.github_redirect_url,
                    associate_by_email=True,
                ),
                prefix="/auth/github",
                tags=["auth"],
            )
            # Associate router can be added later if multi-account linking is required.

    def login_url(self) -> Optional[str]:
        if self.github_provider:
            return "/auth/github/login"
        return None


__all__ = [
    "AuthContext",
    "User",
    "UserCreate",
    "UserRead",
    "UserUpdate",
]
