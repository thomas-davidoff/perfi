import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from app.models import PerfiModel

from config.settings import settings
import logging


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

current_url = config.get_main_option("sqlalchemy.url", None)
if not current_url:
    config.set_main_option(
        "sqlalchemy.url", settings.db.url.render_as_string(hide_password=False)
    )

# Check if alembic already has configured handlers
# if it does, then alembic was likely already handled by the app
# alembic's default logging behavior is to disable existing loggers which
# works well when running from the CLI.
# However, since Alembic is sometimes invoked programmatically in tests and the like,
# we don't always want that behavior.
# Thus... fucking long comment... the below lines check if config references a file,
# alembic handlers is 1 (NullHandler) and that the actual handler in the list is indeed
# a NullHandler. It's ugly as hell and will absolutely fail if I actually choose to configure
# Alembic with a NullHandler. Not sure why I'd do that.
alembic_handlers = logging.getLogger("alembic").handlers
if (
    config.config_file_name is not None
    and len(alembic_handlers) == 1
    and isinstance(alembic_handlers[0], logging.NullHandler)
):
    fileConfig(config.config_file_name)

target_metadata = PerfiModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    connectable = config.attributes.get("connection", None)

    if connectable is None:
        asyncio.run(run_async_migrations())
    else:
        do_run_migrations(connectable)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
