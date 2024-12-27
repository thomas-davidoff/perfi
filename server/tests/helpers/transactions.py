from database import Transaction, TransactionCategory
from datetime import datetime, timedelta
from random import randint, uniform
from typing import Literal, List
from .factory import TestFactory


def random_date():
    year = 2024
    month = 12

    max_day = (
        datetime(year + 1, 1, 1)
        if month == 12
        else datetime(year, month + 1, 1) - timedelta(days=1)
    )
    day = randint(1, max_day.day)
    return datetime(year, month, day).strftime("%Y-%m-%d")


choices = Literal[
    "valid", "invalid_date", "missing_amount", "invalid_category", "missing_account_id"
]


class TransactionFactory(TestFactory):
    def __init__(self, db_session, account_id: int, user_id):
        print(f"init factory with session {db_session}")
        super().__init__(db_session)
        self.account_id = account_id
        self.user_id = user_id

    def get(self, variant: choices = "valid") -> dict:
        return getattr(self, f"_{variant}")()

    def create(self, variant: choices = "valid") -> Transaction:
        t = Transaction(**self.get(variant))
        self.session.add(t)
        self.session.commit()
        self.session.refresh(t)
        from sqlalchemy.orm import object_session

        assert object_session(t) is not None, "Transaction is not bound to a session"
        print(f"object session: {object_session(t)}")
        return t

    def bulk_create(self, variants: List[choices] = None) -> List[Transaction]:
        transactions = []
        for v in variants:
            t = Transaction(**self.get(variant=v))
            self.session.add(t)
            transactions.append(t)
        self.session.commit()
        return transactions

    def _valid(self) -> dict:
        return {
            "amount": round(uniform(5, 250), 2),
            "date": random_date(),
            "merchant": "TEST MERCHANT",
            "category": TransactionCategory.UNCATEGORIZED.value.lower(),
            "account_id": self.account_id,
        }

    def _invalid_date(self) -> dict:
        return {**self._valid(), **{"date": "2024-01-40"}}

    def _invalid_category(self) -> dict:
        return {**self._valid(), **{"category": "NOT A REAL CATEGORY"}}

    def _missing_amount(self) -> dict:
        t = self._valid()
        del t["amount"]
        return t

    def _missing_account_id(self) -> dict:
        t = self._valid()
        del t["account_id"]
        return t
