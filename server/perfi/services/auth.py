from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
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

    async def authenticate(
        self, session: AsyncSession, username_or_email: str, password: str
    ) -> Optional[User]:
        """
        Authenticates a user by verifying their password and returning the user object.
        """
        user = await self.user_service.get_by_username_or_email(
            session, username_or_email
        )

        if not user or not user.verify_password(password):
            raise ServiceError("Invalid username/email or password.")
        return user

    async def register_user(
        self, session: AsyncSession, username: str, email: str, password: str
    ) -> User:
        """
        Registers a new user with hashed password.
        """
        if not all([username, email, password]):
            raise ServiceError("All fields (username, email, password) are required.")

        return await self.user_service.create_user(session, username, email, password)

    def create_access_token(
        self, data: dict, expires_delta: timedelta | None = None
    ) -> str:
        """
        Creates a JWT access token.
        """
        to_encode = data.copy()
        expire = (
            datetime.now(timezone.utc) + expires_delta
            if expires_delta
            else datetime.now(timezone.utc)
            + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

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

    def create_refresh_token(self, user_id: uuid.UUID, expires_in: int = 30) -> str:
        expires_at = datetime.now(datetime.timezone.utc) + timedelta(days=expires_in)
        token = str(uuid.uuid4())
        return token, expires_at

    async def issue_refresh_token(self, user_id: uuid.UUID) -> str:
        token, expires_at = self.create_refresh_token(user_id)
        await self.refresh_token_repo.create(user_id, token, expires_at)
        return token

    async def validate_refresh_token(self, token: str) -> User:
        refresh_token = await self.refresh_token_repo.get_by_token(token)
        if not refresh_token or refresh_token.expires_at < datetime.utcnow():
            raise ValueError("Invalid or expired refresh token")
        return refresh_token.user

    async def revoke_refresh_token(self, token: str) -> None:
        await self.refresh_token_repo.delete(token)

    async def revoke_expired_tokens(self) -> None:
        await self.refresh_token_repo.delete_expired()
