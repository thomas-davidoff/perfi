from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from passlib.context import CryptContext
from perfi.services.user import UserService
from perfi.core.database import User
from perfi.core.exc import ServiceError
from perfi.core.dependencies.settings import get_settings

# JWT Configuration
application_settings = get_settings()
SECRET_KEY = application_settings.SECRET_KEY
ALGORITHM = application_settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = application_settings.ACCESS_TOKEN_EXPIRE_MINUTES


class AuthService:
    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

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
            + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def decode_access_token(self, token: str) -> dict:
        """
        Decodes and validates a JWT access token.
        """
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise ServiceError("Token has expired.")
        except jwt.InvalidTokenError:
            raise ServiceError("Invalid token.")
