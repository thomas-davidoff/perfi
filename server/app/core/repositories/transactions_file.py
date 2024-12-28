from app.core.repositories.base import AsyncRepository
from app.core.database.models import TransactionsFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.core.exc import RepositoryError
from sqlalchemy.future import select
from uuid import UUID


class TransactionsFileRepository(AsyncRepository[TransactionsFile]):
    def __init__(self) -> None:
        super().__init__(entity_name="transactions_file_import", model=TransactionsFile)

    async def get_by_id(
        self, session: AsyncSession, id: UUID, user_id: UUID
    ) -> TransactionsFile:
        query = select(self.model).filter(
            self.model.id == id, self.model.user_id == user_id
        )
        result = await session.execute(query)
        entity = result.scalar_one_or_none()
        if not entity:
            raise RepositoryError(f"{self.entity_name} with ID {id} does not exist.")
        return entity

    async def create(self, session: AsyncSession, data: dict) -> TransactionsFile:
        try:
            return await super().create(session, data)
        except IntegrityError as e:
            if "violates unique constraint" in str(e):
                raise RepositoryError("Transaction file already exists")
            raise RepositoryError from e

    async def get_by_status(
        self, session: AsyncSession, status: str
    ) -> list[TransactionsFile]:
        query = select(self.model).filter(self.model.status == status)
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
            raise RepositoryError from e
