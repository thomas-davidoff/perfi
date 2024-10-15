# database/seeds.py

from .models import User, Transaction, Account
from extensions import db
import json
import os
import uuid
from random import randint


def load_seed_file(seed):
    cur_file = os.path.dirname(os.path.abspath(__file__))
    fp = os.path.join(cur_file, f"seed_data/{seed}.json")
    with open(fp, "r") as f:
        return json.load(f)


def get_random_entity_id(entities):
    return entities[randint(0, len(entities) - 1)].id


def seed():
    for entity_type, model in {
        "users": User,
        "accounts": Account,
        "transactions": Transaction,
    }.items():
        data = load_seed_file(entity_type)
        for entity in data:
            try:
                if entity_type == "users":
                    entity = {**entity, "password": os.environ.get("DB_SEEDS_PASSWORD")}
                if entity_type == "transactions":
                    acx = db.session.query(Account).all()
                    entity = {**entity, "account_id": get_random_entity_id(acx)}
                if entity_type == "accounts":
                    usrs = db.session.query(User).all()
                    entity = {**entity, "user_id": get_random_entity_id(usrs)}
                e = model(**entity)
                db.session.add(e)
                db.session.commit()
            except:
                print(f"could not seed entity {entity_type} with data {entity}")
                raise
                continue

        print(f"Seeded {entity_type} successfully.")
