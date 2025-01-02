from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
)
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime
from perfi.core.utils import CaseInsensitiveEnum, StandardDate
from perfi.core.exc import ValidationError as CustomValidationError
from .generics import Record
from .account import AccountCompact
from enum import Enum


class TransactionFields(str, Enum):
    DATE = "date"
    CATEGORY = "category"
    DESCRIPTION = "description"
    MERCHANT = "merchant"
    AMOUNT = "amount"
    ACCOUNT_ID = "account_id"


class TransactionCategory(CaseInsensitiveEnum):
    GROCERIES = "GROCERIES"
    UTILITIES = "UTILITIES"
    ENTERTAINMENT = "ENTERTAINMENT"
    TRANSPORTATION = "TRANSPORTATION"
    INCOME = "INCOME"
    OTHER = "OTHER"
    HOUSING = "HOUSING"
    UNCATEGORIZED = "UNCATEGORIZED"


class CategoriesResponse(BaseModel):
    """
    A list of categories.
    """

    data: List[str]


class Transaction(Record):
    """
    A serialized transaction.
    """

    amount: float
    description: Optional[str] = None
    merchant: str
    date: datetime
    category: Optional[str] = Field(...)
    account: AccountCompact

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("category", when_used="always")
    def capitalize_category(self, category: str):
        return category.capitalize()

    @field_serializer("date", when_used="always")
    def format_date(self, date: datetime):
        return date.strftime("%Y-%m-%d")

    @field_serializer("amount", when_used="always")
    def format_as_currency(self, amount: float):
        """
        Converts an amount float to a standard currency number, e.g. $123.45
        """
        # TODO: Eventually, handle other currencies.
        return f"${amount:.2f}"


class TransactionRequest(BaseModel):
    """
    Generic transaction requests schema.
    """

    amount: float = Field(default=0.0, ge=-10000)
    description: str = Field(..., max_length=255)
    merchant: str = Field(..., max_length=100)
    date: str
    account_id: UUID
    category: TransactionCategory

    @field_validator("date", mode="before")
    def ensure_correct_date_format(cls, date: str):
        for format in StandardDate.SUPPORTED_FORMATS:
            try:
                return datetime.strptime(date, format).strftime("%Y-%m-%d")
            except Exception as e:
                raise CustomValidationError(
                    "date must be a valid date in one of the supported formats: "
                    f'{", ".join(StandardDate.SUPPORTED_FORMATS)}'
                ) from e

    @field_validator("category", mode="before")
    def coerce_invalid_category(cls, value):
        try:
            return TransactionCategory(value.upper())
        except (ValueError, AttributeError):
            return TransactionCategory.UNCATEGORIZED

    @field_serializer("date", when_used="always")
    def convert_to_datetime(self, date: str):
        return StandardDate(date).date

    @classmethod
    def field_aliases(cls) -> Dict[str, TransactionFields]:
        """
        Map internal field names to their corresponding TransactionFields.
        """
        return {
            "amount": TransactionFields.AMOUNT,
            "description": TransactionFields.DESCRIPTION,
            "merchant": TransactionFields.MERCHANT,
            "date": TransactionFields.DATE,
            "account_id": TransactionFields.ACCOUNT_ID,
            "category": TransactionFields.CATEGORY,
        }

    @classmethod
    def required_fields(cls) -> List[str]:
        """
        Return a list of required fields for the model.
        """
        return set(
            [
                field_name
                for field_name, field in cls.model_fields.items()
                if field.default is ... or field.default_factory is None
            ]
        )


class TransactionCreateRequest(TransactionRequest):
    """
    Schema for creating a new transaction.
    """


class TransactionUpdateRequest(TransactionRequest):
    """
    Schema for updating an existing transaction.
    """

    amount: Optional[float] = Field(default=None, ge=-10000)
    description: Optional[str] = Field(default=None, max_length=255)
    merchant: Optional[str] = Field(default=None, max_length=50)
    date: Optional[str] = Field(default=None)
    account_id: Optional[UUID] = Field(default=None)
    category: Optional[TransactionCategory] = Field(default=None)
