from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from perfi.services.auth import AuthService
from perfi.core.dependencies.session import get_async_session
from perfi.core.dependencies.service_factories import get_auth_service
from perfi.core.exc import ServiceError
from perfi.schemas.auth import TokenResponse
from perfi.schemas.user import UserResponse, UserCreate
from perfi.core.dependencies.settings import get_settings
from config import Settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/token", response_model=TokenResponse)
async def login_for_access_and_refresh_tokens(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
    session: AsyncSession = Depends(get_async_session),
    settings: Settings = Depends(get_settings),
):
    try:
        user = await auth_service.authenticate(
            session, form_data.username, form_data.password
        )
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        access_token = auth_service.create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        refresh_token = auth_service.create_refresh_token(
            data={"sub": str(user.id)}, expires_delta=refresh_token_expires
        )
        return TokenResponse(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )
    except ServiceError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
    session: AsyncSession = Depends(get_async_session),
    settings: Settings = Depends(get_settings),
):
    try:
        user = await auth_service.authenticate(
            session, form_data.username, form_data.password
        )
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_service.create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        return TokenResponse(access_token=access_token, token_type="bearer")
    except ServiceError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        new_user = await auth_service.register_user(
            session, user_data.username, user_data.email, user_data.password
        )
        return UserResponse.model_validate(new_user)
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
