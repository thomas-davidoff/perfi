from perfi.core.repositories.base import AsyncRepository
from perfi.core.database.models import Transaction, Account
from sqlalchemy.ext.asyncio import AsyncSession
from perfi.core.exc import RepositoryError
from sqlalchemy.future import select
from datetime import datetime
from uuid import UUID
import logging


logger = logging.getLogger(__name__)


class TransactionRepository(AsyncRepository[Transaction]):
    def __init__(self) -> None:
        super().__init__(entity_name="transaction", model=Transaction)

    async def get_between_dates(
        self, session: AsyncSession, start_date: datetime, end_date: datetime
    ) -> list[Transaction]:
        if end_date < start_date:
            raise RepositoryError("start_date must be before or equal to end_date.")
        query = select(self.model).filter(self.model.date.between(start_date, end_date))
        result = await session.execute(query)
        return result.scalars().all()

    async def get_user_transactions(
        self, session: AsyncSession, user_id: UUID
    ) -> list[Transaction]:
        query = select(self.model).join(Account).filter(Account.user_id == user_id)
        result = await session.execute(query)
        return result.scalars().all()
