import os
import sys
import pytest
from flask import Flask
from database import User
from app.repositories import UserRepository
from sqlalchemy.exc import IntegrityError, NoResultFound
from tests.helpers.helpers import add_valid_user, add_valid_users


user_repository = UserRepository()


def test_get_by_username_or_email(app: Flask):
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
    n_users = 3
    add_valid_users(n_users)
    # it successfully gets all users
    users = user_repository.get_all()
    assert isinstance(users, list)
    assert len(users) == n_users
    assert all([isinstance(u, User) for u in users])


def test_create(app: Flask):
    # it successfully creates a user with correct data
    user = {"username": "test", "password": "test", "email": "test@test.com"}
    user = user_repository.create(user)

    assert isinstance(user, User)
    assert user.username == "test"


def test_create_duplicate_username(app: Flask, valid_user):
    new_user = {
        "username": valid_user.username,
        "password": "test",
        "email": "test@test.com",
    }
    with pytest.raises(IntegrityError):
        user_repository.create(new_user)


def test_create_duplicate_email(app: Flask, valid_user):
    new_user = {"username": "test", "password": "test", "email": valid_user.email}
    with pytest.raises(IntegrityError):
        user_repository.create(new_user)


def test_delete(app: Flask):
    # create test user
    user = {"username": "test", "password": "test", "email": "test@test.com"}
    user = user_repository.create(user)

    # it successfully deletes the user
    user_repository.delete(user.id)

    with pytest.raises(NoResultFound):
        user_repository.get_by_id(user.id)

    # it fails to delete a non-existent id
    with pytest.raises(NoResultFound):
        user_repository.delete(999)


def test_update(app: Flask):
    with pytest.raises(NotImplementedError):
        user_repository.update(100, "data")
