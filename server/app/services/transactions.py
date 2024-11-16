from app.repositories import TransactionRepository
from .accounts import create_accounts_service
from .user import create_user_service


class TransactionsService:
    def __init__(self, transactions_repository: TransactionRepository) -> None:
        self.repo = transactions_repository
        self.accounts_service = create_accounts_service()
        self.user_service = create_user_service()


def create_transactions_service():
    transaction_repository = TransactionRepository()
    return TransactionsService(transaction_repository)
