import os
import sys

print(os.getcwd())
print(sys.path)

import pytest
from flask import Flask
from database import User
from extensions import db
from app.repositories import UserRepository
from sqlalchemy.exc import IntegrityError, NoResultFound

from tests.helpers.helpers import add_valid_user, add_valid_users


user_repository = UserRepository()


def test_get_by_username_or_email(app: Flask):
    with app.app_context():
        # successfully returns user by username
        # remember to seed data

        # setup: add valid user
        u = add_valid_user()

        user = user_repository.get_by_username_or_email(u.username)
        assert isinstance(user, User)

        # does not return a non-existent user
        user = user_repository.get_by_username_or_email("NOT AN EXISTING USERNAME")
        assert user is None

        # successfully returns user by email
        user = user_repository.get_by_username_or_email(u.email)
        assert isinstance(user, User)

        # does not return a non-existent user by email
        user = user_repository.get_by_username_or_email("NOT AN EXISTING EMAIL")
        assert user is None


def test_get_all(app: Flask):
    with app.app_context():
        n_users = 3
        add_valid_users(n_users)
        # it successfully gets all users
        users = user_repository.get_all()
        assert isinstance(users, list)
        assert len(users) == n_users
        assert all([isinstance(u, User) for u in users])


def test_create(app: Flask):
    with app.app_context():
        # it successfully creates a user with correct data
        user = User(username="test", password="test", email="test@test.com")
        user = user_repository.create(user)

        assert isinstance(user, User)
        assert user.username == "test"


def test_create_duplicate_username(app: Flask, valid_user):
    with app.app_context():
        new_user = User(
            username=valid_user.username, password="test_pass", email="test@example.com"
        )
        with pytest.raises(IntegrityError):
            db.session.add(new_user)
            db.session.commit()


def test_create_duplicate_email(app: Flask, valid_user):
    with app.app_context():
        new_user = User(
            username="test username", password="test_pass", email=valid_user.email
        )
        with pytest.raises(IntegrityError):
            db.session.add(new_user)
            db.session.commit()


def test_delete(app: Flask):
    with app.app_context():
        # create test user
        user = User(username="test", password="test", email="test@test.com")
        user = user_repository.create(user)

        # it successfully deletes the user
        user_repository.delete(user.id)

        with pytest.raises(NoResultFound):
            user_repository.get_by_id(user.id)

        # it fails to delete a non-existent id
        with pytest.raises(NoResultFound):
            user_repository.delete(999)


def test_update(app: Flask):
    with app.app_context():
        with pytest.raises(NotImplementedError):
            user_repository.update(100, "data")
