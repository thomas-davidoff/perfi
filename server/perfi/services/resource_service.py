from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Type, TypeVar, Generic
from abc import ABC, abstractmethod


T = TypeVar("T")


class ResourceService(ABC, Generic[T]):
    def __init__(self):
        pass

    @abstractmethod
    async def fetch_by_id(self, resource_id: UUID) -> T:
        """
        Gets a generic resource by ID
        """
        pass
