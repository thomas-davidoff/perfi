from pydantic import BaseModel
from typing import List, Generic, TypeVar, Any
from pydantic import BaseModel, ConfigDict
from typing import List, Generic, TypeVar
from uuid import UUID
from datetime import datetime


T = TypeVar("T")


class GenericResponse(BaseModel, Generic[T]):
    """
    A generic response model for API responses.
    """

    data: List[T] | Any


class Record(BaseModel):
    """
    A serializer for the base mixin class.
    """

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
