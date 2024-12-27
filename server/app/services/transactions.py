from database import Transaction, TransactionCategory
from app.repositories import TransactionRepository
from typing import List
from app.validators import TransactionAmount
from app.exceptions import ValidationError
from uuid import UUID
from app.utils import StandardDate


class TransactionsService:
    def __init__(
        self,
    ):
        self.repo = TransactionRepository()

    def _validate_uuid(self, id_value: str | UUID) -> UUID:
        """Validates and converts an ID to a UUID object."""
        if isinstance(id_value, UUID):
            return id_value
        try:
            return UUID(id_value)
        except (ValueError, TypeError):
            raise ValidationError("ID must be a valid UUID")

    def validate_category(self, category):
        # coerce to uppercase for enum
        category = category.upper()
        if category is not None:
            try:
                category = TransactionCategory(category)
            except ValueError:
                valid_categories = [c.value for c in TransactionCategory]
                raise ValidationError(
                    f"Invalid category {category}. Must be one of: {', '.join(valid_categories)}"
                )
        return category

    def validate_merchant(self, merchant):
        if not isinstance(merchant, str):
            raise ValidationError("merchant must be a string")
        return merchant

    def validate_date(self, date):
        try:
            date = StandardDate(date)
        except Exception:
            raise ValidationError("Invalid date.")
        return date

    def validate_amount(self, amount):
        try:
            return TransactionAmount(amount).value
        except Exception:
            raise ValidationError("Invalid amount.")

    def create_transaction(self, data: dict) -> Transaction:
        transaction_data = {
            "amount": self.validate_amount(data.get("amount")),
            "merchant": self.validate_merchant(data.get("merchant")),
            "date": self.validate_date(data.get("date")).to_string(),
            "category": self.validate_category(data.get("category")),
            "description": data.get("description", ""),
            "account_id": self._validate_uuid(data.get("account_id")),
        }

        return self.repo.create(data=transaction_data)

    def get_transactions_by_user_id(self, user_id: UUID) -> List[Transaction]:
        return self.repo.get_user_transactions(user_id=user_id)

    def delete_transaction(self, transaction_id: UUID) -> None:
        self.repo.delete(transaction_id)


def create_transactions_service():
    return TransactionsService()
