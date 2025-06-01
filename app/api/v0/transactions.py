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
import logging
from app.dependencies.resource_ownership import get_owned_account_for


logger = logging.getLogger(__name__)

# routes can double inject this auth dep m8
# don't forget it
# you got this
# #affirmations
router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    dependencies=[Depends(get_current_active_user)],
)


from app.models import Account
from app.repositories import AccountRepository
from app.exc import NotFoundException, AuthorizationException


async def verify_account_ownership(
    transaction_data: ApiTransactionCreateRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> Account:
    """Verify that the user owns the account specified in the transaction request."""
    account = await AccountRepository.get_one_by_id(
        session, transaction_data.account_id
    )

    if not account:
        raise NotFoundException("Account not found")

    if account.user_id != current_user.uuid:
        logger.warning("Unauthorized access attempted")
        raise AuthorizationException("You do not have access to this resource.")
        # raise NotFoundException("Account not found")  # use 404 instead of 403

    return account


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiSingletransactionResponse,
)
async def create_transaction(
    transaction_data: ApiTransactionCreateRequest,
    session: AsyncSession = Depends(get_session),
    account: Account = Depends(
        get_owned_account_for(ApiTransactionCreateRequest, "account_id")
    ),
):
    """Create a new transaction"""

    # translate creation request to db create model
    transaction_create = DbTransactionCreateSchema(
        account_id=account.uuid,
        **transaction_data.model_dump(exclude_none=True, exclude={"account_id"})
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
