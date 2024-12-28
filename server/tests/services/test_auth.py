from flask import Flask
from database import User
from perfi.services import create_auth_service
import os

auth_service = create_auth_service()
TEST_PASSWORD = os.environ.get("TEST_PASSWORD")


def test_authenticate_correct_username_incorrect_password(app: Flask, user_factory):
    u = user_factory.create("valid")
    user = auth_service.authenticate(u.username, "not a password")
    assert not user


def test_authenticate_no_user(app: Flask):
    user = auth_service.authenticate("username", "not a password")
    assert not user


def test_authenticate_success(app: Flask, user_factory):
    u = user_factory.create("valid")
    user = auth_service.authenticate(u.username, os.environ["DB_SEEDS_PASSWORD"])
    assert isinstance(user, User)
