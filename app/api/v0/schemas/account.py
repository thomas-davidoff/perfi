from decimal import Decimal

from pydantic import ConfigDict
from app.models.account import AccountType
from app.schemas import PerfiSchema
from app.api.v0.schemas.resource import ApiResourceCompact, ApiResourceFull
from app.api.v0.schemas.api_response import ApiResponse


class ApiAccountCreateRequest(PerfiSchema):
    """
    Almost the same as account create schema, but doesn't take a user id
    Users of the API should not provide a user_id directly as their identity is used instead.
    """

    name: str
    account_type: str
    balance: Decimal | None = Decimal("0")
    institution: str | None = None
    description: str | None = None
    is_active: bool | None = None


class ApiAccountCompactResponse(ApiResourceCompact):
    name: str
    account_type: AccountType


class ApiAccountFullResponse(ApiResourceFull, ApiAccountCompactResponse):
    balance: Decimal = Decimal("0.00")
    institution: str | None = None
    description: str | None = None
    is_active: bool = True


ApiSingleAccountResponse = ApiResponse[ApiAccountFullResponse]
ApiListAccountResponse = ApiResponse[list[ApiAccountFullResponse]]
