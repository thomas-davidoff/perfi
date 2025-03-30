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
    def __init__(self, entity_name: str, model: T, session: AsyncSession) -> None:
        self.entity_name = entity_name
        self.model = model
        self.session = session

    async def create(self, data: dict) -> T:
        """Creates an entity of type T."""
        entity = self.model(**data)
        self.session.add(entity)
        try:
            await self.session.commit()
            await self.session.refresh(entity)
            return entity
        except IntegrityError as e:
            logger.error(f"Integrity error when attempting to create {entity}")
            await self.session.rollback()
            raise RepositoryError(f"Integrity error when attempting to create.") from e
        except Exception as e:
            logger.error(f"Unexpected error: {e} when attempting to create {entity}")
            await self.session.rollback()
            raise RepositoryError(f"Unexpected error") from e

    async def get_by_id(self, id: int) -> T | None:
        """Gets an entity by ID."""
        if isinstance(id, str):
            id = UUID(id)
        query = select(self.model).filter(self.model.id == id)
        result = await self.session.execute(query)
        entity = result.scalar_one_or_none()
        if not entity:
            raise ResourceNotFound(f"No such {self.entity_name}: {id}.")
        return entity

    async def get_all(self) -> List[T]:
        """Gets all entities."""
        query = select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def delete(self, id: int) -> int:
        """Deletes an entity by ID."""
        entity = await self.get_by_id(id)
        if entity:
            await self.session.delete(entity)
            await self.session.commit()
            return id
        else:
            logger.error(f"No {self.entity_name} with ID {id} exists.")
            raise ResourceNotFound(f"No such {self.entity_name}: {id}.")

    async def update_by_id(self, id: int, data: dict) -> T:
        """Updates an existing entity in the database."""
        entity = await self.get_by_id(id)
        return await self.update(entity=entity, data=data)

    async def update(self, entity: T, data: dict) -> T:
        for key, value in data.items():
            setattr(entity, key, value)
        try:
            await self.session.commit()
            await self.session.refresh(entity)
            return entity
        except Exception as e:
            logger.error(f"Error updating {self.entity_name}: {e}")
            await self.session.rollback()
            raise RepositoryError(str(e)) from e

    async def get_where(self, filter_data: dict) -> T | None:

        from pprint import pprint

        pprint(filter_data)
        query = select(self.model).filter_by(**filter_data)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
