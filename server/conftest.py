import pytest
from extensions import db
from flask.testing import FlaskClient
from random import uniform
from datetime import datetime
from database import Transaction
from tests.helpers.helpers import add_valid_user
import os
from initializers import load_env, load_configuration, get_logger

environment = "testing"


def pytest_configure():
    load_env(".env")
    load_env(f".env.{environment}")


@pytest.fixture(scope="session", autouse=True)
def config():
    """Fixture that loads environment variables before any tests are run."""

    environment = "testing"
    configuration = load_configuration(environment)
    return configuration


@pytest.fixture
def app(config):

    from app import create_app

    init_logger = get_logger(logger_name="poo", log_level="CRITICAL")

    app = create_app(config, init_logger)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app) -> FlaskClient:
    return app.test_client()


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
