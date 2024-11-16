from database import Account, User
from datetime import datetime, timedelta
from random import randint, uniform
from typing import Literal, List
from extensions import db
from .users import UserFactory
from .factory import TestFactory


choices = Literal["valid", "invalid_account_type", "missing_name"]


class AccountFactory(TestFactory):
    def __init__(self, db_session):
        super().__init__(db_session)

    def get(self, variant: choices = "valid") -> dict:

        return getattr(self, f"_{variant}")()

    def create(self, variant: choices = "valid") -> Account:

        a = Account(**self.get(variant))
        self.session.add(a)
        self.session.commit()
        return a

    def _valid(self) -> dict:
        user = self.session.query(User).first()
        if not user:
            user_factory = UserFactory(self.session)
            user_factory.create("valid")
        return {
            "name": "Some Account name",
            "balance": 100,
            "account_type": "CHECKING",
            "user_id": self.session.query(User).first().id,
        }

    def _invalid_account_type(self) -> dict:
        a = self._valid()
        a["account_type"] = "NOT A REAL TYPE"
        return a

    def _missing_name(self) -> dict:
        a = self._valid()
        del a["name"]
        return a
