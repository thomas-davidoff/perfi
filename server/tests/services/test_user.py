from flask import Flask
from database import User
from perfi.services import create_user_service
from extensions import db
from tests.helpers import UserFactory
import pytest
from perfi.exceptions import PasswordTooSimpleError

user_service = create_user_service()


def test_register_returns_user_instance(app: Flask, user_factory):
    user_data = user_factory.get("valid")
    u = user_service.create_user(**user_data)
    assert isinstance(u, User)


def test_register_adds_user_to_database(app: Flask, user_factory):
    user_data = user_factory.get("valid")
    u = user_service.create_user(**user_data)

    user = db.session.get(User, u.id)
    assert user


def test_register_fails_simple_password(app: Flask, user_factory: UserFactory):
    user_data = user_factory.get("simple_password")

    # TODO: Add password complexity exception (or just find a better one)
    with pytest.raises(PasswordTooSimpleError):
        user_service.create_user(**user_data)


@pytest.mark.parametrize(
    "email_address",
    [
        "test@example.com",
        "test@example.exmasd.com",
        "something@something.net",
        "secret@secretsomething.net",
        "ONSODN@OINASD.SH",
    ],
)
def test_validate_email_address_success(email_address):
    assert user_service._validate_email(email_address)


@pytest.mark.parametrize(
    "email_address",
    ["asjdn", 1233, "lkasdmd@asldkmasd", "kjnasd@aksnd.com@"],
)
def test_validate_email_address_fail(email_address):
    assert not user_service._validate_email(email_address)


@pytest.mark.parametrize(
    "username",
    ["kajnsdjansd", "something", "OINoON"],
)
def test_validate_username_success(username):
    assert user_service._validate_username(username)


@pytest.mark.parametrize(
    "username",
    ["abc", 123, user_service, "oinasdsdoinasdoin"],
)
def test_validate_username_fail(username):
    assert not user_service._validate_username(username)


@pytest.mark.parametrize(
    "password",
    ["aisdnins"],
)
def test_validate_password_complexity_success(password):
    assert not user_service._validate_password_complexity(password)
