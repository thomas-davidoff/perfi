from database import User
from datetime import datetime, timedelta
from random import randint, uniform
from typing import Literal, List
from extensions import db
import string
import random


choices = Literal["valid"]


def generate_random_credentials():
    username = "".join(random.choices(string.ascii_lowercase, k=10))

    password = "".join(
        random.choices(string.ascii_letters + string.digits + string.punctuation, k=12)
    )
    return {"username": username, "password": password}


class UserFactory:
    def __init__(self):
        pass

    def get(self, variant: choices = "valid") -> dict:
        return getattr(self, f"_{variant}")()

    def create(self, variant: choices = "valid") -> User:
        a = User(**self.get(variant))
        db.session.add(a)
        db.session.commit()
        return a

    def _valid(self) -> dict:
        return generate_random_credentials()
