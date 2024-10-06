import pytest
from flask import Flask
from database import User
from app.repositories import UserRepository
from app.services import AuthService, create_auth_service

auth_service = create_auth_service()


def test_authenticate(app: Flask):
    with app.app_context():
        # returns user if existing user provides correct password
        user = auth_service.authenticate("moo_deng", "woof")
        assert isinstance(user, User)
        # it gets the right user
        assert user.username == "moo_deng"

        # returns None if existing user uses incorrect password
        assert auth_service.authenticate("moo_deng", "anjsdkjansd") is None

        # returns None if no user is found
        assert auth_service.authenticate("lakmsdlakmsd", "asdknasdn") is None
