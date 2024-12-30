from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from perfi.services.auth import AuthService
from perfi.core.dependencies.session import get_async_session
from perfi.core.dependencies.service_factories import get_auth_service
from perfi.core.exc import ServiceError
from perfi.schemas.auth import TokenResponse
from perfi.schemas.user import UserResponse, UserCreate

router = APIRouter(prefix="/auth", tags=["Authentication"])


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


@router.post("/token", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
    session: AsyncSession = Depends(get_async_session),
):
    user = await auth_service.authenticate(
        session, form_data.username, form_data.password
    )
    access_token, access_token_expires_at = auth_service.create_access_token(
        {"sub": str(user.id)}
    )
    refresh_token, refresh_token_expires_at = await auth_service.issue_refresh_token(
        user.id
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        access_token_expires_at=access_token_expires_at,
        refresh_token_expires_at=refresh_token_expires_at,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.validate_refresh_token(refresh_token)
    access_token, access_token_expires_at = auth_service.create_access_token(
        {"sub": str(user.id)}
    )
    (
        new_refresh_token,
        refresh_token_expires_at,
    ) = await auth_service.issue_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        access_token_expires_at=access_token_expires_at,
        refresh_token_expires_at=refresh_token_expires_at,
    )
