"""Authentication utilities for the HTMX FastAPI app using FastAPI Users."""

from __future__ import annotations

import logging
import os
from collections.abc import AsyncGenerator, Callable
from typing import Optional, TYPE_CHECKING, Tuple

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, status
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin, models
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    JWTStrategy,
)
from fastapi_users.authentication.strategy import Strategy
from fastapi_users.models import UP
from httpx_oauth.clients.github import GitHubOAuth2
from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users.router.auth import ErrorCode, OpenAPIResponseType
from fastapi_users.router.common import ErrorModel
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import Integer, select
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

    async def _resolve_username(self, user_manager: BaseUserManager[models.UP, models.ID], username: str) -> str:
        cleaned = username.strip().lower()
        if "@" in cleaned:
            return cleaned
        candidate = cleaned
        if self.config.default_user_email and "@" in self.config.default_user_email:
            suffix = self.config.default_user_email.split("@", 1)[1]
            candidate = f"{cleaned}@{suffix}"
            existing = await user_manager.user_db.get_by_email(candidate)
            if existing:
                return candidate
        session = user_manager.user_db.session
        stmt = select(User.email).where(User.email.ilike(f"{cleaned}@%"))
        result = await session.execute(stmt)
        email = result.scalar_one_or_none()
        if email:
            return email
        return cleaned

    async def _normalize_username(
        self,
        user_manager: BaseUserManager[models.UP, models.ID],
        username: str,
    ) -> str:
        """Compat helper for legacy call sites expecting _normalize_username."""

        return await self._resolve_username(user_manager, username)

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
        await self._ensure_default_user()

    async def shutdown(self) -> None:
        await self.engine.dispose()

    async def _ensure_default_user(self) -> None:
        email = (self.config.default_user_email or "").strip().lower()
        password = self.config.default_user_password
        if not email or not password:
            return
        async with self.async_session_maker() as session:
            user_db = SQLAlchemyUserDatabase(session, User)
            existing = await user_db.get_by_email(email)
            if existing:
                return
            user_manager = UserManager(user_db, self.config.auth_jwt_secret)
            await user_manager.create(
                UserCreate(email=email, password=password),
                safe=True,
            )

    def _build_auth_router(self) -> APIRouter:
        router = APIRouter()
        backend = self.auth_backend
        authenticator = self.fastapi_users.authenticator
        get_current_user_token = authenticator.current_user_token(active=True, verified=False)

        login_responses: OpenAPIResponseType = {
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.LOGIN_BAD_CREDENTIALS: {
                                "summary": "Bad credentials or the user is inactive.",
                                "value": {"detail": ErrorCode.LOGIN_BAD_CREDENTIALS},
                            },
                            ErrorCode.LOGIN_USER_NOT_VERIFIED: {
                                "summary": "The user is not verified.",
                                "value": {"detail": ErrorCode.LOGIN_USER_NOT_VERIFIED},
                            },
                        }
                    }
                },
            },
            **backend.transport.get_openapi_login_responses_success(),
        }

        @router.post(
            "/login",
            name=f"auth:{backend.name}.login",
            responses=login_responses,
        )
        async def login(
            request: Request,
            credentials: OAuth2PasswordRequestForm = Depends(),
            user_manager: BaseUserManager[models.UP, models.ID] = Depends(self.user_manager_dependency),
            strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
        ):
            credentials.username = await self._resolve_username(user_manager, credentials.username)
            user = await user_manager.authenticate(credentials)

            if user is None or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
                )
            response = await backend.login(strategy, user)
            await user_manager.on_after_login(user, request, response)
            return response

        logout_responses: OpenAPIResponseType = {
            **{status.HTTP_401_UNAUTHORIZED: {"description": "Missing token or inactive user."}},
            **backend.transport.get_openapi_logout_responses_success(),
        }

        @router.post(
            "/logout",
            name=f"auth:{backend.name}.logout",
            responses=logout_responses,
        )
        async def logout(
            user_token=Depends(get_current_user_token),
            strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
        ):
            user, token = user_token
            return await backend.logout(strategy, user, token)

        return router

    def include_routers(self, app: FastAPI) -> None:
        app.include_router(
            self._build_auth_router(),
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
