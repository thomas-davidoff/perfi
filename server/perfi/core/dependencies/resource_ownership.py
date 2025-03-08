from fastapi import Depends, HTTPException, status, Path
from typing import TypeVar, Generic
from uuid import UUID
import logging
from perfi.core.exc import ValidationError, UnauthorizedAccessError
from perfi.models import Account, Transaction, User, TransactionsFile
from perfi.services import AccountsService, TransactionsService, FileImportService
from .current_user import get_current_user
from .service_factories import (
    get_accounts_service,
    get_transactions_service,
    get_file_import_service,
)


T = TypeVar("T")


logger = logging.getLogger(__name__)


async def validate_ownership(
    resource_id: UUID,
    user_id: str,
    service: Generic[T],
) -> T:
    """
    Validate that a resource belongs to the given user.

    Args:
        resource_id (str): The ID of the resource.
        user_id (str): The ID of the current user.
        service (Generic[T]): The service for managing the resource.

    Returns:
        T: The validated resource.

    Raises:
        HTTPException: If the resource is not found or the user is unauthorized.
    """

    logger.debug(f"Attempting to validate ownership over resource")

    if not isinstance(resource_id, UUID):
        try:
            resource_id = UUID(resource_id)
        except ValueError as e:
            raise ValidationError(str(e)) from e

    resource = await service.fetch_by_id(resource_id)

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{service.__class__.__name__} with ID {resource_id} not found.",
        )

    if resource.user_id != user_id:
        raise UnauthorizedAccessError

    return resource


async def get_validated_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    accounts_service: AccountsService = Depends(get_accounts_service),
) -> Account:
    """
    Validate that the account belongs to the current user.

    Args:
        account_id (str): The account ID.
        current_user (User): The currently authenticated user.

    Returns:
        Account: The validated account.
    """
    return await validate_ownership(
        resource_id=account_id,
        user_id=current_user.id,
        service=accounts_service,
    )


async def get_validated_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    transactions_service: TransactionsService = Depends(get_transactions_service),
) -> Transaction:
    """
    Validate that the transaction belongs to the current user.

    Args:
        account_id (str): The transaction ID.
        current_user (User): The currently authenticated user.

    Returns:
        Transaction: The validated transaction.
    """
    return await validate_ownership(
        resource_id=transaction_id,
        user_id=current_user.id,
        service=transactions_service,
    )


async def get_validated_transactions_file(
    file_id: UUID = Path(..., alias="file_id"),
    current_user=Depends(get_current_user),
    transactions_file_service: FileImportService = Depends(get_file_import_service),
) -> TransactionsFile:
    """
    Validate that the transactions_file belongs to the current user.

    Args:
        file_id (UUID): The file ID from the path.
        current_user (User): The currently authenticated user.
        transactions_file_service (TransactionsFileService): The service for transactions files.

    Returns:
        TransactionsFile: The validated transactions_file.
    """
    return await validate_ownership(
        resource_id=file_id,
        user_id=current_user.id,
        service=transactions_file_service,
    )
