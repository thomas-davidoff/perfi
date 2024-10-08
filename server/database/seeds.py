# database/seeds.py

from .models import User, Transaction
from extensions import db
import json
import os
from datetime import datetime


def load_seed_file(path):
    cur_file = os.path.dirname(os.path.abspath(__file__))
    fp = os.path.join(cur_file, path)
    with open(fp, "r") as f:
        return json.load(f)


def seed_all():
    seed_users()
    seed_transactions()


def unseed_all():
    unseed_users()
    unseed_transactions()


def seed_users():
    users_data = load_seed_file("seed_data/users.json")
    for user in users_data:
        # check for each individual user like a toddler, because i cant bother vectorizing it
        exists = User.query.filter_by(username=user["username"]).first()
        if not exists:
            user = {**user, **{"password": os.environ["DB_SEEDS_PASSWORD"]}}
            new_user = User(**user)
            db.session.add(new_user)

    db.session.commit()
    print("Seeded users successfully.")


def unseed_users():
    users_data = load_seed_file("seed_data/users.json")

    for user in users_data:
        exists = User.query.filter_by(username=user["username"]).first()
        if exists:
            db.session.delete(exists)

        db.session.commit()
        print("Unseeded users successfully.")


def seed_transactions():
    transactions_data = load_seed_file("seed_data/transactions.json")
    for transaction in transactions_data:
        sqlite_safe_transaction = {**transaction, **{"date": datetime(2020, 10, 3)}}
        new_transaction = Transaction(**sqlite_safe_transaction)
        db.session.add(new_transaction)

    db.session.commit()
    print("Seeded transactions successfully.")


def unseed_transactions():
    pass
