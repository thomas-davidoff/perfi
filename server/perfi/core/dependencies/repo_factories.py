from perfi.core.repositories import (
    AccountRepository,
    UserRepository,
    TransactionRepository,
    TransactionsFileRepository,
    RefreshTokenRepository,
)
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .session import get_async_session


def get_account_repo() -> AccountRepository:
    return AccountRepository()


def get_user_repo() -> UserRepository:
    return UserRepository()


def get_transaction_repo() -> TransactionRepository:
    return TransactionRepository()


def get_file_repo() -> TransactionsFileRepository:
    return TransactionsFileRepository()


def get_refresh_token_repo(
    session: AsyncSession = Depends(get_async_session),
) -> RefreshTokenRepository:
    return RefreshTokenRepository(session=session)
