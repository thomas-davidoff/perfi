from database import Transaction, User, Account
from app.repositories import TransactionRepository
from typing import List
from .accounts import create_accounts_service
from .user import create_user_service
from uuid import UUID


class TransactionsService:
    def __init__(self, transactions_repository: TransactionRepository) -> None:
        self.repo = transactions_repository
        self.accounts_service = create_accounts_service()
        self.user_service = create_user_service()

    def get_transactions_for_user(self, user_id: UUID) -> List[Transaction]:
        return self.user_service.get_transactions(user_id=user_id)


def create_transactions_service():
    transaction_repository = TransactionRepository()
    return TransactionsService(transaction_repository)
