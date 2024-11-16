from database import Transaction, TransactionCategory
from app.repositories import TransactionRepository
from typing import List
from uuid import UUID
from app.utils import StandardDate
from app.exceptions import ValidationError, ResourceNotFoundError
from .transactions import TransactionsService
from sqlalchemy.exc import NoResultFound


class TransactionUserService(TransactionsService):
    """Class for handling transactions data as an authenticated user"""

    def __init__(self, transactions_repository, user_id):
        super().__init__(transactions_repository)

        user = self.user_service.get_by_id(user_id=user_id)

        if not user:
            raise Exception(f"User {user_id} does not exist.")

        self.user = user

    def validate_account_id(self, account_id):
        account_id = self._validate_uuid(account_id)
        user_accounts = [a.id for a in self.user.accounts]
        if UUID(account_id) not in user_accounts:
            # potential to raise flag for user trying to take an unauthorized action
            # user either incorrectly entering account ID or user is attempting to access info which is not theirs
            raise Exception(f"Account {account_id} does not exist")
        return account_id

    def create_transaction(self, data):
        account_id = self.validate_account_id(data.get("account_id"))
        amount = self.validate_amount(data.get("amount"))
        date = StandardDate(data.get("date"))
        merchant = self.validate_merchant(data.get("merchant"))
        category = self.validate_category(data.get("category"))
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
        # validate transaction_id is uuid
        transaction_id = self._validate_uuid(transaction_id)
        try:
            self.repo.delete(transaction_id)
        except NoResultFound:
            raise ResourceNotFoundError(
                f"Transaction with ID {transaction_id} does not exist."
            )


def create_authenticated_transaction_service(user_id):
    transaction_repository = TransactionRepository()
    return TransactionUserService(transaction_repository, user_id)
