from decimal import Decimal
from app.schemas import PerfiSchema
from app.api.v0.schemas.resource import ApiResourceCompact, ApiResourceFull
from app.api.v0.schemas.api_response import ApiResponse
from uuid import UUID
from datetime import date


class ApiTransactionCreateRequest(PerfiSchema):
    """
    Almost the same as transaction create schema, but doesn't take a user id
    Users of the API should not provide a user_id directly as their identity is used instead.
    """

    account_id: UUID
    amount: Decimal
    description: str
    date: date
    is_pending: bool = False
    notes: str | None = None
    category_id: UUID | None = None


class DbTransactionUpdateSchema(PerfiSchema):
    pass


class ApiTransactionCompactResponse(ApiResourceCompact):
    pass


class ApiTransactionFullResponse(ApiResourceFull, ApiTransactionCompactResponse):
    pass


ApiSingletransactionResponse = ApiResponse[ApiTransactionFullResponse]
ApiListtransactionResponse = ApiResponse[list[ApiTransactionFullResponse]]
