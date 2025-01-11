from fastapi import APIRouter, Depends, Response
from perfi.schemas.user import UserResponse
from perfi.core.database import User
from perfi.core.dependencies.current_user import get_current_user

router = APIRouter(tags=["Main"])


@router.get("/whoami", response_model=UserResponse)
async def whoami(current_user: User = Depends(get_current_user)):
    """
    Return details of the current user based on the JWT token.
    """
    return UserResponse.model_validate(current_user)


@router.get("/health")
async def health():
    """
    Returns 200 to indicate liveness
    """
    return Response(status_code=200)
