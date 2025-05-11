from decimal import Decimal
from uuid import UUID
from app.models import AccountType
from app.schemas import PerfiSchema, UuidMixinSchema, TimestampMixinSchema


class DbAccountBaseSchema(PerfiSchema):
    name: str
    account_type: AccountType
    balance: Decimal = Decimal("0.00")
    institution: str | None = None
    description: str | None = None
    is_active: bool = True


class DbAccountSchema(DbAccountBaseSchema, UuidMixinSchema, TimestampMixinSchema):
    user_id: UUID


class DbAccountCreateSchema(DbAccountBaseSchema):
    user_id: UUID


class DbAccountUpdateSchema(PerfiSchema):
    name: str | None = None
    account_type: AccountType | None = None
    balance: Decimal | None = None
    institution: str | None = None
    description: str | None = None
    is_active: bool | None = None
