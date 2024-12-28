from app.core.repositories.base import AsyncRepository
from app.core.database.models import Account
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
import logging


logger = logging.getLogger(__name__)


class AccountRepository(AsyncRepository[Account]):
    def __init__(self) -> None:
        super().__init__(entity_name="account", model=Account)

    async def get_user_accounts(
        self, session: AsyncSession, user_id: UUID
    ) -> list[Account]:
        query = select(self.model).filter(self.model.user_id == user_id)
        result = await session.execute(query)
        return result.scalars().all()

    async def bulk_update_status(
        self, session: AsyncSession, ids: list[UUID], status: str
    ) -> None:
        query = select(self.model).filter(self.model.id.in_(ids))
        result = await session.execute(query)
        entities = result.scalars().all()
        if not entities:
            return

        for entity in entities:
            entity.status = status

        try:
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
