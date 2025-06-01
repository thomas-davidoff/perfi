from typing import TypeAlias
from pydantic import BaseModel

from db.model import Base


PerfiModel: TypeAlias = Base

# import concrete models
from .user import User
from .refresh_token import RefreshToken
from .account import Account, AccountType
from .transaction import Transaction
from .category import Category, CategoryType
