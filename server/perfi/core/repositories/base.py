from abc import ABC
from typing import List, TypeVar, Generic, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from perfi.core.exc import RepositoryError, ResourceNotFound
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T")


class AsyncRepository(ABC, Generic[T]):
    def __init__(self, entity_name: str, model: T) -> None:
        self.entity_name = entity_name
        self.model = model

    async def create(self, session: AsyncSession, data: dict) -> T:
        """Creates an entity of type T."""
        entity = self.model(**data)
        session.add(entity)
        try:
            await session.commit()
            await session.refresh(entity)  # Refresh to get the generated ID or defaults
            return entity
        except IntegrityError as e:
            logger.error(f"Integrity error when attempting to create {entity}")
            await session.rollback()
            raise RepositoryError(str(e)) from e
        except Exception as e:
            logger.error(f"Unexpected error: {e} when attempting to create {entity}")
            await session.rollback()
            raise RepositoryError(str(e)) from e

    async def get_by_id(self, session: AsyncSession, id: int) -> Optional[T]:
        """Gets an entity by ID."""
        if isinstance(id, str):
            id = UUID(id)
        query = select(self.model).filter(self.model.id == id)
        result = await session.execute(query)
        entity = result.scalar_one_or_none()
        if not entity:
            raise ResourceNotFound(f"No such {self.entity_name}: {id}.")
        return entity

    async def get_all(self, session: AsyncSession) -> List[T]:
        """Gets all entities."""
        query = select(self.model)
        result = await session.execute(query)
        return result.scalars().all()

    async def delete(self, session: AsyncSession, id: int) -> int:
        """Deletes an entity by ID."""
        entity = await self.get_by_id(session, id)
        if entity:
            await session.delete(entity)
            await session.commit()
            return id
        else:
            logger.error(f"No {self.entity_name} with ID {id} exists.")
            raise ResourceNotFound(f"No such {self.entity_name}: {id}.")

    async def update_by_id(self, session: AsyncSession, id: int, data: dict) -> T:
        """Updates an existing entity in the database."""
        entity = await self.get_by_id(session, id)
        return await self.update(session=session, entity=entity, data=data)

    async def update(self, session: AsyncSession, entity: T, data: dict) -> T:
        for key, value in data.items():
            setattr(entity, key, value)
        try:
            await session.commit()
            await session.refresh(entity)
            return entity
        except Exception as e:
            logger.error(f"Error updating {self.entity_name}: {e}")
            await session.rollback()
            raise RepositoryError(str(e)) from e

    async def get_where(self, session: AsyncSession, filter_data: dict) -> T | None:

        from pprint import pprint

        pprint(filter_data)
        query = select(self.model).filter_by(**filter_data)
        result = await session.execute(query)
        return result.scalar_one_or_none()
