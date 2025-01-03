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


def get_account_repo(
    session: AsyncSession = Depends(get_async_session),
) -> AccountRepository:
    return AccountRepository(session=session)


def get_user_repo(
    session: AsyncSession = Depends(get_async_session),
) -> UserRepository:
    return UserRepository(session=session)


def get_transaction_repo(
    session: AsyncSession = Depends(get_async_session),
) -> TransactionRepository:
    return TransactionRepository(session=session)


def get_file_repo(
    session: AsyncSession = Depends(get_async_session),
) -> TransactionsFileRepository:
    return TransactionsFileRepository(session=session)


def get_refresh_token_repo(
    session: AsyncSession = Depends(get_async_session),
) -> RefreshTokenRepository:
    return RefreshTokenRepository(session=session)
