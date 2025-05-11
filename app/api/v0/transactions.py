from typing import Annotated
from fastapi import Depends, status, APIRouter
from db.session_manager import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.transactions import TransactionService
from app.models import User
from app.dependencies.auth import get_current_active_user
from app.api.v0.schemas.transaction import (
    ApiSingletransactionResponse,
    ApiListtransactionResponse,
    ApiTransactionCreateRequest,
)
from app.schemas.transaction import DbTransactionCreateSchema

# routes can double inject this auth dep m8
# don't forget it
# you got this
# #affirmations
router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    dependencies=[Depends(get_current_active_user)],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiSingletransactionResponse,
)
async def create_transaction(
    transaction_data: ApiTransactionCreateRequest,
    session: AsyncSession = Depends(get_session),
):
    """Create a new transaction"""

    print(transaction_data)

    # translate creation request to db create model
    transaction_create = DbTransactionCreateSchema.model_validate(
        transaction_data, from_attributes=True
    )

    transaction = await TransactionService.create_transaction(
        session=session, data=transaction_create
    )

    return {"data": transaction}


@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=ApiListtransactionResponse
)
async def list_transactions(
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_session),
):
    """Get transactions"""

    transactions = await TransactionService.list_transactions(
        session=session, user_id=current_user.uuid
    )

    return {"data": transactions}
