from app.models import Account
from app.repositories.base import RepositoryFactory


class AccountRepository(RepositoryFactory(Account)):
    pass
