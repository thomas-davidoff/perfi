from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from perfi.core.repositories import AccountRepository
from perfi.core.database import Account, AccountType
from perfi.core.exc import ServiceError, ResourceNotFound
import logging
from .resource_service import ResourceService


logger = logging.getLogger(__name__)


class AccountsService(ResourceService[Account]):
    def __init__(self, accounts_repo: AccountRepository):
        self.repo = accounts_repo

    async def fetch_by_id(self, session: AsyncSession, account_id: UUID) -> Account:
        """
        Fetch an account by its ID.

        Args:
            session (AsyncSession): The database session.
            account_id (UUID): The account ID to fetch.

        Returns:
            Account: The account object.

        Raises:
            ServiceError: If the account is not found.
        """
        try:
            account = await self.repo.get_by_id(session, account_id)
        except ResourceNotFound as e:
            logger.debug("Caught resource not found in accounts_service")
            raise ServiceError(str(e)) from e
        return account

    async def ensure_ownership(self, account: Account, user_id: UUID) -> None:
        """
        Ensure the given account belongs to the specified user.

        Args:
            account (Account): The account to validate.
            user_id (UUID): The user ID to validate ownership.

        Raises:
            ServiceError: If the account does not belong to the user.
        """
        if account.user_id != user_id:
            raise ServiceError("You do not have access to this resource.")

    async def get_account(
        self, account: Optional[Account], session: AsyncSession, account_id: UUID
    ) -> Account:
        """
        Get account details by account ID. If an account is already provided, reuse it.

        Args:
            account (Optional[Account]): The already validated account object, if available.
            session (AsyncSession): The database session.
            account_id (UUID): The account ID to fetch if the account is not provided.

        Returns:
            Account: The account object.
        """
        if account:
            return account
        return await self.fetch_by_id(session, account_id)

    async def get_accounts_by_user_id(
        self, session: AsyncSession, user_id: UUID
    ) -> List[Account]:
        """
        Get all accounts for a specific user.

        Args:
            session (AsyncSession): The database session.
            user_id (UUID): The user ID whose accounts to fetch.

        Returns:
            List[Account]: A list of the user's accounts.
        """
        return await self.repo.get_by_user_id(session, user_id)

    async def create_account(
        self, session: AsyncSession, user_id: UUID, data: dict
    ) -> Account:
        """
        Create a new account for a user.

        Args:
            session (AsyncSession): The database session.
            user_id (UUID): The user ID creating the account.
            data (dict): The account data.

        Returns:
            Account: The newly created account.
        """
        account_name = data.get("name")
        if not account_name or not isinstance(account_name, str):
            raise ServiceError("You must provide a valid account name.")

        # Ensure account name is unique for the user
        existing_accounts = await self.get_accounts_by_user_id(session, user_id)
        if account_name in [account.name for account in existing_accounts]:
            raise ServiceError(f"Account with name '{account_name}' already exists.")

        # Validate balance
        balance = data.get("balance")
        if not isinstance(balance, (int, float)):
            raise ServiceError("Balance must be a valid number.")

        # Validate account type
        account_type_input = data.get("account_type")
        try:
            account_type = AccountType(account_type_input)
        except ValueError:
            valid_types = ", ".join([t.value for t in AccountType])
            raise ServiceError(
                f"Invalid account type '{account_type_input}'. Must be one of: {valid_types}."
            )

        account_data = {
            "user_id": user_id,
            "name": account_name,
            "balance": balance,
            "account_type": account_type,
        }
        return await self.repo.create(session, account_data)

    async def update_account(
        self,
        account: Account,
        session: AsyncSession,
        data: dict,
    ) -> Account:
        """
        Update an account's details.
        """
        return await self.repo.update(session=session, entity=account, data=data)

    async def delete_account(
        self, account: Optional[Account], session: AsyncSession, account_id: UUID
    ) -> None:
        """
        Delete an account. If an account is already provided, reuse it.

        Args:
            account (Optional[Account]): The already validated account object, if available.
            session (AsyncSession): The database session.
            account_id (UUID): The ID of the account to delete if the account is not provided.
        """
        if not account:
            account = await self.fetch_by_id(session, account_id)
        await self.repo.delete(session, account.id)
