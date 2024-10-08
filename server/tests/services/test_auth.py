from flask import Flask
from database import User
from app.services import create_auth_service
from tests.helpers.helpers import add_valid_user
import os

auth_service = create_auth_service()
TEST_PASSWORD = os.environ.get("TEST_PASSWORD")


def test_authenticate_correct_username_incorrect_password(app: Flask):
    u = add_valid_user(password=TEST_PASSWORD)
    user = auth_service.authenticate(u.username, "not a password")
    assert not user


def test_authenticate_no_user(app: Flask):
    user = auth_service.authenticate("username", "not a password")
    assert not user


def test_authenticate_correct_username(app: Flask):
    u = add_valid_user(password=TEST_PASSWORD)
    user = auth_service.authenticate(u.username, TEST_PASSWORD)
    assert user.username == u.username


def test_authenticate_success(app: Flask):
    u = add_valid_user(password=TEST_PASSWORD)
    user = auth_service.authenticate(u.username, TEST_PASSWORD)
    assert isinstance(user, User)
