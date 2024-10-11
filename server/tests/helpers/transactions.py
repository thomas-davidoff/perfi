from database import Transaction
from datetime import datetime, timedelta
from random import randint, uniform
from typing import Literal, List
from extensions import db


def random_date():
    year = 2024
    month = 12

    max_day = (
        datetime(year + 1, 1, 1)
        if month == 12
        else datetime(year, month + 1, 1) - timedelta(days=1)
    )
    day = randint(1, max_day.day)
    return datetime(year, month, day)


choices = Literal["valid", "invalid_date", "missing_amount", "invalid_category"]


class TransactionFactory:
    def __init__(self):
        pass

    def get(self, variant: choices = "valid") -> dict:
        return getattr(self, f"_{variant}")()

    def create(self, variant: choices = "valid") -> Transaction:
        t = Transaction(**self.get(variant))
        db.session.add(t)
        db.session.commit()
        return t

    def bulk_create(self, variants: List[choices] = None) -> List[Transaction]:
        transactions = []
        for v in variants:
            t = Transaction(**self.get(variant=v))
            db.session.add(t)
            transactions.append(t)
        db.session.commit()
        return transactions

    def _valid(self) -> dict:
        return {
            "amount": round(uniform(5, 250), 2),
            "date": random_date(),
            "merchant": "TEST MERCHANT",
            "category": "UNCATEGORIZED",
        }

    def _invalid_date(self) -> dict:
        return {**self._valid(), **{"date": "2024-01-40"}}

    def _invalid_category(self) -> dict:
        return {**self._valid(), **{"category": "NOT A REAL CATEGORY"}}

    def _missing_amount(self) -> dict:
        t = self._valid()
        del t["amount"]
        return t
