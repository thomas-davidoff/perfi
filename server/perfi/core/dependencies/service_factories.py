from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from perfi.services import (
    UserService,
    LocalFileService,
    AuthService,
    FileImportService,
    AccountsService,
    TransactionsService,
)

from perfi.core.repositories import (
    AccountRepository,
    UserRepository,
    TransactionRepository,
    TransactionsFileRepository,
)
from config import Settings
from .settings import get_settings


from .repo_factories import (
    get_account_repo,
    get_user_repo,
    get_transaction_repo,
    get_file_repo,
)
from .session import get_async_session


# user service factory
def get_user_service(session: AsyncSession = Depends(get_async_session)) -> UserService:
    user_repo = get_user_repo()
    return UserService(user_repo)


# accounts service factory
def get_accounts_service(
    accounts_repo: AccountRepository = Depends(get_account_repo),
) -> AccountsService:

    return AccountsService(accounts_repo=accounts_repo)


# transactions service factory
def get_transactions_service(
    transaction_repo: TransactionRepository = Depends(get_transaction_repo),
) -> TransactionsService:
    return TransactionsService(transaction_repository=transaction_repo)


def get_auth_service(
    user_service: UserService = Depends(get_user_service),
) -> AuthService:
    return AuthService(user_service)


def get_local_file_service(
    app_settings: Settings = Depends(get_settings),
) -> LocalFileService:
    upload_folder = app_settings.UPLOAD_FOLDER
    return LocalFileService(upload_folder=upload_folder)


# factory for file import service
def get_file_import_service(
    file_service: LocalFileService = Depends(get_local_file_service),
    file_repo: TransactionsFileRepository = Depends(get_file_repo),
    transaction_repo: TransactionRepository = Depends(get_transaction_repo),
    account_repo: AccountRepository = Depends(get_account_repo),
    user_repo: UserRepository = Depends(get_user_repo),
) -> FileImportService:
    return FileImportService(
        file_service, file_repo, transaction_repo, account_repo, user_repo
    )
