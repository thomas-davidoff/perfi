from flask import Flask
from database import User
from app.services import create_user_service
from extensions import db
from tests.helpers import UserFactory
import pytest

user_service = create_user_service()


def test_register_returns_user_instance(app: Flask, user_factory):
    user_data = user_factory.get("valid")
    u = user_service.register(**user_data)
    assert isinstance(u, User)


def test_register_adds_user_to_database(app: Flask, user_factory):
    user_data = user_factory.get("valid")
    u = user_service.register(**user_data)

    user = db.session.get(User, u.id)
    assert user


def test_register_fails_simple_password(app: Flask, user_factory: UserFactory):
    user_data = user_factory.get("simple_password")

    # TODO: Add password complexity exception (or just find a better one)
    with pytest.raises(ValueError):
        user_service.register(**user_data)
