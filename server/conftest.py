import pytest
import time
import docker
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from perfi.core.database import Base
from perfi.core.dependencies.settings import get_settings, Settings


DB_IMAGE = "postgres:17"


@pytest.fixture(scope="session", autouse=True)
def settings() -> Settings:
    return get_settings()


# Utility to wait for PostgreSQL to be ready
def wait_for_postgres(db_config, timeout=30):
    start_time = time.time()
    while True:
        try:
            from psycopg2 import connect

            connection_string = (
                f"postgresql://{db_config['user']}:{db_config['password']}"
                f"@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
            )
            with connect(connection_string) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
            return True
        except Exception:
            if time.time() - start_time > timeout:
                raise TimeoutError("Postgres did not start in time.")
            time.sleep(0.1)


def wait_for_port_mapping(container, container_port_protocol, timeout=30):
    start_time = time.time()
    while True:
        container.reload()
        port_info = container.attrs["NetworkSettings"]["Ports"]
        if (
            port_info
            and port_info.get(container_port_protocol)
            and port_info[container_port_protocol][0].get("HostPort")
        ):
            return port_info[container_port_protocol][0]["HostPort"]
        if time.time() - start_time > timeout:
            logs = container.logs().decode("utf-8")
            print(f"Container logs:\n{logs}")
            raise Exception("Timed out waiting for port mapping from Docker container.")
        time.sleep(0.1)


@pytest.fixture(scope="session", autouse=True)
def postgresql_container(db_config_from_settings):
    """Spin up a Docker container for PostgreSQL."""
    client = docker.from_env()
    container_name = f"test-postgres-{uuid.uuid4()}"

    container_port_protocol = f"{db_config_from_settings['port']}/tcp"

    container = client.containers.run(
        image=DB_IMAGE,
        name=container_name,
        ports={container_port_protocol: None},
        environment={
            "POSTGRES_USER": db_config_from_settings["user"],
            "POSTGRES_PASSWORD": db_config_from_settings["password"],
            "POSTGRES_DB": db_config_from_settings["dbname"],
        },
        detach=True,
        tmpfs={"/var/lib/postgresql/data": "rw"},
        command=f"-p {db_config_from_settings['port']}",
    )

    # Get mapped host port
    container.reload()

    host_port = wait_for_port_mapping(
        container, container_port_protocol=container_port_protocol
    )

    db_config_from_settings["port"] = host_port
    wait_for_postgres(db_config_from_settings)

    yield db_config_from_settings

    container.stop()
    container.remove()


# === Test Database Session Management ===


@asynccontextmanager
async def get_test_db(database_url):
    """
    Provide a test database session. Rolls back after each use.
    """
    engine = create_async_engine(database_url, echo=False)
    TestSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="session")
def db_config_from_settings(settings):
    return {
        "dbname": settings.DB_NAME,
        "user": settings.DB_USER,
        "password": settings.DB_PASS,
        "host": settings.DB_HOST,
        "port": settings.DB_PORT,
    }


@pytest.fixture(scope="session")
def test_database_url(postgresql_container, db_config_from_settings):
    """Generate the test database URL from the container config."""
    return (
        f"postgresql+asyncpg://{postgresql_container['user']}:{postgresql_container['password']}"
        f"@{postgresql_container['host']}:{postgresql_container['port']}/{postgresql_container['dbname']}"
    )


async def get_test_db(database_url):
    """
    Provide an async test database session. Rolls back after each use.
    """
    engine = create_async_engine(
        database_url,
        echo=False,
        future=True,
    )
    TestSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="session")
async def test_db(test_database_url):
    """
    Initialize the test database by creating tables.
    """
    async with get_test_db(test_database_url) as session:
        yield session


@pytest.fixture
async def db_session(test_database_url):
    """
    Provide a transactional database session for each test.
    """
    async for session in get_test_db(test_database_url):
        yield session
