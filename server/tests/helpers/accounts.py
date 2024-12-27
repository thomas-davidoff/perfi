from database import Account, User
from typing import Literal
from .factory import TestFactory


choices = Literal["valid", "invalid_account_type", "missing_name"]


class AccountFactory(TestFactory):
    def __init__(self, db_session, user: User):
        super().__init__(db_session)
        self.user_id = user.id
        self.user = user

    def get(self, variant: choices = "valid") -> dict:

        return getattr(self, f"_{variant}")()

    def create(self, variant: choices = "valid") -> Account:

        a = Account(**self.get(variant))
        self.session.add(a)
        self.session.commit()
        return a

    def _valid(self) -> dict:
        return {
            "name": "Some Account name",
            "balance": 100,
            "account_type": "CHECKING",
            "user_id": self.user_id,
        }

    def _invalid_account_type(self) -> dict:
        a = self._valid()
        a["account_type"] = "NOT A REAL TYPE"
        return a

    def _missing_name(self) -> dict:
        a = self._valid()
        del a["name"]
        return a
