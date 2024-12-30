from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone, UTC
from typing import Optional
import jwt
import uuid
from perfi.services.user import UserService
from perfi.core.database import User
from perfi.core.exc import ServiceError
from perfi.core.dependencies.settings import get_settings
from perfi.core.repositories import RefreshTokenRepository


class AuthService:
    def __init__(
        self, user_service: UserService, refresh_token_repo: RefreshTokenRepository
    ) -> None:
        self.user_service = user_service
        self.refresh_token_repo = refresh_token_repo
        application_settings = get_settings()
        self.SECRET_KEY = application_settings.SECRET_KEY
        self.ALGORITHM = application_settings.ALGORITHM
        self.ACCESS_TOKEN_EXPIRE_MINUTES = (
            application_settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        self.REFRESH_TOKEN_EXPIRE_DAYS = application_settings.REFRESH_TOKEN_EXPIRE_DAYS

    async def authenticate(
        self, username_or_email: str, password: str
    ) -> Optional[User]:
        """
        Authenticates a user by verifying their password and returning the user object.
        """
        user = await self.user_service.get_by_username_or_email(username_or_email)

        if not user or not user.verify_password(password):
            raise ServiceError("Invalid username/email or password.")
        return user

    async def register_user(self, username: str, email: str, password: str) -> User:
        """
        Registers a new user with hashed password.
        """
        if not all([username, email, password]):
            raise ServiceError("All fields (username, email, password) are required.")

        return await self.user_service.create_user(username, email, password)

    def create_access_token(
        self, data: dict, expires_delta: timedelta | None = None
    ) -> tuple[str, datetime]:
        """
        Creates a JWT access token and returns it with its expiration time.
        """
        to_encode = data.copy()
        expire = (
            datetime.now(timezone.utc) + expires_delta
            if expires_delta
            else datetime.now(timezone.utc)
            + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token, expire

    def decode_access_token(self, token: str) -> dict:
        """
        Decodes and validates a JWT access token.
        """
        try:
            return jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise ServiceError("Token has expired.")
        except jwt.InvalidTokenError:
            raise ServiceError("Invalid token.")

    def create_refresh_token(self) -> str:
        expires_at = datetime.now(UTC) + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        token = str(uuid.uuid4())
        return token, expires_at

    async def issue_refresh_token(self, user_id: uuid.UUID) -> tuple[str, datetime]:
        """
        Creates a fresh refresh token and returns it with its expiration time.
        """
        token, expires_at = self.create_refresh_token()
        await self.refresh_token_repo.create(user_id, token, expires_at)
        self.revoke_expired_tokens()
        return token, expires_at

    async def validate_refresh_token(self, token: str) -> User:
        refresh_token = await self.refresh_token_repo.get_by_token(token)
        if not refresh_token or refresh_token.expires_at < datetime.now(UTC):
            raise ValueError("Invalid or expired refresh token")
        return refresh_token.user

    async def revoke_refresh_token(self, token: str) -> None:
        await self.refresh_token_repo.delete(token)

    async def revoke_expired_tokens(self) -> None:
        await self.refresh_token_repo.delete_expired()
