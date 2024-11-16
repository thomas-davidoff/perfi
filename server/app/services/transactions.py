from app.repositories import TransactionRepository
from .accounts import create_accounts_service
from .user import create_user_service
from database import TransactionCategory
from app.exceptions import ValidationError
from uuid import UUID
from app.utils import StandardDate


class TransactionsService:
    def __init__(self, transactions_repository: TransactionRepository) -> None:
        self.repo = transactions_repository
        self.accounts_service = create_accounts_service()
        self.user_service = create_user_service()

    def _validate_uuid(self, id):
        """Converts string id into a uuid object. Raises ValidationError if uuid is improper."""
        try:
            transaction_id = UUID(id)
        except (ValueError, TypeError):
            raise ValidationError("Transaction ID must be a valid UUID")

        return transaction_id

    def validate_category(self, category):
        if category is not None:
            # user passed in a category, so validate it
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
            raise ValidationError("merchant must be string")
        return merchant

    def validate_amount(self, amount):
        if not isinstance(amount, (float, int)):
            raise ValidationError("amount must be a valid number")
        return amount

    def validate_date(self, date):
        try:
            date = StandardDate(date)
        except Exception:
            raise ValidationError("Invalid date.")
        return date


def create_transactions_service():
    transaction_repository = TransactionRepository()
    return TransactionsService(transaction_repository)
