import os

# Set PERFI_ENV=test early on to correctly load test config, if one
# is provided. See: config/settings.py for implementation details
os.environ["PERFI_ENV"] = "test"

import pytest
from alembic.config import Config
from alembic import command
from db.session_manager import db_manager
import contextlib
import uuid
from typing import AsyncIterator
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.engine.url import URL as SQLAlchemyURL
from config.settings import settings


@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio", {"use_uvloop": True}


async def create_postgres_db(
    engine: AsyncEngine,
    database_name: str,
    encoding: str = "utf8",
    template: str = "template1",
) -> None:
    async with engine.begin() as conn:
        await conn.execute(
            sa.text(
                f'CREATE DATABASE "{database_name}" ENCODING \'{encoding}\' TEMPLATE "{template}"'
            )
        )


async def drop_postgres_db(engine: AsyncEngine, database_name: str) -> None:
    async with engine.begin() as conn:
        await conn.execute(
            sa.text(
                """
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = :database
                AND pid <> pg_backend_pid()
                """
            ).bindparams(database=database_name)
        )
        await conn.execute(sa.text(f'DROP DATABASE "{database_name}"'))


@pytest.fixture(scope="session")
async def postgres():
    """
    Creates empty temporary database.
    """
    async with tmp_postgres_db(suffix="pytest") as tmp_url:
        yield tmp_url


@contextlib.asynccontextmanager
async def tmp_postgres_db(
    suffix: str = "",
    encoding: str = "utf8",
) -> AsyncIterator[SQLAlchemyURL]:

    tmp_db_name = f"{uuid.uuid4().hex}_test{f'_{suffix}' if suffix else ''}"

    tmp_db_url = SQLAlchemyURL.create(
        username=settings.db.USER,
        password=settings.db.PASSWORD,
        host=settings.db.HOST,
        port=settings.db.PORT,
        database=tmp_db_name,
        drivername=settings.db.DRIVER,
    )

    engine = create_async_engine(settings.db.url, isolation_level="AUTOCOMMIT")

    try:
        await create_postgres_db(engine, tmp_db_name, encoding)
        yield tmp_db_url
    finally:
        await drop_postgres_db(engine, tmp_db_name)
        await engine.dispose()


# upgrade and downgrade serving as lambda-esque approach to run
# alembic migrations programmatically with async
# ripped from: https://github.com/sqlalchemy/alembic/discussions/991
def run_upgrade(connection, cfg):
    cfg.attributes["connection"] = connection
    command.upgrade(cfg, "head")


def run_downgrade(connection, cfg):
    cfg.attributes["connection"] = connection
    command.downgrade(cfg, "base")


@pytest.fixture(scope="session")
async def sessionmanager_for_tests(postgres):
    alembic_config = Config("alembic.ini")
    alembic_config.set_main_option(
        "sqlalchemy.url", postgres.render_as_string(hide_password=False)
    )

    db_manager.init(db_url=postgres)
    async with db_manager.connect() as conn:
        await conn.run_sync(run_upgrade, alembic_config)

    yield db_manager

    async with db_manager.connect() as conn:
        await conn.run_sync(run_downgrade, alembic_config)
    await db_manager.close()


@pytest.fixture()
async def session(sessionmanager_for_tests):
    async with sessionmanager_for_tests.session() as session:
        yield session

    await session.rollback()
