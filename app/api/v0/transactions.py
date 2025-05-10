from typing import Annotated
from app.schemas.transaction import TransactionCreateSchema, TransactionSchema
from fastapi import Depends, status, APIRouter
from db.session_manager import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v0.schema import SingleTransactionResponse
from app.services.transactions import TransactionService
from app.models import User
from app.dependencies.auth import get_current_active_user


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
    response_model=SingleTransactionResponse,
    response_model_exclude_none=True,
)
async def create_transaction(
    transaction_data: TransactionCreateSchema,
    session: AsyncSession = Depends(get_session),
):
    """Create a new transaction"""
    transaction = await TransactionService.create_transaction(
        session=session, data=transaction_data
    )

    return {"data": transaction}
