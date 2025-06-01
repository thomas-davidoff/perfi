from typing import Generic, TypeVar
from pydantic import BaseModel
from app.schemas import PerfiSchema
from app.models import PerfiModel

T = TypeVar("T")


class ApiResponse(PerfiSchema, Generic[T]):
    """Standard API response wrapper"""

    data: T


from app.schemas.transaction import DbTransactionSchema
from app.schemas.account import DbAccountSchema

# Type aliases for common responses
SingleTransactionResponse = ApiResponse[DbTransactionSchema]
ListTransactionResponse = ApiResponse[list[DbTransactionSchema]]

SingleAccountResponse = ApiResponse[DbAccountSchema]
ListAccountResponse = ApiResponse[list[DbAccountSchema]]
