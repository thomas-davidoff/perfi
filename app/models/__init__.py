from typing import TypeAlias
from pydantic import BaseModel

from db.model import Base

PerfiSchema: TypeAlias = BaseModel
PerfiModel: TypeAlias = Base

# import concrete models
from .user import User, UserSchema, UserCreateSchema, UserUpdateSchema
from .refresh_token import (
    RefreshToken,
    RefreshTokenSchema,
    RefreshTokenCreateSchema,
    RefreshTokenUpdateSchema,
)
from .account import (
    Account,
    AccountType,
    AccountSchema,
    AccountCreateSchema,
    AccountUpdateSchema,
)
from .transaction import (
    Transaction,
    TransactionSchema,
    TransactionCreateSchema,
    TransactionUpdateSchema,
)
from .category import (
    Category,
    CategoryType,
    CategorySchema,
    CategoryCreateSchema,
    CategoryUpdateSchema,
)
