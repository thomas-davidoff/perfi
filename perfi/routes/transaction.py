from fastapi import APIRouter, Depends
from perfi.models import (
    TransactionCategory,
    User,
    Transaction as TransactionDBModel,
)
from perfi.schemas import (
    Transaction as TransactionSchema,
    GenericResponse,
    TransactionCreateRequest,
    TransactionUpdateRequest,
)
from perfi.core.dependencies.current_user import get_current_user
from perfi.core.dependencies.service_factories import (
    get_transactions_service,
    get_accounts_service,
)
from perfi.core.dependencies.resource_ownership import get_validated_transaction
from perfi.services import TransactionsService, AccountsService
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/transactions", tags=["Transaction"])


@router.get("/categories", response_model=GenericResponse[str])
async def list_categories(
    current_user: User = Depends(get_current_user),
) -> GenericResponse[str]:
    """
    Retrieve the list of valid transaction categories.

    Args:
        current_user (User): The currently authenticated user (from dependency).

    Returns:
        GenericResponse[str]: A list of valid transaction categories in a standardized response format.
    """
    return GenericResponse(data=[c.value.capitalize() for c in TransactionCategory])


@router.get("/", response_model=GenericResponse[TransactionSchema])
async def list_transactions(
    current_user: User = Depends(get_current_user),
    transactions_service: TransactionsService = Depends(get_transactions_service),
) -> GenericResponse[TransactionSchema]:
    """
    Retrieve the list of transactions for the current user.

    Args:
        current_user (User): The currently authenticated user (from dependency).
        transactions_service (TransactionsService): The service for managing transactions.

    Returns:
        GenericResponse[Transaction]: A list of transactions associated with the current user.
    """
    transactions = await transactions_service.get_transactions_by_user_id(
        user_id=current_user.id
    )
    return GenericResponse(
        data=[TransactionSchema.model_validate(t).model_dump() for t in transactions]
    )


@router.post("/", response_model=TransactionSchema)
async def create_transaction(
    transaction_data: TransactionCreateRequest,
    transactions_service: TransactionsService = Depends(get_transactions_service),
    current_user: User = Depends(get_current_user),
    accounts_service: AccountsService = Depends(get_accounts_service),
) -> TransactionSchema:
    """
    Create a new transaction for the current user.

    Args:
        transaction_data (TransactionCreateRequest): The transaction details to be created.
        transactions_service (TransactionsService): The service for managing transactions.

    Returns:
        Transaction: The created transaction serialized as a Pydantic model.
    """
    logger.debug("Request for transaction creation")
    transaction = await transactions_service.create_transaction(
        user=current_user, data=transaction_data, accounts_service=accounts_service
    )
    logger.debug(f"Created transaction: {str(transaction)}")
    return TransactionSchema.model_validate(transaction)


@router.delete("/{transaction_id}", status_code=200)
async def delete_transaction(
    transaction_id: UUID,
    transactions_service: TransactionsService = Depends(get_transactions_service),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Delete a transaction by its ID.

    Args:
        transaction_id (UUID): The unique identifier of the transaction to delete.
        current_user (User): The currently authenticated user (from dependency).
        transactions_service (TransactionsService): The service for managing transactions.

    Returns:
        dict: A confirmation message indicating successful deletion.
    """
    await transactions_service.delete_transaction(transaction_id=transaction_id)
    return {"message": f"Transaction {transaction_id} has been deleted."}


@router.get("/{transaction}", response_model=TransactionSchema)
async def get_transaction(
    transaction: TransactionDBModel = Depends(get_validated_transaction),
) -> TransactionSchema:
    """
    Retrieve a single transaction by its ID.
    """
    return TransactionSchema.model_validate(transaction)


@router.put("/{transaction}", response_model=TransactionSchema)
async def update_transaction(
    transaction_data: TransactionUpdateRequest,
    transaction: TransactionDBModel = Depends(get_validated_transaction),
    transactions_service: TransactionsService = Depends(get_transactions_service),
) -> TransactionSchema:
    """
    Update a transaction by its ID.
    """
    transaction = await transactions_service.update_transaction(
        transaction=transaction,
        data=transaction_data.model_dump(exclude_unset=True),
    )
    return TransactionSchema.model_validate(transaction)
