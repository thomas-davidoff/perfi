from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from perfi.core.database import Transaction, TransactionCategory
from perfi.core.repositories import TransactionRepository
from perfi.core.exc import ValidationError
from perfi.core.utils import StandardDate
from perfi.core.validators import TransactionAmount
import logging
from .resource_service import ResourceService

from perfi.core.exc import ServiceError, ResourceNotFound


logger = logging.getLogger(__name__)


class TransactionsService(ResourceService[Transaction]):
    def __init__(self, transaction_repository: TransactionRepository) -> None:
        self.repo = transaction_repository

        # TODO: Massive refactor to use pydantic transaction request schema for validation

    def _validate_uuid(self, id_value: str | UUID) -> UUID:
        """Validates and converts an ID to a UUID object."""
        if isinstance(id_value, UUID):
            return id_value
        try:
            return UUID(id_value)
        except (ValueError, TypeError):
            raise ValidationError("ID must be a valid UUID.")

    def validate_category(
        self, category: Optional[str]
    ) -> Optional[TransactionCategory]:
        if category is None:
            return None
        category = category.upper()
        try:
            return TransactionCategory(category)
        except ValueError:
            valid_categories = [c.value for c in TransactionCategory]
            raise ValidationError(
                f"Invalid category '{category}'. Must be one of: {', '.join(valid_categories)}."
            )

    def validate_merchant(self, merchant: Optional[str]) -> Optional[str]:
        if merchant is None:
            return None
        if not isinstance(merchant, str):
            raise ValidationError("Merchant must be a string.")
        return merchant

    def validate_date(self, date: Optional[str]) -> StandardDate:
        try:
            return StandardDate(date)
        except Exception:
            raise ValidationError("Invalid date.")

    def validate_amount(self, amount: float) -> float:
        try:
            return TransactionAmount(amount).value
        except Exception:
            raise ValidationError("Invalid amount.")

    async def create_transaction(self, data: dict) -> Transaction:
        logger.debug(data)
        transaction_data = {
            "amount": self.validate_amount(data.get("amount")),
            "merchant": self.validate_merchant(data.get("merchant")),
            "date": self.validate_date(data.get("date")).date,
            "category": self.validate_category(data.get("category")),
            "description": data.get("description", ""),
            "account_id": self._validate_uuid(data.get("account_id")),
        }

        return await self.repo.create(data=transaction_data)

    async def get_transactions_by_user_id(self, user_id: UUID) -> List[Transaction]:
        return await self.repo.get_user_transactions(user_id=user_id)

    async def delete_transaction(self, transaction_id: UUID) -> None:
        transaction_id = self._validate_uuid(transaction_id)
        await self.repo.delete(transaction_id)

    async def fetch_by_id(self, transaction_id: UUID) -> Transaction:
        """
        Fetch an transaction by its ID.

        Args:
            account_id (UUID): The transaction ID to fetch.

        Returns:
            Transaction: The transaction object.

        Raises:
            ServiceError: If the transaction is not found.
        """
        try:
            transaction = await self.repo.get_by_id(transaction_id)
        except ResourceNotFound as e:
            raise ServiceError(str(e)) from e
        return transaction

    async def update_transaction(
        self, transaction: Transaction, data: dict
    ) -> Transaction:
        """
        Update an existing transaction
        """
        return await self.repo.update(entity=transaction, data=data)
