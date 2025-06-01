from app.models import Account
from app.repositories.base import RepositoryFactory
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID


class AccountRepository(RepositoryFactory(Account)):
    @classmethod
    async def get_by_user_id(
        cls, session: AsyncSession, user_id: UUID
    ) -> list[Account]:
        """Get all accounts for a specific user."""
        accounts = await cls.get_many_by_ids(
            session=session, ids=[user_id], column="user_id"
        )
        return accounts
