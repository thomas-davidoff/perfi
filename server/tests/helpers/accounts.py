from database import Account
from datetime import datetime, timedelta
from random import randint, uniform
from typing import Literal, List
from extensions import db


choices = Literal["valid", "invalid_account_type", "missing_name"]


class AccountFactory:
    def __init__(self):
        pass

    def get(self, variant: choices = "valid") -> dict:
        return getattr(self, f"_{variant}")()

    def create(self, variant: choices = "valid") -> Account:
        a = Account(**self.get(variant))
        db.session.add(a)
        db.session.commit()
        return a

    def _valid(self) -> dict:
        return {
            "name": "Some Account name",
            "balance": 100,
            "account_type": "CHECKING",
        }

    def _invalid_account_type(self) -> dict:
        a = self._valid()
        a["account_type"] = "NOT A REAL TYPE"
        return a

    def _missing_name(self) -> dict:
        a = self._valid()
        del a["name"]
        return a
