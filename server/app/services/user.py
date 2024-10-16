from database import User
from app.repositories import UserRepository
import re


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repo = user_repository

    def register(self, username, email, password) -> User:

        user_data = {"username": username, "email": email, "password": password}

        self._validate_user_data(user_data)

        new_user = self.user_repo.create(user_data)
        return new_user

    def _validate_user_data(self, user_data):
        for v in user_data.values():
            assert isinstance(v, str)
        if not self._validate_email(user_data["email"]):
            raise ValueError("Email address is invalid.")
        if not self._validate_username(user_data["username"]):
            raise ValueError("Username is invalid.")
        if not self._validate_password_complexity(user_data["password"]):
            raise ValueError("Password is too simple.")

    def _validate_email(self, email):
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if re.match(pattern, email):
            return True
        else:
            return False

    def _validate_username(self, username):
        return False if len(username) >= 12 or not isinstance(username, str) else True

    def _validate_password_complexity(self, password):
        """
        Validates password complexity.
        """

        return True if len(password) > 8 else False


def create_user_service():
    user_repository = UserRepository()
    return UserService(user_repository)
