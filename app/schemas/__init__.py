from typing import TypeAlias
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

PerfiSchema: TypeAlias = BaseModel


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
    AccountSchema,
    AccountCreateSchema,
    AccountUpdateSchema,
)
from .transaction import (
    TransactionSchema,
    TransactionCreateSchema,
    TransactionUpdateSchema,
)
from .category import (
    CategoryType,
    CategorySchema,
    CategoryCreateSchema,
    CategoryUpdateSchema,
)
