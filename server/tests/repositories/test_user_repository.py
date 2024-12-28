import pytest
from flask import Flask
from database import User
from perfi.repositories import UserRepository
from sqlalchemy.exc import IntegrityError
import uuid
from perfi.exceptions import ResourceNotFoundError


user_repository = UserRepository()


def test_get_by_username_or_email(app: Flask, user_factory):
    # successfully returns user by username
    # remember to seed data

    u = user_factory.create("valid")

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


def test_get_all(app: Flask, user_factory):

    n_users = 3

    users = user_factory.bulk_create(["valid"] * n_users)
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


def test_create_duplicate_username(app: Flask, user_factory):
    user = user_factory.create("valid")
    u = user_factory.get("valid")
    u["username"] = user.username
    with pytest.raises(IntegrityError):
        user_repository.create(u)


def test_create_duplicate_email(app: Flask, user_factory):
    user = user_factory.create("valid")
    u = user_factory.get("valid")
    u["email"] = user.email
    with pytest.raises(IntegrityError):
        user_repository.create(u)


def test_delete(app: Flask, user_factory):
    user = user_factory.create("valid")

    # it successfully deletes the user
    user_repository.delete(user.id)

    user = user_repository.get_by_id(user.id)
    assert user is None

    # it fails to delete a non-existent id
    with pytest.raises(ResourceNotFoundError):
        user_repository.delete(uuid.uuid4())


def test_update(app: Flask, user_factory):
    user = user_factory.create("valid")
    with pytest.raises(NotImplementedError):
        user_repository.update(user.id, {"username": "test"})
