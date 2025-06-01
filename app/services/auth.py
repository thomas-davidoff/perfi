from datetime import datetime, timedelta, timezone
from re import A
from uuid import UUID

from typing import Any

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import BaseModel, model_serializer, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, user, RefreshToken
from app.schemas import PerfiSchema
from app.repositories.user import UserRepository
from app.repositories.refresh_token import RefreshTokenRepository
from app.utils.password import verify_password
from config.settings import settings

from app.services import UserService


from app.exc import (
    InvalidTokenException,
    ExpiredTokenException,
    RepositoryException,
    RevokedTokenException,
    InvalidCredentialsException,
)
import json

import logging


logger = logging.getLogger(__name__)


class BearerAccessTokenRefreshTokenPair(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str | None = None
    expires_at: datetime


class TokenData(PerfiSchema):
    sub: UUID
    exp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        + settings.jwt.ACCESS_TOKEN_EXPIRES_IN_MINUTES
    )

    @model_serializer
    def ser_model(self) -> dict[str, str | datetime]:
        return {"sub": str(self.sub), "exp": self.exp}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


class AuthService:
    @staticmethod
    def create_access_token_for_user(user_id: UUID) -> tuple[str, datetime]:
        """
        Create a JWT access token.
        """
        token_data = TokenData(sub=user_id)
        encoded_jwt = jwt.encode(
            token_data.model_dump(),
            settings.jwt.SECRET_KEY,
            algorithm=settings.jwt.ALGO,
        )

        return encoded_jwt, token_data.exp

    @classmethod
    async def authenticate_user(
        cls, session: AsyncSession, email: str, password: str
    ) -> User:
        """
        Authenticate a user with email and password.
        """
        logger.debug(f"Attempting to authenticate user with email {email}")

        user = await UserService.get_user_by_email(session=session, email=email)

        if not user:
            raise InvalidCredentialsException("Invalid email or password")

        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException("Invalid email or password")

        return user

    @classmethod
    async def create_tokens(
        cls, session: AsyncSession, user_id: UUID, device_info: str | None = None
    ) -> BearerAccessTokenRefreshTokenPair:
        """
        Create both access and refresh tokens.
        """
        access_token, expires_at = cls.create_access_token_for_user(user_id=user_id)

        # Create refresh token
        refresh_token = await RefreshTokenRepository.generate_token(
            session=session, user_id=user_id, device_info=device_info
        )

        return BearerAccessTokenRefreshTokenPair(
            access_token=access_token,
            token_type="bearer",
            refresh_token=refresh_token.token_value,
            expires_at=expires_at,
        )

    @classmethod
    async def generate_new_access_token_from_refresh_token(
        cls, session: AsyncSession, refresh_token_value: str
    ) -> BearerAccessTokenRefreshTokenPair:
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
            if token.revoked:
                raise RevokedTokenException("Token has been revoked")

            if token.expires_at < now:
                raise ExpiredTokenException("Token has expired")

            # Update last used time
            await RefreshTokenRepository.mark_as_used(session, token.uuid)

            # Create new access token
            return await cls.create_tokens(session, token.user_id)

        except (RevokedTokenException, ExpiredTokenException) as e:
            # Re-raise specific exceptions
            raise
        except RepositoryException as e:
            # Catch other exceptions and convert to a generic token error
            raise InvalidTokenException(f"Invalid refresh token: {str(e)}")

    @classmethod
    async def logout(cls, session: AsyncSession, refresh_token_value: str) -> None:
        refresh_token = await RefreshTokenRepository.get_by_token_value(
            session, refresh_token_value
        )

        await RefreshTokenRepository.revoke_token(
            session=session, token_id=refresh_token.uuid
        )
