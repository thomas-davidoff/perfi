from database.models.models import User
from .instance import db
import json
import os


def load_seed_file(path):
    cur_file = os.path.dirname(os.path.abspath(__file__))
    fp = os.path.join(cur_file, path)
    with open(fp, "r") as f:
        return json.load(f)


def seed_all():
    seed_users()


def unseed_all():
    unseed_users()


def seed_users():

    users_data = load_seed_file("seed_data/users.json")
    for user in users_data:
        # check for each individual user like a toddler, because i cant bother vectorizing it
        exists = User.query.filter_by(username=user["username"]).first()
        if not exists:
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
