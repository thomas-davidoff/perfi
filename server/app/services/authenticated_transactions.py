from database import Transaction, TransactionCategory
from app.repositories import TransactionRepository
from typing import List
from uuid import UUID
from app.utils import StandardDate
from app.exceptions import ValidationError, ResourceNotFoundError
from .transactions import TransactionsService


class TransactionUserService(TransactionsService):
    """Class for handling transactions data as an authenticated user"""

    def __init__(self, transactions_repository, user_id):
        super().__init__(transactions_repository)

        user = self.user_service.get_by_id(user_id=user_id)

        if not user:
            raise Exception(f"User {user_id} does not exist.")

        self.user = user

    def create_transaction(self, data):

        # verify account exists
        account_id = data.get("account_id")
        user_accounts = [a.id for a in self.user.accounts]
        if UUID(account_id) not in user_accounts:
            # potential to raise flag for user trying to take an unauthorized action
            # user either incorrectly entering account ID or user is attempting to access info which is not theirs
            raise Exception(f"Account {account_id} does not exist")

        # validate amount
        amount = data.get("amount")
        if not isinstance(amount, (float, int)):
            raise ValidationError("amount must be a valid number")

        # validate date
        date = data.get("date")
        date = StandardDate(date)

        # merchant must be str
        merchant = data.get("merchant")
        if not isinstance(merchant, str):
            raise ValidationError("merchant must be string")

        category = data.get("category")
        if category is not None:
            # user passed in a category, so validate it
            try:
                category = TransactionCategory(category)
            except ValueError:
                valid_categories = [c.value for c in TransactionCategory]
                raise ValidationError(
                    f"Invalid category {category}. Must be one of: {', '.join(valid_categories)}"
                )

        description = data.get("description", "")

        transaction_data = {
            "amount": amount,
            "merchant": merchant,
            "date": date.to_string(),
            "category": category,
            "description": description,
            "account_id": account_id,
        }

        transaction = self.repo.create(data=transaction_data)

        return transaction

    def get_transactions_for_user(self) -> List[Transaction]:
        return self.user_service.get_transactions(user_id=self.user.id)

    def delete_transaction(self, transaction_id) -> None:
        # get the transaction
        transaction = self.repo.get_by_id(id=transaction_id)
        if not transaction:
            raise ResourceNotFoundError("Transaction not found")


def create_authenticated_transaction_service(user_id):
    transaction_repository = TransactionRepository()
    return TransactionUserService(transaction_repository, user_id)
