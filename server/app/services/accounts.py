from database import Transaction, Account, AccountType
from typing import List
from app.repositories import AccountRepository
from app.exceptions import ValidationError
from app.services import create_user_service


class AccountsService:
    def __init__(self, accounts_repo: AccountRepository):
        self.repo = accounts_repo
        self.user_service = create_user_service()

    def get_transactions(self, account_id) -> List[Transaction]:
        account = self.get_account(account_id)
        return account.transactions

    def get_account(self, account_id):
        return self.repo.get_by_id(account_id)

    def get_user_accounts(self, user_id):
        return self.user_service.get_user_accounts(user_id=user_id)

    def create_account(self, user_id, data) -> Account:

        account_name = data.get("account_name")
        if account_name is None:
            raise ValidationError("You must provide a valid account_name.")
        elif not isinstance(account_name, str):
            raise ValidationError("Account name must be a string.")

        # TODO: check existing accounts for user. cannot duplicate the name for the user.

        existing_accounts = self.get_user_accounts(user_id=user_id)
        existing_account_names = [a.name for a in existing_accounts]
        if account_name in existing_account_names:
            raise ValidationError(f"You already have an account named {account_name}")

        # validate account name

        balance = data.get("balance")
        if not isinstance(balance, (int, float)):
            raise ValidationError("Balance must be a valid number.")
        # validate balance

        account_type = data.get("account_type")
        # validate account type
        try:
            account_type_input = data.get("account_type")
            account_type = AccountType(account_type_input)
        except ValueError:
            valid_types = [t.value for t in AccountType]
            raise ValidationError(
                f"Invalid account type '{account_type}'. Must be one of: {', '.join(valid_types)}"
            )
        except Exception as e:
            raise Exception(e)

        account_data = {
            "user_id": user_id,
            "name": account_name,
            "balance": balance,
            "account_type": account_type,
        }
        account = self.repo.create(account_data)
        return account


def create_accounts_service() -> AccountsService:
    accounts_repository = AccountRepository()
    return AccountsService(accounts_repo=accounts_repository)
