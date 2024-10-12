import pytest
from extensions import db
from flask.testing import FlaskClient
from tests.helpers.helpers import add_valid_user
import os
from initializers import load_env, load_configuration, get_logger

from tests.helpers import TransactionFactory
import pytest
from pytest_postgresql import factories
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from extensions import db
from initializers import load_env, load_configuration, get_logger
import psycopg
import time
import docker


environment = "testing"
DEFAULT_DATABASE_NAME = "postgres"

DB_CONFIG = {
    "dbname": "testdb",
    "user": "postgres",
    "password": "mysecretpassword",
    "host": "localhost",
    "port": 5432,
}

CONNECTION = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"


def is_postgres_available(db_name=None):
    db_config = DB_CONFIG.copy()
    db_config["dbname"] = db_name or DEFAULT_DATABASE_NAME
    try:
        with psycopg.connect(**db_config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            return True
    except psycopg.OperationalError:
        raise
        return False


postgresql_in_docker = factories.postgresql_noproc(
    host=DB_CONFIG["host"],
    port=DB_CONFIG["port"],
    password=DB_CONFIG["password"],
)

postgresql = factories.postgresql(
    "postgresql_in_docker",
    dbname=DB_CONFIG["dbname"],
)


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
def app(config, session):

    from app import create_app

    init_logger = get_logger(logger_name="poo", log_level="CRITICAL")

    app = create_app(config, init_logger)

    # Update app config with test database connection
    app.config.update({"SQLALCHEMY_DATABASE_URI": CONNECTION})

    with app.app_context():
        db.create_all()
        yield app

        session.rollback()
        db.drop_all()


@pytest.fixture()
def client(app) -> FlaskClient:
    return app.test_client()


@pytest.fixture()
def session(postgresql_connection):
    engine = create_engine(CONNECTION)

    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()


@pytest.fixture(scope="session")
def postgresql_container():
    client = docker.from_env()
    container = client.containers.run(
        image="postgres:12",
        auto_remove=True,
        name="test-postgres",
        ports={f"5432/tcp": DB_CONFIG["port"]},
        environment={"POSTGRES_PASSWORD": DB_CONFIG["password"]},
        detach=True,
        remove=True,
    )

    timeout = 10

    # Wait for the container to start
    start = time.time()
    while container.status != "running":
        container.reload()
        elapsed = time.time() - start
        if elapsed > timeout:
            raise TimeoutError("Postgres container did not start in time")

    # Wait for the database to be ready
    start = time.time()
    while not is_postgres_available():
        elapsed = time.time() - start
        if elapsed > timeout:
            raise TimeoutError("Postgres database did not start in time")

    try:
        yield container
    finally:
        container.stop()


@pytest.fixture()
def valid_user():
    return add_valid_user(password=os.environ["TEST_PASSWORD"])


@pytest.fixture()
def transaction_factory():
    return TransactionFactory()


@pytest.fixture()
def postgresql_connection(postgresql_container, postgresql):
    yield postgresql
