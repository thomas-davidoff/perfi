from alembic import command
import contextlib
import uuid
from typing import AsyncIterator
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.engine.url import URL as SQLAlchemyURL
from config.settings import settings


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
