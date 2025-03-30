# app/routes/auth.py
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from db.session_manager import get_session
from app.dependencies.auth import get_current_user, get_current_active_user
from app.models import User, UserCreateSchema, UserSchema
from app.repositories.user import UserRepository
from app.services.auth import AuthService, Token


router = APIRouter(prefix="/auth", tags=["auth"])


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/register", response_model=Token)
async def register_user(
    user_data: UserCreateSchema, session: AsyncSession = Depends(get_session)
):
    """
    Register a new user and return access token.
    """
    # Check if email already exists
    existing_user = await UserRepository.get_by_email(session, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )

    # Create user
    user = await UserRepository.create(session, user_data)

    # Create tokens
    tokens = await AuthService.create_tokens(session, user.uuid)
    return tokens


@router.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session),
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    print(form_data)
    print(form_data.username)
    print(form_data.password)
    user = await AuthService.authenticate_user(
        session, form_data.username, form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    tokens = await AuthService.create_tokens(session, user.uuid)
    return tokens


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest, session: AsyncSession = Depends(get_session)
):
    """
    Get a new access token using refresh token.
    """
    tokens = await AuthService.refresh_tokens(session, refresh_data.refresh_token)
    return tokens


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    refresh_data: RefreshTokenRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
):
    """
    Logout by revoking the refresh token.
    """
    await AuthService.revoke_token(session, refresh_data.refresh_token)
    return None


@router.get("/me", response_model=UserSchema)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Get current user.
    """
    return current_user
