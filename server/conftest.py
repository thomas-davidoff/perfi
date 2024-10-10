import pytest
from extensions import db
from flask.testing import FlaskClient
from tests.helpers.helpers import add_valid_user
import os
from initializers import load_env, load_configuration, get_logger

from tests.helpers import TransactionFactory

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
def valid_user():
    return add_valid_user(password=os.environ["TEST_PASSWORD"])


@pytest.fixture()
def transaction_factory():
    return TransactionFactory()
