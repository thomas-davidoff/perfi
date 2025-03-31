from datetime import date as dt
from decimal import Decimal
from uuid import UUID
from app.schemas import PerfiSchema, UuidMixinSchema, TimestampMixinSchema


class TransactionBaseSchema(PerfiSchema):
    account_id: UUID
    amount: Decimal
    description: str
    date: dt
    is_pending: bool = False
    notes: str | None = None
    category_id: UUID = None


class TransactionSchema(TransactionBaseSchema, UuidMixinSchema, TimestampMixinSchema):
    pass


class TransactionCreateSchema(TransactionBaseSchema):
    pass


class TransactionUpdateSchema(PerfiSchema):
    amount: Decimal | None = None
    description: str | None = None
    date: dt | None = None
    is_pending: bool | None = None
    notes: str | None = None
    category_id: UUID | None = None
