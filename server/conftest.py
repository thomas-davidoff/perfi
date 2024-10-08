# conftest.py

import pytest
from extensions import db
from flask.testing import FlaskClient
from random import uniform
from datetime import datetime
from database import User, Transaction
from tests.helpers.helpers import add_valid_user
import os


@pytest.fixture
def app():
    from app import create_app

    app = create_app()

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app) -> FlaskClient:
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture()
def valid_transaction():
    return Transaction(
        amount=round(uniform(5, 150), 2),
        date=datetime(2024, 10, 7),
        merchant="test_merchant",
        category="UNCATEGORIZED",
    )


@pytest.fixture()
def valid_user():
    return add_valid_user(password=os.environ["TEST_PASSWORD"])
