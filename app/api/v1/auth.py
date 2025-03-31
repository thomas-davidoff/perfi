from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from db.session_manager import get_session
from app.dependencies.auth import get_current_active_user
from app.models import User
from app.schemas import UserCreateSchema, UserSchema
from app.repositories.user import UserRepository
from app.services.auth import AuthService, BearerAccessTokenRefreshTokenPair

from app.exc import (
    InvalidCredentialsException,
    InvalidTokenException,
    ExpiredTokenException,
    RevokedTokenException,
    UserExistsException,
)
from app.api.v1.schema import ApiResponse

router = APIRouter(prefix="/auth", tags=["auth"])


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post(
    "/register",
    response_model=ApiResponse[UserSchema],
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user_data: UserCreateSchema, session: AsyncSession = Depends(get_session)
):
    """
    Register a new user and return access token.
    """
    # Check if email already exists
    existing_user = await UserRepository.get_by_email(session, user_data.email)
    if existing_user:
        raise UserExistsException("Email already registered")

    # Create user
    user = await UserRepository.create(session, user_data)
    return ApiResponse(data=user)


@router.post("/token", response_model=BearerAccessTokenRefreshTokenPair)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session),
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    try:
        user = await AuthService.authenticate_user(
            session, form_data.username, form_data.password
        )
        tokens = await AuthService.create_tokens(session, user.uuid)
        return tokens
    except InvalidCredentialsException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/refresh", response_model=BearerAccessTokenRefreshTokenPair)
async def refresh_token(
    refresh_data: RefreshTokenRequest, session: AsyncSession = Depends(get_session)
):
    """
    Get a new access token using refresh token.
    """
    try:
        tokens = await AuthService.generate_new_access_token_from_refresh_token(
            session, refresh_data.refresh_token
        )
        return tokens
    except (InvalidTokenException, ExpiredTokenException, RevokedTokenException) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/whoami", response_model=UserSchema)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Get current user.
    """
    return current_user
