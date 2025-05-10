from typing import Annotated
from uuid import UUID

from fastapi import Depends
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from db.session_manager import get_session
from app.models import User
from app.repositories.user import UserRepository
from app.services.auth import oauth2_scheme, TokenData
from config.settings import settings

from app.exc import InvalidTokenException, InactiveUserException


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_session),
) -> User:
    """
    Decode JWT token and return current user.
    """
    # Decode and validate JWT token
    try:
        payload = jwt.decode(
            token, settings.jwt.SECRET_KEY, algorithms=[settings.jwt.ALGO]
        )
    except jwt.PyJWTError:
        raise InvalidTokenException("Invalid token.")

    # Extract user ID from token payload
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise InvalidTokenException("Token missing subject claim")

    # Parse user ID to UUID
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise InvalidTokenException("Invalid user ID format")

    # Fetch user from database
    try:
        user = await UserRepository.get_one_by_id(session, user_id)
    except Exception as e:
        raise InvalidTokenException("Failed to fetch user") from e

    # Verify user exists
    if user is None:
        raise InvalidTokenException("User not found")

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Check if the current user is active.
    """
    if not current_user.is_active:
        raise InactiveUserException("Inactive user")
    return current_user
