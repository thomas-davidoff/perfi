# app/dependencies/auth.py
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from db.session_manager import get_session
from app.models import User
from app.repositories.user import UserRepository
from app.services.auth import oauth2_scheme, TokenPayload
from config.settings import settings


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_session),
) -> User:
    """
    Decode JWT token and return current user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # try:
    # Decode the JWT
    payload = jwt.decode(token, settings.jwt.SECRET_KEY, algorithms=[settings.jwt.ALGO])

    # Extract user ID
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    token_data = TokenPayload(sub=user_id, exp=payload.get("exp"))
    # except Exception:
    #     raise credentials_exception

    # Get the user
    user = await UserRepository.get_one_by_id(session, UUID(user_id))
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Check if the current user is active.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user
