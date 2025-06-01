from app.models import Transaction
from app.repositories.base import RepositoryFactory


class TransactionRepository(RepositoryFactory(Transaction)):
    pass
