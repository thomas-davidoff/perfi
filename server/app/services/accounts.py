from database import Transaction
from typing import List
from app.repositories import AccountRepository


class AccountsService:
    def __init__(self, accounts_repo: AccountRepository):
        self.repo = accounts_repo

    def get_transactions(self, account_id) -> List[Transaction]:
        account = self.get_account(account_id)
        return account.transactions

    def get_account(self, account_id):
        return self.repo.get_by_id(account_id)


def create_accounts_service() -> AccountsService:
    accounts_repository = AccountRepository()
    return AccountsService(accounts_repo=accounts_repository)
