from database import User
from datetime import datetime, timedelta
from random import randint, uniform
from typing import Literal, List
from extensions import db
import string
import random
import os


choices = Literal["valid"]


def generate_random_credentials():
    username = "".join(random.choices(string.ascii_lowercase, k=10))

    return {
        "username": username,
        "password": os.environ["DB_SEEDS_PASSWORD"],
        "email": "".join(random.choices(string.ascii_lowercase, k=10)),
    }


class UserFactory:
    def __init__(self):
        pass

    def get(self, variant: choices = "valid") -> dict:
        return getattr(self, f"_{variant}")()

    def create(self, variant: choices = "valid") -> User:
        u = User(**self.get(variant))
        db.session.add(u)
        db.session.commit()
        return u

    def _valid(self) -> dict:
        return generate_random_credentials()

    def bulk_create(self, variants: List[choices] = None) -> List[User]:
        transactions = []
        for v in variants:
            u = User(**self.get(variant=v))
            db.session.add(u)
            transactions.append(u)
        db.session.commit()
        return transactions
