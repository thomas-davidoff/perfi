from pydantic import BaseModel, ConfigDict, Field, model_serializer
from uuid import UUID
from .generics import Record
from typing import Optional, Dict, Any
import enum


class Account(Record):
    """
    A full serialized account.
    """

    name: str
    balance: float
    account_type: str
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)


class AccountCompact(Account):
    """
    A compact account record
    """

    @model_serializer
    def ser_model(self) -> Dict[str, Any]:
        return {"name": self.name, "id": self.id}


class AccountType(enum.Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT_CARD = "credit_card"


class AccountRequest(BaseModel):
    """
    Generic account schema
    """

    name: str = Field(..., max_length=255)
    balance: float = Field(default=0.0, ge=-10000000, le=10000000)
    account_type: AccountType


class AccountCreateRequest(AccountRequest):
    pass


class AccountUpdateRequest(AccountRequest):
    name: Optional[str] = Field(default=None, max_length=255)
    balance: Optional[float] = Field(default=None, ge=-10000000, le=10000000)
    account_type: Optional[AccountType] = Field(default=None)
