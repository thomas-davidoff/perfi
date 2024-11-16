import pytest
from flask.testing import FlaskClient
import os
from initializers import load_env, load_configuration, get_logger
from tests.helpers import TransactionFactory, AccountFactory, UserFactory
from extensions import db
import psycopg
import time
import docker
import uuid
from database import Account, User

environment = "testing"

DB_CONFIG = {
    "dbname": "testdb",
    "user": "testuser",
    "password": "mysecretpassword",
    "host": "localhost",
}


def is_postgres_available(db_config):
    db_config = db_config.copy()
    connection_string = (
        f"postgresql://{db_config['user']}:{db_config['password']}"
        f"@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
    )
    try:
        with psycopg.connect(connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return True
    except psycopg.OperationalError as e:
        print(f"OperationalError: {e}")
        return False


def pytest_configure():
    load_env(f".env")
    load_env(f".env.{environment}")


@pytest.fixture(scope="function", autouse=True)
def config(postgresql_container):
    environment = "testing"

    test_db_config = postgresql_container

    connection_string = (
        f"postgresql://{test_db_config['user']}:{test_db_config['password']}"
        f"@{test_db_config['host']}:{test_db_config['port']}/{test_db_config['dbname']}"
    )

    os.environ["DATABASE_URI"] = connection_string
    configuration = load_configuration(environment)
    return configuration


@pytest.fixture(scope="session")
def postgresql_container():
    unique_container_name = f"test-postgres-{uuid.uuid4()}"

    client = docker.from_env()
    container = client.containers.run(
        image="postgres:17",
        name=unique_container_name,
        ports={"5432/tcp": None},
        environment={
            "POSTGRES_USER": DB_CONFIG["user"],
            "POSTGRES_PASSWORD": DB_CONFIG["password"],
            "POSTGRES_DB": DB_CONFIG["dbname"],
        },
        detach=True,
        tmpfs={"/var/lib/postgresql/data": "rw"},
    )

    host_port = wait_for_port_mapping(container)

    test_db_config = DB_CONFIG.copy()
    test_db_config["port"] = host_port

    timeout = 30
    start = time.time()
    while not is_postgres_available(db_config=test_db_config):
        time.sleep(0.1)
        if time.time() - start > timeout:
            logs = container.logs().decode("utf-8")
            print(f"Container logs:\n{logs}")
            raise TimeoutError("Postgres database did not start in time")

    try:
        yield test_db_config
    finally:
        container.stop()
        container.remove()


def wait_for_port_mapping(container, timeout=30):
    start_time = time.time()
    while True:
        container.reload()
        port_info = container.attrs["NetworkSettings"]["Ports"]
        if (
            port_info
            and port_info.get("5432/tcp")
            and port_info["5432/tcp"][0].get("HostPort")
        ):
            return port_info["5432/tcp"][0]["HostPort"]
        if time.time() - start_time > timeout:
            logs = container.logs().decode("utf-8")
            print(f"Container logs:\n{logs}")
            raise Exception("Timed out waiting for port mapping from Docker container.")
        time.sleep(0.1)


@pytest.fixture
def logger():
    import logging
    import sys

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)

    testing_logger = logging.getLogger("test_logger")

    yield testing_logger

    root.removeHandler(handler)


@pytest.fixture
def app(logger, config):

    from app import create_app

    app = create_app(config, logger)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app) -> FlaskClient:
    return app.test_client()


@pytest.fixture()
def transaction_factory():
    return TransactionFactory()


@pytest.fixture
def account_factory():
    return AccountFactory()


@pytest.fixture
def user_factory():
    return UserFactory()


@pytest.fixture
def valid_user(user_factory):
    return user_factory.create("valid")


@pytest.fixture
def auth_headers(valid_user, client):
    # log the user in to get an auth token
    headers = {"Content-type": "application/json", "Accept": "application/json"}
    r = client.post(
        "/auth/login",
        json={
            "username": valid_user.username,
            "password": os.environ["DB_SEEDS_PASSWORD"],
        },
        headers=headers,
    )
    headers["Authorization"] = f"Bearer {r.json['access_token']}"
    return headers
