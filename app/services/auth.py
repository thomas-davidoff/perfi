from datetime import datetime, timedelta, timezone
from uuid import UUID

from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repositories.user import UserRepository
from app.repositories.refresh_token import RefreshTokenRepository
from app.utils.password import verify_password
from config.settings import settings


import logging


logger = logging.getLogger(__name__)


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str | None = None
    expires_at: datetime


class TokenPayload(BaseModel):
    sub: str
    exp: datetime


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


class AuthService:
    @staticmethod
    def create_access_token(
        data: dict[str, Any], expires_delta: timedelta | None = None
    ) -> tuple[str, datetime]:
        """
        Create a JWT access token.
        """
        to_encode = data.copy()

        # Set expiration
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)

        to_encode.update({"exp": expire})

        # Create the JWT
        encoded_jwt = jwt.encode(
            to_encode, settings.jwt.SECRET_KEY, algorithm=settings.jwt.ALGO
        )

        return encoded_jwt, expire

    @classmethod
    async def authenticate_user(
        cls, session: AsyncSession, email: str, password: str
    ) -> User | None:
        """
        Authenticate a user with email and password.
        """

        logger.debug(
            f"Attempting to authenticate user with username OR email {email} and password {password}"
        )

        # try email
        user = await UserRepository.get_one_by_id(
            session, id_=email, column="email", with_for_update=False
        )

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    @classmethod
    async def create_tokens(
        cls, session: AsyncSession, user_id: UUID, device_info: str | None = None
    ) -> Token:
        """
        Create both access and refresh tokens.
        """
        # Create access token
        token_data = {"sub": str(user_id)}
        access_token, expires_at = cls.create_access_token(
            data=token_data,
            expires_delta=settings.jwt.ACCESS_TOKEN_EXPIRES_IN_MINUTES,
        )

        # Create refresh token
        refresh_token = await RefreshTokenRepository.generate_token(
            session, user_id, device_info
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            refresh_token=refresh_token.token_value,
            expires_at=expires_at,
        )

    @classmethod
    async def refresh_tokens(
        cls, session: AsyncSession, refresh_token_value: str
    ) -> Token:
        """
        Use a refresh token to create a new access token.
        """
        try:
            # Get the refresh token
            token = await RefreshTokenRepository.get_by_token_value(
                session, refresh_token_value
            )

            # Verify token is valid
            now = datetime.now(timezone.utc)
            if token.revoked or token.expires_at < now:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Update last used time
            await RefreshTokenRepository.mark_as_used(session, token.uuid)

            # Create new access token
            return await cls.create_tokens(session, token.user_id)

        except Exception:
            # TODO: Don't catch every exception...
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
