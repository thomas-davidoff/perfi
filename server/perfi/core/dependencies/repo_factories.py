from perfi.core.repositories import (
    AccountRepository,
    UserRepository,
    TransactionRepository,
    TransactionsFileRepository,
)


def get_account_repo() -> AccountRepository:
    return AccountRepository()


def get_user_repo() -> UserRepository:
    return UserRepository()


def get_transaction_repo() -> TransactionRepository:
    return TransactionRepository()


def get_file_repo() -> TransactionsFileRepository:
    return TransactionsFileRepository()
