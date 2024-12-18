from database import User, Account
from app.repositories import UserRepository
import re
from app.exceptions import (
    ValidationError,
    PasswordTooSimpleError,
    InvalidEmailError,
    UserAlreadyExistsError,
)
from typing import List


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repo = user_repository

    def create_user(self, username, email, password) -> User:

        user_data = {"username": username, "email": email, "password": password}

        self._validate_user_data(user_data)

        # try to get user
        if self._user_exists(username):
            raise UserAlreadyExistsError(f"Username {username} already exists.")
        if self._user_exists(email):
            raise UserAlreadyExistsError(f"Email {email} already in-use.")

        new_user = self.user_repo.create(user_data)
        return new_user

    def get_by_id(self, user_id):
        return self.user_repo.get_by_id(user_id)

    def _validate_user_data(self, user_data):
        if not self._validate_email(user_data["email"]):
            raise InvalidEmailError("Email address is invalid.")
        if not self._validate_username(user_data["username"]):
            raise ValidationError("Username is invalid.")
        if not self._validate_password_complexity(user_data["password"]):
            raise PasswordTooSimpleError("Password is too simple.")

    def _validate_email(self, email):
        if not isinstance(email, str):
            return False
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

        return True if re.match(pattern, email) else False

    def _validate_username(self, username):
        if not isinstance(username, str):
            return False
        return False if len(username) > 12 or len(username) < 6 else True

    def _validate_password_complexity(self, password):
        """
        Validates password complexity.
        """
        # TODO: Obviously, make this way better.

        return True if len(password) > 8 else False

    def get_by_username_or_email(self, username_or_email) -> User | None:
        return self.user_repo.get_by_username_or_email(
            username_or_email=username_or_email
        )

    def _user_exists(self, username_or_email) -> bool:
        return isinstance(
            self.user_repo.get_by_username_or_email(username_or_email), User
        )

    def get_user_accounts(self, user_id) -> List[Account]:
        user = self.user_repo.get_by_id(user_id)
        accounts = user.accounts
        return accounts

    def get_transactions(self, user_id):
        transactions = []
        # get accounts for user
        accounts = self.get_user_accounts(user_id=user_id)

        if not accounts:
            raise Exception("User has no accounts.")

        # get all transactions for each account and merge into
        for account in accounts:
            account: Account
            t = account.transactions
            transactions.extend(t)

        return transactions


def create_user_service():
    user_repository = UserRepository()
    return UserService(user_repository)
