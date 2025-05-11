from typing import TypeAlias
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class PerfiSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UuidMixinSchema(PerfiSchema):
    uuid: UUID = None


class TimestampMixinSchema(PerfiSchema):
    created_at: datetime | None = None
    updated_at: datetime | None = None


from .user import UserCreateSchema, UserSchema, UserUpdateSchema
from .refresh_token import (
    RefreshTokenSchema,
    RefreshTokenCreateSchema,
    RefreshTokenUpdateSchema,
)
from .account import (
    AccountType,
    DbAccountSchema,
    DbAccountCreateSchema,
    DbAccountUpdateSchema,
)
from .transaction import (
    DbTransactionSchema,
    DbTransactionCreateSchema,
    DbTransactionUpdateSchema,
)
from .category import (
    CategoryType,
    CategorySchema,
    CategoryCreateSchema,
    CategoryUpdateSchema,
)
