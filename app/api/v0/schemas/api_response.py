from typing import Generic, TypeVar
from pydantic import BaseModel
from app.schemas import PerfiSchema
from app.models import PerfiModel

T = TypeVar("T")


class ApiResponse(PerfiSchema, Generic[T]):
    """Standard API response wrapper"""

    data: T
