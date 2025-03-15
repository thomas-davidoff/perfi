from typing import TypeAlias
from pydantic import BaseModel

from db.model import Base

PerfiSchema: TypeAlias = BaseModel
PerfiModel: TypeAlias = Base

# import concrete models
from .refresh_token import RefreshToken
from .user import User, UserCreateSchema, UserSchema, UserUpdateSchema
from .account import Account, AccountType
from .transaction import Transaction
from .category import Category, CategoryType
