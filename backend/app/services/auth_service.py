from typing import Optional
from uuid import UUID
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models.user import User
from shared.schemas.user import UserResponse, TokenResponse
from shared.core.logging_config import get_logger
from app.repositories.user_repository import UserRepository, get_user_repository
from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)

logger = get_logger(__name__)


class AuthService:
    """Service layer for authentication business logic."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register(
        self,
        db: AsyncSession,
        email: str,
        password: str
    ) -> tuple[UserResponse, TokenResponse]:
        """Register a new user and return tokens."""
        # Check if email already exists
        if await self.user_repository.email_exists(db, email):
            raise ValueError("Email already registered")

        # Create user with hashed password
        hashed = hash_password(password)
        user = await self.user_repository.create_user(db, email, hashed)

        # Generate tokens
        tokens = self._create_tokens(str(user.id))
        user_response = UserResponse.model_validate(user)

        logger.info(f"User registered: {email}")
        return user_response, tokens

    async def login(
        self,
        db: AsyncSession,
        email: str,
        password: str
    ) -> tuple[UserResponse, TokenResponse]:
        """Authenticate user and return tokens."""
        user = await self.user_repository.get_by_email(db, email)

        if not user:
            raise ValueError("Invalid email or password")

        if not verify_password(password, user.hashed_password):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("User account is disabled")

        # Generate tokens
        tokens = self._create_tokens(str(user.id))
        user_response = UserResponse.model_validate(user)

        logger.info(f"User logged in: {email}")
        return user_response, tokens

    async def refresh_access_token(
        self,
        db: AsyncSession,
        refresh_token: str
    ) -> TokenResponse:
        """Validate refresh token and return new access token."""
        payload = decode_token(refresh_token)

        if not payload:
            raise ValueError("Invalid refresh token")

        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")

        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid token payload")

        # Verify user still exists and is active
        user = await self.user_repository.get_by_id(db, UUID(user_id))
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")

        # Generate new tokens
        return self._create_tokens(user_id)

    async def get_current_user(
        self,
        db: AsyncSession,
        token: str
    ) -> Optional[User]:
        """Get current user from access token."""
        payload = decode_token(token)

        if not payload:
            return None

        if payload.get("type") != "access":
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        user = await self.user_repository.get_by_id(db, UUID(user_id))
        if user and user.is_active:
            return user

        return None

    def _create_tokens(self, user_id: str) -> TokenResponse:
        """Create access and refresh tokens for a user."""
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )


async def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository)
) -> AuthService:
    """Dependency injection for AuthService."""
    return AuthService(user_repository=user_repository)
