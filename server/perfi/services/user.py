from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from perfi.core.repositories import UserRepository
from perfi.core.database import User, Account
from perfi.core.exc import ServiceError
import re


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repo = user_repository

    async def create_user(self, username: str, email: str, password: str) -> User:
        if not all([username, email, password]):
            raise ServiceError("All fields (username, email, password) are required.")

        user_data = {"username": username, "email": email, "password": password}
        await self._validate_user_data(user_data)

        if await self._user_exists(username):
            raise ServiceError("Username")
        if await self._user_exists(email):
            raise ServiceError("Email")

        return await self.user_repo.create(user_data)

    async def get_by_id(self, user_id: int) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ServiceError(f"User with ID {user_id} does not exist.")
        return user

    async def get_by_username_or_email(self, username_or_email: str) -> Optional[User]:
        return await self.user_repo.get_by_username_or_email(username_or_email)

    async def _validate_user_data(self, user_data: dict):
        if not self._validate_email(user_data["email"]):
            raise ServiceError("Invalid email address.")
        if not self._validate_username(user_data["username"]):
            raise ServiceError("Invalid username.")
        if not self._validate_password_complexity(user_data["password"]):
            raise ServiceError("Password is too simple.")

    def _validate_email(self, email: str) -> bool:
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return bool(re.match(pattern, email))

    def _validate_username(self, username: str) -> bool:
        return 6 <= len(username) <= 12

    def _validate_password_complexity(self, password: str) -> bool:
        return len(password) > 8

    async def _user_exists(self, username_or_email: str) -> bool:
        return bool(await self.user_repo.get_by_username_or_email(username_or_email))

    async def get_user_accounts(self, user_id: int) -> List[Account]:
        user = await self.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return list(user.accounts)

    async def get_transactions(self, user_id: int):
        accounts = await self.get_user_accounts(user_id)
        if not accounts:
            raise ServiceError("User has no accounts.")

        transactions = []
        for account in accounts:
            transactions.extend(account.transactions)
        return transactions
