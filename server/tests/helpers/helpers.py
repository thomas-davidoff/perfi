from extensions import db
from database import User
from random import choice
from string import ascii_lowercase


def random_string(length=10):
    return "".join(choice(ascii_lowercase) for i in range(length))


def add_valid_user(password=None):
    password = password or random_string()
    user = User(
        username=random_string(),
        password=password,
        email=f"{random_string()}@example.com",
    )
    db.session.add(user)
    db.session.commit()
    return user


def add_valid_users(n_users=3):
    i = 0
    while i < n_users:
        add_valid_user()
        i += 1
