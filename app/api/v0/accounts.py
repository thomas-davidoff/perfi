from typing import Annotated
from fastapi import Depends, status, APIRouter
from db.session_manager import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.accounts import AccountService
from app.models import User
from app.dependencies.auth import get_current_active_user
from app.api.v0.schemas.account import (
    ApiSingleAccountResponse,
    ApiListAccountResponse,
    ApiAccountCreateRequest,
)
from app.schemas.account import DbAccountCreateSchema


router = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
    dependencies=[Depends(get_current_active_user)],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiSingleAccountResponse,
    response_model_exclude_none=True,
)
async def create_account(
    account_data: ApiAccountCreateRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_session),
):
    """Create a new account"""

    # translate creation request to db create model
    account_create = DbAccountCreateSchema(
        user_id=current_user.uuid, **account_data.model_dump(exclude_none=True)
    )

    transaction = await AccountService.create_account(
        session=session, data=account_create
    )
    return {"data": transaction}
