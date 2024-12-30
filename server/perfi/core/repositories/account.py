from perfi.core.repositories.base import AsyncRepository
from perfi.core.database.models import Account
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
import logging


logger = logging.getLogger(__name__)


class AccountRepository(AsyncRepository[Account]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(entity_name="account", model=Account, session=session)

    async def get_by_user_id(self, user_id: UUID) -> list[Account]:
        query = select(self.model).filter(self.model.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def bulk_update_status(self, ids: list[UUID], status: str) -> None:
        query = select(self.model).filter(self.model.id.in_(ids))
        result = await self.session.execute(query)
        entities = result.scalars().all()
        if not entities:
            return

        for entity in entities:
            entity.status = status

        try:
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise e
