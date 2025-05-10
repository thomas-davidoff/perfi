from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.account import AccountRepository
from app.models import Account


class AccountService:
    @classmethod
    async def get_accounts_by_user_id(
        cls, session: AsyncSession, user_id: UUID
    ) -> list[Account]:
        return await AccountRepository.get_by_user_id(session, user_id)
