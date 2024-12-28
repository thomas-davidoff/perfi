from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from perfi.services.auth import AuthService
from perfi.services.user import UserService
from perfi.core.database import User
from typing import Annotated
from .session import get_async_session
from .service_factories import get_auth_service, get_user_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """
    Dependency to retrieve the current authenticated user from the JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = auth_service.decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    user = await user_service.get_by_id(session, user_id)
    if user is None:
        raise credentials_exception

    return user
