from datetime import date as dt
from decimal import Decimal
from uuid import UUID
from app.schemas import PerfiSchema, UuidMixinSchema, TimestampMixinSchema


class DbTransactionBaseSchema(PerfiSchema):
    account_id: UUID
    amount: Decimal
    description: str
    date: dt
    is_pending: bool = False
    notes: str | None = None
    category_id: UUID = None


class DbTransactionSchema(
    DbTransactionBaseSchema, UuidMixinSchema, TimestampMixinSchema
):
    pass


class DbTransactionCreateSchema(DbTransactionBaseSchema):
    pass


class DbTransactionUpdateSchema(PerfiSchema):
    amount: Decimal | None = None
    description: str | None = None
    date: dt | None = None
    is_pending: bool | None = None
    notes: str | None = None
    category_id: UUID | None = None
