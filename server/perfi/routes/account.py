from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from perfi.core.database import User
from perfi.schemas import (
    Account as AccountSchema,
    AccountCreateRequest,
    GenericResponse,
    AccountUpdateRequest,
)
from perfi.core.dependencies.current_user import get_current_user
from perfi.core.dependencies.service_factories import get_accounts_service
from perfi.core.dependencies.session import get_async_session
from perfi.services import AccountsService
from sqlalchemy.ext.asyncio import AsyncSession
from perfi.core.database import Account as AccountDBModel

from perfi.core.dependencies.resource_ownership import get_validated_account

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/account", tags=["Account"])


@router.post("/", response_model=AccountSchema)
async def create_account(
    account_data: AccountCreateRequest,
    current_user: User = Depends(get_current_user),
    accounts_service: AccountsService = Depends(get_accounts_service),
    session: AsyncSession = Depends(get_async_session),
) -> AccountSchema:
    """
    Create a new account for the current user.

    Args:
        account_data (AccountCreateRequest): The account details to be created.
        current_user (User): The currently authenticated user (from dependency).
        accounts_service (AccountsService): The service for managing accounts.
        session (AsyncSession): The database session (from dependency).

    Returns:
        Account: The created account serialized as a Pydantic model.
    """
    logger.debug("Request for account creation")
    account = await accounts_service.create_account(
        session=session, user_id=current_user.id, data=account_data.model_dump()
    )
    logger.debug(f"Created account: {str(account)}")
    return AccountSchema.model_validate(account)


@router.get("/", response_model=GenericResponse[AccountSchema])
async def get_accounts(
    current_user: User = Depends(get_current_user),
    accounts_service: AccountsService = Depends(get_accounts_service),
    session: AsyncSession = Depends(get_async_session),
) -> GenericResponse[AccountSchema]:
    """
    Retrieve the list of accounts for the current user.

    Args:
        current_user (User): The currently authenticated user (from dependency).
        accounts_service (AccountsService): The service for managing accounts.
        session (AsyncSession): The database session (from dependency).

    Returns:
        GenericResponse[Account]: A list of accounts associated with the current user.
    """
    accounts = await accounts_service.get_accounts_by_user_id(
        session=session, user_id=current_user.id
    )
    return GenericResponse(data=[AccountSchema.model_validate(a) for a in accounts])


@router.get("/{account_id}", response_model=AccountSchema)
async def get_account(
    account: AccountDBModel = Depends(get_validated_account),
) -> AccountSchema:
    """
    Retrieve a single account by its ID.
    """
    return AccountSchema.model_validate(account)


@router.put("/{account_id}", response_model=AccountSchema)
async def update_account(
    account_data: AccountUpdateRequest,
    account: AccountDBModel = Depends(get_validated_account),
    session: AsyncSession = Depends(get_async_session),
    accounts_service: AccountsService = Depends(get_accounts_service),
) -> AccountSchema:
    """
    Update an account by its ID.
    """
    return await accounts_service.update_account(
        account=account,
        session=session,
        data=account_data.model_dump(),
    )


@router.delete("/{account_id}", status_code=200)
async def delete_account(
    account: AccountDBModel = Depends(get_validated_account),
    accounts_service: AccountsService = Depends(get_accounts_service),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Delete an account by its ID.
    """
    await accounts_service.delete_account(
        account=account, session=session, account_id=account.id
    )
    return {"message": f"Account {str(account.id)} has been deleted."}